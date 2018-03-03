
import time
import abc
import zipfile
import traceback
import os.path
import hashlib
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import magic

import WebRequest

import settings
import runStatus
import nameTools as nt

import MangaCMS.ScrapePlugins.MangaScraperDbBase
import MangaCMS.ScrapePlugins.ScrapeExceptions as ScrapeExceptions

def hash_file(filepath):

	with open(filepath, "rb") as f:
		hash_md5 = hashlib.md5()
		hash_md5.update(f.read())
		fhash = hash_md5.hexdigest()
	return fhash

class RetreivalBase(MangaCMS.ScrapePlugins.MangaScraperDbBase.MangaScraperDbBase):

	# Abstract class (must be subclassed)
	__metaclass__ = abc.ABCMeta

	plugin_type = "ContentRetreiver"

	itemLimit = 250
	retreival_threads = 1

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.wg = WebRequest.WebGetRobust(logPath=self.logger_path+".Web")
		self.die = False

	@abc.abstractmethod
	def get_link(self, link_row_id):
		pass

	# Provision for a delay. If checkDelay returns false, item is not enqueued
	def checkDelay(self, _):
		return True

	# And for logging in (if needed)
	def setup(self):
		pass

	def _retreiveTodoLinksFromDB(self):

		# self.QUERY_DEBUG = True

		self.log.info( "Fetching items from db...",)

		with self.db.session_context() as sess:

			res = sess.query(self.target_table)                            \
				.filter(self.target_table.source_site == self.plugin_key)  \
				.filter(self.target_table.state == 'new')                  \
				.order_by(self.target_table.id.desc())                     \
				.all()

			res = [(tmp.id, tmp.posted_at) for tmp in res]

		self.log.info( "Done")

		items = []
		for item_row_id, posted_at in res:
			if self.checkDelay(posted_at):
				items.append((item_row_id, posted_at))

		self.log.info( "Have %s new items to retreive in %s Downloader", len(items), self.plugin_key.title())


		items = sorted(items, key=lambda k: k[1], reverse=True)
		if self.itemLimit:
			items = items[:self.itemLimit]

		items = [tmp[0] for tmp in items]

		return items


	def _fetch_link(self, link_row_id):
		try:
			if link_row_id is None:
				self.log.error("Worker received null task! Wat?")
				return
			if self.die:
				self.log.warning("Skipping job due to die flag!")
				return
			if not runStatus.run:
				self.log.info( "Breaking due to exit flag being set")
				return

			status = self.get_link(link_row_id=link_row_id)

			ret1 = None
			if status == 'phash-duplicate':
				ret1 = self.mon_con.incr('phash_dup_items', 1)
			elif status == 'binary-duplicate':
				ret1 = self.mon_con.incr('bin_dup_items', 1)

			# We /always/ send the "fetched_items" count entry.
			# However, the deduped result is only send if the item is actually deduped.
			ret2 = self.mon_con.incr('fetched_items', 1)
			self.log.info("Retreival complete. Sending log results:")
			if ret1:
				self.log.info("	-> %s", ret1)
			self.log.info("	-> %s", ret2)

		except SystemExit:
			self.die = True
			raise

		except ScrapeExceptions.LimitedException as e:
			self.log.info("Remote site is rate limiting. Exiting early.")
			self.die = True
			raise e

		except KeyboardInterrupt:
			self.log.critical("Keyboard Interrupt!")
			self.log.critical(traceback.format_exc())

			# Reset the download, since failing because a keyboard interrupt is not a remote issue.
			with self.row_context(dbid=link_row_id) as row:
				row.state = 'new'
			raise

		except Exception:
			ret = self.mon_con.incr('failed_items', 1)
			self.log.critical("Sending log result: %s", ret)

			self.log.critical("Exception!")
			traceback.print_exc()
			self.log.critical(traceback.format_exc())



	def processTodoLinks(self, links):
		if links:

			with ThreadPoolExecutor(max_workers=self.retreival_threads) as executor:

				futures = [executor.submit(self._fetch_link, link) for link in links]

				while futures:
					futures = [tmp for tmp in futures if not (tmp.done() or tmp.cancelled())]
					if not runStatus.run:
						self.log.warning("Cancelling all pending futures")
						for job in futures:
							job.cancel()
						self.log.warning("Jobs cancelled. Exiting executor context.")
						return
					time.sleep(1)





	# ---------------------------------------------------------------------------------------------------------------------------------------------------------
	# Filesystem stuff
	# ---------------------------------------------------------------------------------------------------------------------------------------------------------


	# either locate or create a directory for `seriesName`.
	# If the directory cannot be found, one will be created.
	# Returns {pathToDirectory string}, {HadToCreateDirectory bool}
	def locateOrCreateDirectoryForSeries(self, seriesName):

		if self.shouldCanonize:
			canonSeriesName = nt.getCanonicalMangaUpdatesName(seriesName)
		else:
			canonSeriesName = seriesName

		safeBaseName = nt.makeFilenameSafe(canonSeriesName)


		if canonSeriesName in nt.dirNameProxy:
			self.log.info("Have target dir for '%s' Dir = '%s'", canonSeriesName, nt.dirNameProxy[canonSeriesName]['fqPath'])
			return nt.dirNameProxy[canonSeriesName]["fqPath"], False
		else:
			self.log.info("Don't have target dir for: %s, full name = %s", canonSeriesName, seriesName)
			targetDir = os.path.join(settings.baseDir, safeBaseName)
			if not os.path.exists(targetDir):
				try:
					os.makedirs(targetDir)
					return targetDir, True

				except FileExistsError:
					# Probably means the directory was concurrently created by another thread in the background?
					self.log.critical("Directory doesn't exist, and yet it does?")
					self.log.critical(traceback.format_exc())
				except OSError:
					self.log.critical("Directory creation failed?")
					self.log.critical(traceback.format_exc())

			else:
				self.log.warning("Directory not found in dir-dict, but it exists!")
				self.log.warning("Directory-Path: %s", targetDir)
				self.log.warning("Base series name: %s", seriesName)
				self.log.warning("Canonized series name: %s", canonSeriesName)
				self.log.warning("Safe canonized name: %s", safeBaseName)
			return targetDir, False

	def _get_existing_file_by_hash(self, sess, file_hash):
		have_row = sess.query(self.db.ReleaseFile)          \
			.filter(self.db.ReleaseFile.fhash == file_hash) \
			.scalar()
		return have_row

	def save_archive(self, row, sess, fqfilename, file_content):
		filepath, fileN = os.path.split(fqfilename)
		fileN = fileN.replace('.zip .zip', '.zip')
		fileN = fileN.replace('.zip.zip', '.zip')
		fileN = fileN.replace(' .zip', '.zip')
		fileN = fileN.replace('..zip', '.zip')
		fileN = fileN.replace('.rar .rar', '.rar')
		fileN = fileN.replace('.rar.rar', '.rar')
		fileN = fileN.replace(' .rar', '.rar')
		fileN = fileN.replace('..rar', '.rar')
		fileN = nt.makeFilenameSafe(fileN)

		fqfilename = os.path.join(filepath, fileN)
		fqfilename = self.insertCountIfFilenameExists(fqfilename)
		self.log.info("Complete filepath: %s", fqfilename)

		chop = len(fileN)-4

		while 1:
			try:
				with open(fqfilename, "wb") as fp:
					fp.write(file_content)

				# Round-trip via the filesystem because why not
				fhash = hash_file(fqfilename)

				have = self._get_existing_file_by_hash(sess, fhash)

				dirpath, filename = os.path.split(fqfilename)
				if have:
					have_fqp = os.path.join(have.dirpath, have.filename)
					if have_fqp == fqfilename:
						self.log.error("Multiple instances of a releasefile created on same on-disk file!")
						self.log.error("File: %s. Row id: %s", have_fqp, row.id)
						raise RuntimeError
					if os.path.exists(have_fqp):

						with open(have_fqp, "rb") as fp1:
							fc1 = fp1.read()
						with open(fqfilename, "rb") as fp2:
							fc2 = fp2.read()

						if fc1 != fc2:
							self.log.error("Multiple instances of a releasefile with the same md5, but different contents?")
							self.log.error("Files: %s, %s. Row id: %s", have_fqp, fqfilename, row.id)
							raise RuntimeError

						self.log.warning("Duplicate file found by md5sum search. Re-using existing file.")
						self.log.warning("Files: '%s', '%s'.", have_fqp, fqfilename)
						os.unlink(fqfilename)

						row.fileid = have.id
						return have_fqp
					else:
						self.log.warning("Duplicate file found by md5sum search, but existing file has been deleted.")
						self.log.warning("Files: '%s', '%s'.", have_fqp, fqfilename)

						have.dirpath = dirpath
						have.filename = filename

						row.fileid = have.id

						return fqfilename

				else:

					new_row = self.db.ReleaseFile(
							dirpath  = dirpath,
							filename = filename,
							fhash    = fhash
						)

					sess.add(new_row)
					sess.flush()

					row.fileid = new_row.id

				return fqfilename

			except (IOError, OSError):
				chop = chop - 1
				filepath, fileN = os.path.split(fqfilename)

				fileN = fileN[:chop]+fileN[-4:]
				self.log.warn("Truncating file length to %s characters and re-encoding.", chop)
				fileN = fileN.encode('utf-8','ignore').decode('utf-8')
				fileN = nt.makeFilenameSafe(fileN)
				fqfilename = os.path.join(filepath, fileN)
				fqfilename = self.insertCountIfFilenameExists(fqfilename)




	def save_image_set(self, row, sess, fqfilename, image_list):

		filepath, fileN = os.path.split(fqfilename)
		fileN = fileN.replace('.zip .zip', '.zip')
		fileN = fileN.replace('.zip.zip', '.zip')
		fileN = fileN.replace(' .zip', '.zip')
		fileN = fileN.replace('..zip', '.zip')
		fileN = nt.makeFilenameSafe(fileN)

		fqfilename = os.path.join(filepath, fileN)
		fqfilename = self.insertCountIfFilenameExists(fqfilename)
		self.log.info("Complete filepath: %s", fqfilename)

		assert len(image_list) >= 1
		chop = len(fileN)-4

		while 1:
			try:
				arch = zipfile.ZipFile(fqfilename, "w")

				#Write all downloaded files to the archive.
				for imageName, imageContent in image_list:
					assert isinstance(imageName, str)
					assert isinstance(imageContent, bytes)

					mtype = magic.from_buffer(imageContent, mime=True)
					assert "image" in mtype.lower()

					_, ext = os.path.splitext(imageName)
					if not ext:
						self.log.warning("Missing extension in archive file: %s", imageName)
						fext = mimetypes.guess_extension(mtype)
						self.log.warning("Appending guessed file-extension %s", fext)
						imageName += fext

					arch.writestr(imageName, imageContent)
				arch.close()


				fhash = hash_file(fqfilename)

				dirpath, filename = os.path.split(fqfilename)
				new_row = self.db.ReleaseFile(
						dirpath  = dirpath,
						filename = filename,
						fhash    = fhash
					)

				sess.add(new_row)
				sess.flush()

				row.fileid = new_row.id

				return fqfilename

			except (IOError, OSError):
				chop = chop - 1
				filepath, fileN = os.path.split(fqfilename)

				fileN = fileN[:chop]+fileN[-4:]
				self.log.warn("Truncating file length to %s characters and re-encoding.", chop)
				fileN = fileN.encode('utf-8','ignore').decode('utf-8')
				fileN = nt.makeFilenameSafe(fileN)
				fqfilename = os.path.join(filepath, fileN)
				fqfilename = self.insertCountIfFilenameExists(fqfilename)




	def insertCountIfFilenameExists(self, fqFName):

		base, ext = os.path.splitext(fqFName)
		loop = 1
		while os.path.exists(fqFName):
			fqFName = "%s - (%d).%s" % (base, loop, ext)
			loop += 1

		return fqFName

	def do_fetch_content(self):
		if hasattr(self, 'setup'):
			self.setup()

		todo = self._retreiveTodoLinksFromDB()
		if not runStatus.run:
			return

		if not todo:

			ret = self.mon_con.incr('fetched_items.count', 0)
			self.log.info("No links to fetch. Sending null result: %s", ret)

		if todo:
			self.processTodoLinks(todo)
		self.log.info("ContentRetreiver for %s has finished.", self.pluginName)

	def go(self):
		raise ValueError("use do_fetch_content() instead!")
