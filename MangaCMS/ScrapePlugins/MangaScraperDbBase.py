
if __name__ == "__main__":
	import runStatus
	runStatus.preloadDicts = False

import logging
import psycopg2
import functools
import abc

import threading
import settings
import os
import traceback


from sqlalchemy import or_

import nameTools as nt
import MangaCMS.db as mdb
import MangaCMS.lib.LogBase

class MangaScraperDbBase(MangaCMS.lib.LogBase.LoggerMixin):


	@abc.abstractmethod
	def pluginName(self):
		return None

	@abc.abstractmethod
	def loggerPath(self):
		return None

	@abc.abstractmethod
	def tableKey(self):
		return None

	@abc.abstractmethod
	def is_manga(self):
		return None

	def __init__(self):
		super().__init__()

		self.db = mdb

		if self.is_manga:
			self.shouldCanonize = True
			self.target_table = self.db.MangaReleases
		else:
			self.shouldCanonize = False
			self.target_table = self.db.HentaiReleases


	# ---------------------------------------------------------------------------------------------------------------------------------------------------------
	# Misc Utilities
	# ---------------------------------------------------------------------------------------------------------------------------------------------------------

	def _resetStuckItems(self):
		self.log.info("Resetting stuck downloads in DB")

		with self.db.session_context() as sess:
			res = sess.query(self.target_table)                         \
				.filter(self.target_table.source_site == self.tableKey) \
				.filter(or_(
					self.target_table.state == 'fetching',
					self.target_table.state == 'processing',
					self.target_table.state == 'missing',
					))                                                  \
				.update({"state" : 'new'})
			self.log.info("Reset updated %s rows!", res)

		self.log.info("Download reset complete")

	# ---------------------------------------------------------------------------------------------------------------------------------------------------------
	# DB Tools
	# ---------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
	import settings
	class TestClass(MangaScraperDbBase):


		pluginName = "Wat?"
		loggerPath = "Wat?"
		tableKey = "mk"
		is_manga = True
		def go(self):
			print("Go?")

		def test(self):
			print("Wat?")


	import utilities.testBase as tb

	with tb.testSetup(load=False):
		obj = TestClass()
		print(obj)
		obj.test()
		obj._resetStuckItems()


