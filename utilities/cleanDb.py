# import sys
# sys.path.insert(0,"..")
import os
import os.path
import sys
import tqdm
import gzip
import json
import datetime
import time

import MangaCMS.lib.logSetup
if __name__ == "__main__":
	MangaCMS.lib.logSetup.initLogging()


import runStatus
runStatus.preloadDicts = False

import traceback
import re
import nameTools as nt
import shutil
import settings
import hashlib

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

import MangaCMS.cleaner.processDownload
import MangaCMS.ScrapePlugins.MangaScraperBase


class CleanerBase(MangaCMS.ScrapePlugins.MangaScraperBase.MangaScraperBase):

	# QUERY_DEBUG = True

	def __init__(self, tableKey=None):
		self.tableKey = tableKey
		super().__init__()


	def __delete(self, cur, dbid, wanted):

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

		fqpath = os.path.join(downloadPath, fileName)

		if not os.path.exists(fqpath):
			print("Deleting row for missing item")
			cur.execute("""DELETE FROM {tableName} WHERE dbid = %s""".format(tableName=self.tableName), (dbid, ))


		cur.execute("""
			SELECT
				dbId, tags
			FROM
				{tableName}
			WHERE
				downloadPath = %s
			AND
				fileName = %s

				""".format(tableName=self.tableName), (downloadPath, fileName))

		matches = cur.fetchall()

		ids = [(tmp[0], ) for tmp in matches]

		tagagg = [tmp[1] for tmp in matches if tmp[1]]
		tagagg = " ".join([tmp if tmp else "" for tmp in tagagg])
		lcSet = set(tagagg.lower().split(" "))

		keep_tags = [tag for tag in lcSet if any([item in tag for item in wanted])]


		if "language-english" in tagagg:
			return

		if ids == [(dbId, )] and dbId == dbid:
			print("row", os.path.exists(fqpath), downloadPath, fileName)
			print("Tags", tags)

			if os.path.exists(fqpath):
				os.remove(fqpath)

			cur.execute("""DELETE FROM {tableName} WHERE dbid = %s""".format(tableName=self.tableName), (dbid, ))
		elif not keep_tags:
			print("Have multiple rows for item!")
			print(keep_tags)
			print(fqpath)
			print(matches)

			for item_id in ids:
				cur.execute("""DELETE FROM {tableName} WHERE dbid = %s""".format(tableName=self.tableName), (item_id, ))

			if os.path.exists(fqpath):
				os.remove(fqpath)

		else:
			print("Keeeping")
			print(keep_tags)
			print(fqpath)

	def cleanJapaneseOnly(self):
		print("cleanJapaneseOnly")

		bad_tags = [r'%language-japanese%', r'%language-日本語%', r'%language-chinese%',]

		wanted = [tmp.lower() for tmp in settings.tags_keep]



		for bad in bad_tags:

			with self.transaction() as cur:
				print("Searching for tag %s" % bad)
				cur.execute("""SELECT dbId, tags FROM {tableName} WHERE tags LIKE %s""".format(tableName=self.tableName), (bad, ))
				items = cur.fetchall()
				print("Processing %s results", len(items))

				for dbId, tags in items:

					lcSet = set(tags.lower().split(" "))

					# if any([tmp in lcSet for tmp in settings.deleted_indicators]):
					# 	continue

					match = [tag for tag in lcSet if any([item in tag for item in wanted])]
					if not match:
						self.__delete(cur, dbId, wanted)

				print(len(items))


	def cleanYaoiOnly(self):
		print("cleanYaoiOnly")

		bad_tags = [
			'yaoi',
			'male-yaoi',
			'guys-only',
			'males-only',
			'male-males-only',
			'male-guys-only',
			'trap-yaoi',
		]

		releases = set()
		with self.db.session_context() as sess:
			bad = sess.query(self.db.HentaiTags) \
				.filter(or_(
						*(self.db.HentaiTags.tag.like(tag) for tag in bad_tags)
					)).all()


			self.log.info("Found %s tags to process", len(bad))

			for row in tqdm.tqdm(bad):
				for release in tqdm.tqdm(row.hentai_releases.all()):
					if release.id not in releases:
						releases.add(release.id)

		self.log.info("")
		self.log.info("Found %s items to examine", len(releases))

		releases = list(releases)
		releases.sort(reverse=True)

		for relid in tqdm.tqdm(releases):
			with self.row_sess_context(dbid=relid, limit_by_plugin=False) as (row, sess):

				if not row:
					continue
				if row.last_checked < datetime.datetime.now() - datetime.timedelta(days=7):
					continue



				ftags = set(row.file.hentai_tags)
				atags = set() | ftags
				for a_row in row.file.hentai_releases:
					for tag in a_row.tags:
						atags.add(tag)


				if not self.wanted_from_tags(atags):
					self.log.info("Deleting %s series release rows with tags: %s", len(row.file.hentai_releases), atags)
					for bad_rel in row.file.hentai_releases:
						sess.delete(bad_rel)
					sess.delete(row.file)

					fqp = os.path.join(row.file.dirpath, row.file.filename)
					self.log.info("Deleting file: '%s'", fqp)
					os.unlink(fqp)

	def syncHFileTags(self):
		with self.db.session_context() as sess:
			file_rows = sess.query(self.db.ReleaseFile.id).all()

		file_rows.sort(reverse=True)

		for relid, in tqdm.tqdm(file_rows):

			with self.db.session_context(commit=True) as sess:
				row_q = sess.query(self.db.ReleaseFile)     \
					.options(joinedload("hentai_releases")) \
					.filter(self.db.ReleaseFile.id == relid)

				row = row_q.one()


				atags = set()
				for a_row in row.hentai_releases:
					for tag in a_row.tags:
						atags.add(tag)

				missing = set()
				for tag in atags:
					if tag not in row.hentai_tags:
						row.hentai_tags.add(tag)
						missing.add(tag)

				if missing:
					self.log.info("Missing tags from row %s -> %s", row.id, missing)



	# # STFU, abstract base class
	def go(self):
		pass

class MCleaner(CleanerBase):
	logger_path = "Main.Mc"
	tableName  = "MangaItems"
	is_manga   = True
	plugin_name = "None"
	plugin_key   = "None"
	plugin_type = 'Utility'


class HCleaner(CleanerBase):
	logger_path = "Main.Hc"
	is_manga   = False
	plugin_name = "None"
	plugin_key   = "None"
	plugin_type = 'Utility'


if __name__ == "__main__":
	import MangaCMS.lib.logSetup
	MangaCMS.lib.logSetup.initLogging()