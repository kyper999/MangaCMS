# import sys
# sys.path.insert(0,"..")
import os
import os.path
import sys

import logSetup
if __name__ == "__main__":
	logSetup.initLogging()


import runStatus
runStatus.preloadDicts = False

import traceback
import re
import DbBase
import ScrapePlugins.MangaScraperDbBase
import nameTools as nt
import shutil
import settings
import hashlib


import utilities.EmptyRetreivalDb
import processDownload


class PathCleaner(DbBase.DbBase):
	loggerPath = "Main.Pc"
	tableName  = "MangaItems"
	pluginName = "PathCleanerUtil"

	def moveFile(self, srcPath, dstPath):
		dlPath, fName = os.path.split(srcPath)
		# print("dlPath, fName", dlPath, fName)
		with self.transaction() as cur:

			cur.execute("SELECT dbId FROM {tableName} WHERE downloadPath=%s AND fileName=%s".format(tableName=self.tableName), (dlPath, fName))
			ret = cur.fetchall()

			if not ret:
				cur.execute("COMMIT;")
				return
			dbId = ret.pop()

			cur.execute("UPDATE {tableName} SET downloadPath=%s, fileName=%s WHERE dbId=%s".format(tableName=self.tableName), (dlPath, fName, dbId))
		self.log.info("Moved file in local DB.")

	def updatePath(self, dbId, dlPath, cur):

		cur.execute("UPDATE {tableName} SET downloadPath=%s WHERE dbId=%s".format(tableName=self.tableName), (dlPath, dbId))
		self.log.info("Moved file in local DB.")

	def findIfMigrated(self, filePath):
		dirPath, fileName = os.path.split(filePath)

		series = dirPath.split("/")[-1]
		series = nt.getCanonicalMangaUpdatesName(series)
		otherDir = nt.dirNameProxy[series]

		if not otherDir["fqPath"]:
			return False
		if otherDir["fqPath"] == dirPath:
			return False

		newPath = os.path.join(otherDir["fqPath"], fileName)
		if os.path.exists(newPath):
			print("File moved!")
			return otherDir["fqPath"]

		return False

	def resetDlState(self, dbId, newState, cur):
		cur.execute("UPDATE {tableName}  SET dlState=%s WHERE dbId=%s".format(tableName=self.tableName), (newState, dbId))

	def resetMissingDownloads(self):


		if not nt.dirNameProxy.observersActive():
			nt.dirNameProxy.startDirObservers()




		with self.transaction() as cur:
			cur.execute("SELECT dbId, sourceSite, downloadPath, fileName, tags FROM {tableName} WHERE dlState=%s ORDER BY retreivalTime DESC;".format(tableName=self.tableName), (2, ))
			ret = cur.fetchall()

		print("Ret", len(ret))

		with self.transaction() as cur:
			loops = 0
			for dbId, sourceSite, downloadPath, fileName, tags in ret:
				filePath = os.path.join(downloadPath, fileName)
				if tags == None:
					tags = ""

				if not os.path.exists(filePath):
					migPath = self.findIfMigrated(filePath)
					if not migPath:
						print("Resetting download for ", filePath, "source=", sourceSite)
						self.resetDlState(dbId, 0, cur)

					else:
						print("Moved!")
						print("		Old = '%s'" % filePath)
						print("		New = '%s'" % migPath)
						self.updatePath(dbId, migPath, cur)

				loops += 1
				if loops % 1000 == 0:
					cur.execute("COMMIT;")
					print("Incremental Commit!")
					cur.execute("BEGIN;")


	def updateTags(self, dbId, newTags):
		cur = self.get_cursor()
		cur.execute("UPDATE {tableName} SET tags=%s WHERE dbId=%s;".format(tableName=self.tableName), (newTags, dbId))

	def clearInvalidDedupTags(self):

		cur = self.get_cursor()
		cur.execute("BEGIN;")
		print("Querying")
		cur.execute("SELECT dbId, downloadPath, fileName, tags FROM {tableName}".format(tableName=self.tableName))
		print("Queried. Fetching results")
		ret = cur.fetchall()
		cur.execute("COMMIT;")
		print("Have results. Processing")

		cur.execute("BEGIN;")
		for  dbId, downloadPath, fileName, tags in ret:
			if tags == None: tags = ""
			if "deleted" in tags and "was-duplicate" in tags:
				fPath = os.path.join(downloadPath, fileName)
				if os.path.exists(fPath):
					tags = set(tags.split(" "))
					tags.remove("deleted")
					tags.remove("was-duplicate")
					tags = " ".join(tags)
					print("File ", fPath, "exists!", dbId, )
					self.updateTags(dbId, tags)

		cur.execute("COMMIT;")



	def patchBatotoLinks(self):


		cur = self.get_cursor()
		cur.execute("BEGIN;")
		print("Querying")
		cur.execute("SELECT dbId, sourceUrl FROM {tableName} WHERE sourceSite='bt';".format(tableName=self.tableName))
		print("Queried. Fetching results")
		ret = cur.fetchall()
		cur.execute("COMMIT;")
		print("Have results. Processing")

		cur.execute("BEGIN;")
		for  dbId, sourceUrl in ret:
			if "batoto" in sourceUrl.lower():
				sourceUrl = sourceUrl.replace("http://www.batoto.net/", "http://bato.to/")
				print("Link", sourceUrl)

				cur.execute("SELECT dbId FROM {tableName} WHERE sourceUrl=%s;".format(tableName=self.tableName), (sourceUrl, ))
				ret = cur.fetchall()
				if not ret:
					print("Updating")
					cur.execute("UPDATE {tableName} SET sourceUrl=%s WHERE dbId=%s;".format(tableName=self.tableName), (sourceUrl, dbId))

				else:
					print("Replacing")
					cur.execute("DELETE FROM {tableName} WHERE sourceUrl=%s;".format(tableName=self.tableName), (sourceUrl, ))
					cur.execute("UPDATE {tableName} SET sourceUrl=%s WHERE dbId=%s;".format(tableName=self.tableName), (sourceUrl, dbId))


		cur.execute("COMMIT;")




	def insertNames(self, buId, names):

		with self.get_cursor() as cur:
			for name in names:
				fsSafeName = nt.prepFilenameForMatching(name)
				cur.execute("""SELECT COUNT(*) FROM munamelist WHERE buId=%s AND name=%s;""", (buId, name))
				ret = cur.fetchone()
				if not ret[0]:
					cur.execute("""INSERT INTO munamelist (buId, name, fsSafeName) VALUES (%s, %s, %s);""", (buId, name, fsSafeName))
				else:
					print("wat", ret[0], bool(ret[0]))

	def crossSyncNames(self):

		cur = self.get_cursor()
		cur.execute("BEGIN;")
		print("Querying")
		cur.execute("SELECT DISTINCT ON (buname) buname, buId FROM mangaseries ORDER BY buname, buid;")
		print("Queried. Fetching results")
		ret = cur.fetchall()
		cur.execute("COMMIT;")
		print("Have results. Processing")

		cur.execute("BEGIN;")

		missing = 0
		for item in ret:
			buName, buId = item
			if not buName:
				continue

			cur.execute("SELECT * FROM munamelist WHERE name=%s;", (buName, ))
			ret = cur.fetchall()
			# mId = nt.getMangaUpdatesId(buName)

			if not ret:
				print("Item missing '{item}', mid:{mid}".format(item=item, mid=ret))
				self.insertNames(buId, [buName])
				missing += 1

			if not runStatus.run:
				break
				# print("Item '{old}', '{new}', mid:{mid}".format(old=item, new=nt.getCanonicalMangaUpdatesName(item), mid=mId))
		print("Total: ", len(ret))
		print("Missing: ", missing)


	def consolidateSeriesNaming(self):


		cur = self.get_cursor()
		# cur.execute("BEGIN;")
		# print("Querying")
		# cur.execute("SELECT DISTINCT(seriesName) FROM {tableName};".format(tableName=self.tableName))
		# print("Queried. Fetching results")
		# ret = cur.fetchall()
		# cur.execute("COMMIT;")
		# print("Have results. Processing")

		# for item in ret:
		# 	item = item[0]
		# 	if not item:
		# 		continue

		# 	mId = nt.getMangaUpdatesId(item)
		# 	if not mId:
		# 		print("Item '{old}', '{new}', mid:{mid}".format(old=item, new=nt.getCanonicalMangaUpdatesName(item), mid=mId))
		# print("Total: ", len(ret))

		items = ["Murciélago", "Murcielago", "Murciélago"]

		for item in items:
			print("------", item, nt.getCanonicalMangaUpdatesName(item), nt.haveCanonicalMangaUpdatesName(item))

		# cur.execute("BEGIN;")
		# print("Querying")
		# cur.execute("SELECT DISTINCT ON (buname) buname, buId FROM mangaseries ORDER BY buname, buid;")
		# print("Queried. Fetching results")
		# ret = cur.fetchall()
		# cur.execute("COMMIT;")
		# print("Have results. Processing")

		# cur.execute("BEGIN;")

		# missing = 0
		# for item in ret:
		# 	buName, buId = item
		# 	if not buName:
		# 		continue

		# 	cur.execute("SELECT * FROM munamelist WHERE name=%s;", (buName, ))
		# 	ret = cur.fetchall()
		# 	# mId = nt.getMangaUpdatesId(buName)

		# 	if not ret:
		# 		print("Item missing '{item}', mid:{mid}".format(item=item, mid=ret))
		# 		self.insertNames(buId, [buName])
		# 		missing += 1

		# 	if not runStatus.run:
		# 		break
		# 		# print("Item '{old}', '{new}', mid:{mid}".format(old=item, new=nt.getCanonicalMangaUpdatesName(item), mid=mId))
		# print("Total: ", len(ret))
		# print("Missing: ", missing)


		# for  dbId, sourceUrl in ret:
		# 	if "batoto" in sourceUrl.lower():
		# 		sourceUrl = sourceUrl.replace("http://www.batoto.net/", "http://bato.to/")
		# 		print("Link", sourceUrl)

		# 		cur.execute("SELECT dbId FROM {tableName} WHERE sourceUrl=%s;".format(tableName=self.tableName), (sourceUrl, ))
		# 		ret = cur.fetchall()
		# 		if not ret:
		# 			print("Updating")
		# 			cur.execute("UPDATE {tableName} SET sourceUrl=%s WHERE dbId=%s;".format(tableName=self.tableName), (sourceUrl, dbId))

		# 		else:
		# 			print("Replacing")
		# 			cur.execute("DELETE FROM {tableName} WHERE sourceUrl=%s;".format(tableName=self.tableName), (sourceUrl, ))
		# 			cur.execute("UPDATE {tableName} SET sourceUrl=%s WHERE dbId=%s;".format(tableName=self.tableName), (sourceUrl, dbId))


		cur.execute("COMMIT;")

	def renameDlPaths(self):
		nt.dirNameProxy.startDirObservers()
		cur = self.get_cursor()
		cur.execute("BEGIN ;")
		cur.execute("SELECT dbId, downloadPath, seriesName FROM mangaitems ORDER BY retreivalTime DESC;")
		rows = cur.fetchall()
		print("Processing %s items" % len(rows))
		cnt = 0
		for row in rows:
			dbId, filePath, seriesName = row
			if filePath == None:
				filePath = ''
			if seriesName == '' or seriesName == None:
				print("No series name", row)
				continue

			if not os.path.exists(filePath):
				if seriesName in nt.dirNameProxy:
					itemPath = nt.dirNameProxy[seriesName]['fqPath']
					if os.path.exists(itemPath):
						print("Need to change", filePath, itemPath)
						cur.execute("UPDATE mangaitems SET downloadPath=%s WHERE dbId=%s", (itemPath, dbId))

			cnt += 1
			if cnt % 1000 == 0:
				print("ON row ", cnt)
				cur.execute("COMMIT;")
				cur.execute("BEGIN;")

		cur.execute("COMMIT;")
		nt.dirNameProxy.stop()

	def regenerateNameMappings(self):
		cur = self.get_cursor()
		cur.execute("BEGIN ;")
		cur.execute("SELECT dbId, name, fsSafeName FROM munamelist;")
		rows = cur.fetchall()
		print("Processing %s items" % len(rows))
		cnt = 0
		for row in rows:
			dbId, name, fsSafeName = row

			prepped = nt.prepFilenameForMatching(name)
			if not prepped or (len(name) - len(prepped)) > 2:
				continue

			if prepped != fsSafeName:
				print("Bad match", row, prepped)
				cur.execute("UPDATE munamelist SET fsSafeName=%s WHERE dbId=%s", (prepped, dbId))
			cnt += 1
			if cnt % 1000 == 0:
				print("ON row ", cnt)

		cur.execute("COMMIT;")
		nt.dirNameProxy.stop()

	def extractTags(self, name):
		tagre = re.compile(r'{\(Tags\)(.+?)}')
		tagout = tagre.findall(name)
		tagout = set(" ".join(tagout).strip().split(" "))
		if "none" in tagout:
			tagout.remove("none")
		return tagout

	def fetchLinkList(self, itemList):

		dbInt = utilities.EmptyRetreivalDb.ScraperDbTool()

		try:
			for item in itemList:

				srcStr = 'import-{hash}'.format(hash=hashlib.md5(item.encode("utf-8")).hexdigest())
				itemtags = self.extractTags(item)
				if itemtags == "None" or itemtags == None:
					itemtags = ''
				fPath = os.path.join(settings.djMoeDir, "imported")

				if not os.path.exists(fPath):
					os.makedirs(fPath)

				srcPath = os.path.join(self.sourcePath, item)
				dstPath = os.path.join(fPath, item)

				if os.path.exists(dstPath):
					raise ValueError("Destination path already exists? = '%s'" % dstPath)



				# print("os.path.exists", os.path.exists(srcPath), os.path.exists(dstPath))

				# print("Item '%s' '%s' '%s'" % (srcPath, dstPath, itemtags))
				shutil.move(srcPath, dstPath)
				dbInt.insertIntoDb(retreivalTime=200,
									sourceUrl=srcStr,
									originName=item,
									dlState=2,
									downloadPath=fPath,
									fileName=item,
									seriesName="imported")




				dedupState = processDownload.processDownload("imported", dstPath, pron=True, deleteDups=True)


				tags = dedupState + ' ' + ' '.join(itemtags)
				tags = tags.strip()
				if dedupState:
					dbInt.addTags(sourceUrl=srcStr, tags=tags)

				self.log.info( "Done")

				if not runStatus.run:
					self.log.info( "Breaking due to exit flag being set")
					break

		except:
			self.log.critical("Exception!")
			traceback.print_exc()
			self.log.critical(traceback.format_exc())


	def processTodoItems(self, items):
		if items:

			self.fetchLinkList(items)





	def importDjMItems(self, sourcePath):

		# Horrible tweak the class definition before instantiating.
		utilities.EmptyRetreivalDb.ScraperDbTool.tableKey = "djm"
		self.sourcePath = sourcePath

		items = os.listdir(sourcePath)
		self.processTodoItems(items)

	def fixDjMItems(self):

		# Horrible tweak the class definition before instantiating.
		utilities.EmptyRetreivalDb.ScraperDbTool.tableKey = "djm"

		dbInt = utilities.EmptyRetreivalDb.ScraperDbTool()
		cur = dbInt.get_cursor()
		print("Cursor", cur)
		cur.execute("SELECT sourceUrl, fileName, tags FROM HentaiItems WHERE sourceSite='djm' AND retreivalTime=200;")
		rows = cur.fetchall()

		bad = 0
		for row in rows:
			sourceUrl, fileName, tags = row
			itemtags = self.extractTags(fileName)
			if itemtags == "None" or itemtags == None:
				itemtags = ''

			if tags != itemtags and itemtags:
				bad += 1
				print("Wat?", tags, itemtags)
				dbInt.addTags(sourceUrl=sourceUrl, tags=" ".join(itemtags))

		print("need to fix", bad, "of", len(rows))


	def btUrlFix(self):
		'''
		Fix batoto URLs from http -> https switch.
		'''
		print("Fixing Batoto URLs.")

		with self.transaction() as cur:
			print("Querying")
			cur.execute("""SELECT dbId, sourceurl FROM {tableName} WHERE sourcesite = %s AND sourceurl LIKE %s""".format(tableName=self.tableName), ('bt', "http://%"))
			items = cur.fetchall()
			print("Updating %s items" % len(items))
			updated = 0
			for dbid, srcurl in items:
				srcurl_fixed = srcurl.replace("http://", "https://")
				# print("{} -> {}".format(srcurl, srcurl_fixed))
				cur.execute("""UPDATE {tableName} SET sourceurl = %s WHERE dbid=%s""".format(tableName=self.tableName), (srcurl_fixed, dbid))
				updated += 1

				sys.stdout.write('|')
				sys.stdout.flush()

				if updated % 1000 == 0:
					print("Updating - %s" % updated)
					cur.execute("commit;")
					print("Committed")


			cur.execute("commit;")
			print(len(items))
			print(items[:5])

