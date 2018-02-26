
if __name__ == "__main__":
	import runStatus
	runStatus.preloadDicts = False

import logging
import psycopg2
import functools
import operator as opclass
import abc

import threading
import settings
import os
import traceback
import WebRequest

import nameTools as nt
import MangaCMS.DbBase

import sql
import time
import sql.operators as sqlo

import MangaCMS.ScrapePlugins.MangaScraperDbBase


class LoaderBase(MangaCMS.ScrapePlugins.MangaScraperDbBase.MangaScraperDbBase):


	pluginType = "Loader"

	def __init__(self, *args, **kwargs):
		self.wg = WebRequest.WebGetRobust(logPath=self.loggerPath+".Web")

		super().__init__(*args, **kwargs)


	def setup(self):
		pass

	def __check_keys(self, check_dict):
		keys = set(check_dict.keys())
		allowed = set(
				'state',
				'err_str',
				'source_site',
				'source_id',
				'posted_at',
				'downloaded_at',
				'last_checked',
				'deleted',
				'was_duplicate',
				'phash_duplicate',
				'uploaded',
				'dirstate',
				'origin_name',
				'series_name',
				'additional_metadata',
			)
		bad = keys - allowed
		assert not bad, "Bad key(s) in ret: '%s'!" % bad

		require = set(
				'source_site',
			)
		required_missing = require - keys
		assert not required_missing, "Key(s) missing from ret: '%s'!" % required_missing


	def _processLinksIntoDB(self, linksDicts):

		self.log.info( "Inserting...")


		newItems = 0
		with self.db.session_context() as sess:
			for link in linksDicts:
				if link is None:
					print("linksDicts", linksDicts)
					print("WAT")
					continue

				self.__check_keys(link)

				if 'series_name' in link and self.shouldCanonize:
					link["series_name"] = nt.getCanonicalMangaUpdatesName(link["series_name"])

				have = sess.query(self.target_table)                            \
					.filter(self.target_table.source_site == self.tableKey)     \
					.filter(self.target_table.source_id == link["source_site"]) \
					.scalar()

				if not have:
					newItems += 1
					new_row = self.target_table(
							state       = 'new',            # Should be set automatically.
							source_site = self.tableKey,
							**link
						)

					sess.add(new_row)

					self.log.info("New item: %s", link)


		if self.mon_con:
			self.mon_con.incr('new_links', newItems)

		self.log.info( "Done (%s new items)", newItems)

		return newItems



	def do_fetch_feeds(self, *args, **kwargs):
		self._resetStuckItems()
		# dat = self.getFeed(list(range(50)))
		self.setup()
		dat = self.getFeed(*args, **kwargs)
		new = self._processLinksIntoDB(dat)

		# for x in range(10):
		# 	dat = self.getFeed(pageOverride=x)
		# 	self.processLinksIntoDB(dat)

	def go(self):
		raise RuntimeError("I think you meant to call 'do_fetch_feeds()'")