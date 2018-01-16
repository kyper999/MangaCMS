
import WebRequest
import settings
import traceback
import os.path



import time
import calendar
import datetime
import dateutil.parser
import urllib.error


import runStatus

import bs4
import re
import MangaCMS.ScrapePlugins.SeriesRetreivalDbBase

from MangaCMS.ScrapePlugins.M.BtLoader.common import checkLogin


# Only downlad items in language specified.
# Set to None to disable filtering (e.g. fetch ALL THE FILES).
DOWNLOAD_ONLY_LANGUAGE = "English"

class SeriesEnqueuer(MangaCMS.ScrapePlugins.SeriesRetreivalDbBase.SeriesScraperDbBase):

	loggerPath      = "Main.BtS.Se"
	pluginName      = "Batoto Series Link Retreiver"
	tableKey        = "bt"
	dbName          = settings.DATABASE_DB_NAME

	tableName       = "MangaItems"

	urlBase         = "http://bato.to/"

	seriesUrl       = "http://bato.to/comic/_/comics/%s"

	seriesTableName = "batotoSeries"

	def parseDateStr(self, inStr):

		# For strings like "n Days Ago", split out the "n", convert it to an int, and take the
		# time-delta so we know what actual date it refers to.

		# convert instances of "a minute ago" to "1 minute ago", for mins, hours, etc...
		inStr = inStr.strip()
		if inStr.lower().startswith("an"):
			inStr = "1"+inStr[2:]

		if inStr.lower().startswith("a"):
			inStr = "1"+inStr[1:]

		if "just now" in inStr:
			updateDate = datetime.datetime.now()
		elif "months ago" in inStr or "month ago" in inStr:
			monthsAgo = inStr.split()[0]
			monthsAgo = int(monthsAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(monthsAgo*7)
		elif "weeks ago" in inStr or "week ago" in inStr:
			weeksAgo = inStr.split()[0]
			weeksAgo = int(weeksAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(weeksAgo*7)
		elif "days ago" in inStr or "day ago" in inStr:
			daysAgo = inStr.split()[0]
			daysAgo = int(daysAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(daysAgo)
		elif "hours ago" in inStr or "hour ago" in inStr:
			hoursAgo = inStr.split()[0]
			hoursAgo = int(hoursAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(0, hoursAgo*60*60)
		elif "minutes ago" in inStr or "minute ago" in inStr:
			minutesAgo = inStr.split()[0]
			minutesAgo = int(minutesAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(0, minutesAgo*60)
		elif "seconds ago" in inStr or "second ago" in inStr:
			secondsAgo = inStr.split()[0]
			secondsAgo = int(secondsAgo)
			updateDate = datetime.datetime.now() - datetime.timedelta(0, secondsAgo)
		else:
			# self.log.warning("Date parsing failed. Using fall-back parser")
			updateDate = dateutil.parser.parse(inStr, fuzzy=True)
			# self.log.warning("Failing string = '%s'", inStr)
			# self.log.warning("As parsed = '%s'", updateDate)

		return updateDate



	def getItemFromContainer(self, row):
		cells = row.find_all("td")

		if len(cells) != 5:
			self.log.error("Invalid number of TD items in row!")
			return None

		chapter, lang, dummy_scanlator, dummy_uploader, uploadDate = cells


		# Skip uploads in other languages
		if DOWNLOAD_ONLY_LANGUAGE and not DOWNLOAD_ONLY_LANGUAGE in str(lang):
			self.log.info("Skipping due to language filter (%s)", lang.div.get('title', "Unknown!") if lang.div else "Unknown and no div?")
			return None


		dateStr = uploadDate.get_text().strip()
		addDate = self.parseDateStr(dateStr)

		item = {}

		item["date"] = calendar.timegm(addDate.timetuple())
		item["dlLink"] = chapter.a["href"]

		if not '://bato.to/reader#' in item["dlLink"]:

			return False

		return item


	def fetchItemFromRow(self, row):
		# for item in items:
		# 	self.log.info( item)

		self.log.info("Loading items for series '%s'", row["seriesName"])


		url = self.seriesUrl % row["seriesId"]
		soup = self.wg.getSoup(url)

		with open("test.html", "w") as fp:
			fp.write(soup.prettify())

		# Find the divs containing either new files, or the day a file was uploaded
		itemRows = soup.find_all("tr", class_="chapter_row")

		self.log.info("Found %s table rows", len(itemRows))

		items = 0
		newItems = 0
		for itemRow in itemRows:

			item = self.getItemFromContainer(itemRow)

			if item:
				items += 1

				# # Flags has to be an empty string, because the DB is annoying.
				# #
				# # TL;DR, comparing with LIKE in a column that has NULLs in it is somewhat broken.
				#

				haveRows = self.getRowsByValue(sourceUrl=item["dlLink"])
				if not haveRows:
					newItems += 1

					self.insertIntoDb(retreivalTime = item["date"],
										sourceUrl   = item["dlLink"],
										dlState     = 0,
										flags       = '')

		self.log.info("Found %s items for %s, %s were new.", items, row["seriesName"], newItems)


	def do_fetch_content(self):


		self.resetStuckSeriesItems()
		self.log.info("Getting feed items")
		rows = self.getSeriesRowsByValue(dlState=0)
		self.log.info("Have %s new items to scan for items.", len(rows))
		for row in rows:
			try:
				self.updateSeriesDbEntryById(row["dbId"], dlState=1)
				self.fetchItemFromRow(row)
				self.updateSeriesDbEntryById(row["dbId"], dlState=2, lastUpdate=time.time())
			except urllib.error.URLError:
				self.log.error("Failure fetching pave: '%s'",  self.seriesUrl % row["seriesId"])
				for line in traceback.format_exc().split("\n"):
					self.log.error("%s", line)

			except WebRequest.WebGetException:
				self.log.error("Failure fetching pave: '%s'",  self.seriesUrl % row["seriesId"])
				for line in traceback.format_exc().split("\n"):
					self.log.error("%s", line)


			if not runStatus.run:
				self.log.info( "Breaking due to exit flag being set")
				break



			# return

		self.log.info("Complete")


	def setup(self):
		checkLogin(self.wg)


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup():
		fl = SeriesEnqueuer()
		# fl.do_fetch_content()


		test = {
			'seriesId'   : 'lies-of-the-sheriff-evans-dead-or-love-r21685',
			'seriesName' : 'Lies of the Sheriff Evans: Dead or Love',
		}
		fl.fetchItemFromRow(test)
		test = {
			'seriesId'   : 'cardcaptor-sakura-clear-card-arc-r18987',
			'seriesName' : 'Cardcaptor Sakura - Clear Card Arc',
		}
		fl.fetchItemFromRow(test)

		# fl.getSeriesUrls()

		# fl.getAllItems()