class HCleaner(ScrapePlugins.MangaScraperDbBase.MangaScraperDbBase):
	loggerPath = "Main.Pc"
	tableName  = "HentaiItems"
	pluginName = "None"
	tableKey   = "None"

	# QUERY_DEBUG = True

	def __init__(self, tableKey=None):
		self.tableKey = tableKey
		super().__init__()

	def resetMissingDownloads(self):



		with self.transaction() as cur:
			cur.execute("SELECT dbId, sourceSite, downloadPath, fileName, tags FROM {tableName} WHERE dlState=%s ORDER BY retreivalTime DESC;".format(tableName=self.tableName), (2, ))
			ret = cur.fetchall()

		print("Ret", len(ret))

		match = []
		loops = 0
		for dbId, sourceSite, downloadPath, fileName, tags in ret:


			filePath = os.path.join(downloadPath, fileName)
			if os.path.exists(filePath):
				self.log.info("File exists: %s", filePath)
			else:
				self.log.info("Item missing: %s", filePath)
				self.updateDbEntryById(rowId=dbId, dlState=0, commit=False)

				removeTags = ["deleted", "was-duplicate", "phash-duplicate", "dup-checked"]
				tagList = tags.split(" ")

				self.log.info("Processing '%s', '%s'", downloadPath, fileName)
				for tag in tagList:
					if "crosslink" in tag:
						removeTags.append(tag)
				if not "crosslink" in " ".join(removeTags):
					print("Wat?", sourceSite, downloadPath, fileName)

				rows = self.getRowsByValue(limitByKey=False, filename=fileName, downloadpath=downloadPath)

				for row in rows:
					self.removeTags(dbId=row['dbId'], limitByKey=False, tags=" ".join(removeTags), commit=False)


				loops += 1
				if loops % 1000 == 0:

					with self.transaction() as cur:
							cur.execute("COMMIT;")
							print("Incremental Commit!")
							cur.execute("BEGIN;")

				match.append(downloadPath)

		with self.transaction() as cur:
				cur.execute("COMMIT;")
				print("Incremental Commit!")
				cur.execute("BEGIN;")


	def cleanTags(self):
		'''
		So I've accidentally been introducing duplicate tags into the h-tag database. Not totally sure where
		(I added some protective {str}.lower() calls in a few places to see if it helps), but it's annoying.
		Anyways, this extracts all the tags, consolidates and lower-cases them, and then reinserts the
		fixed values.
		'''
		print("Fixing tags with case issues.")

		with self.transaction() as cur:
			cur.execute("""SELECT dbId, tags FROM {tableName} WHERE tags IS NOT NULL and tags != %s""".format(tableName=self.tableName), ('', ))
			items = cur.fetchall()

			for dbId, tags in items:
				lcSet = set(tags.lower().split(" "))
				if lcSet != set(tags.split(" ")):
					fTags = " ".join(lcSet)
					cur.execute("UPDATE {tableName} SET tags=%s WHERE dbid=%s".format(tableName=self.tableName), (fTags, dbId))
					print(dbId, tags, set(tags.split(" ")))
			print(len(items))

	def __delete(self, cur, dbid):

		cur.execute("""
			SELECT
				dbId, sourceSite, dlState, sourceUrl, retreivalTime, lastUpdate, sourceId, seriesName, fileName, originName, downloadPath, flags, tags, note
			FROM
				{tableName}
			WHERE dbid = %s""".format(tableName=self.tableName), (dbid, ))
		have = cur.fetchone()
		if not have:
			return

		dbId, sourceSite, dlState, sourceUrl, retreivalTime, lastUpdate, sourceId, seriesName, fileName, originName, downloadPath, flags, tags, note = have


		cur.execute("""
			SELECT
				dbId
			FROM
				{tableName}
			WHERE
				downloadPath = %s
			AND
				fileName = %s

				""".format(tableName=self.tableName), (downloadPath, fileName))

		ids = cur.fetchall()

		fqpath = os.path.join(downloadPath, fileName)

		if 'ASMHentai' not in downloadPath:
			return

		if ids == [(dbId, )] and dbId == dbid:
			print("row", os.path.exists(fqpath), downloadPath, fileName)
			print("Tags", tags)

			os.remove(fqpath)

			cur.execute("""DELETE FROM {tableName} WHERE dbid = %s""".format(tableName=self.tableName), (dbid, ))

	def cleanJapaneseOnly(self):
		'''
		So I've accidentally been introducing duplicate tags into the h-tag database. Not totally sure where
		(I added some protective {str}.lower() calls in a few places to see if it helps), but it's annoying.
		Anyways, this extracts all the tags, consolidates and lower-cases them, and then reinserts the
		fixed values.
		'''
		print("cleanJapaneseOnly")

		bad_tags = [r'%language-japanese%', r'%language-日本語%']

		wanted = [tmp.lower() for tmp in settings.tags_keep]

		for bad in bad_tags:

			with self.transaction() as cur:
				print("Searching for tag %s" % bad)
				cur.execute("""SELECT dbId, tags FROM {tableName} WHERE tags LIKE %s""".format(tableName=self.tableName), (bad, ))
				items = cur.fetchall()
				print("Processing %s results", len(items))

				for dbId, tags in items:

					lcSet = set(tags.lower().split(" "))

					if any([tmp in lcSet for tmp in settings.deleted_indicators]):
						continue

					match = [tag for tag in lcSet if any([item in tag for item in wanted])]
					if not match:
						self.__delete(cur, dbId)

				print(len(items))



	# # STFU, abstract base class
	def go(self):
		pass

if __name__ == "__main__":
	import logSetup
	logSetup.initLogging()