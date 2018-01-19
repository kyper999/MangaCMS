

import runStatus
runStatus.preloadDicts = False

import bs4
import re

import time
import calendar
import dateutil.parser

import settings
import datetime
import urllib.error
import WebRequest
import traceback

from MangaCMS.ScrapePlugins.M.BtLoader.common import checkLogin
import MangaCMS.ScrapePlugins.LoaderBase
from concurrent.futures import ThreadPoolExecutor


# Only downlad items in language specified.
# Set to None to disable filtering (e.g. fetch ALL THE FILES).
DOWNLOAD_ONLY_LANGUAGE = "English"

class DbLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):



	loggerPath = "Main.Manga.Bt.Fl"
	pluginName = "Batoto Link Retreiver"
	tableKey = "bt"
	dbName = settings.DATABASE_DB_NAME


	tableName = "MangaItems"

	urlBase = "http://www.bato.to/"

	feedUrl = "http://www.bato.to/?p=%d"

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




	def getItemFromSeriesPageContainer(self, row):

		cells = row.find_all("td")

		if len(cells) != 5:
			if " chapters hidden in " in row.get_text():
				return None
			self.log.error("Invalid number of TD items in row!")
			for line in row.prettify().split("\n"):
				self.log.error('	%s', line)
			return None

		chapter, lang, dummy_scanlator, dummy_uploader, uploadDate = cells

		if lang is None:
			self.log.error("Row with no language tag")
			for line in row.prettify().split("\n"):
				self.log.error('	%s', line)
			return None

		# Skip uploads in other languages
		if DOWNLOAD_ONLY_LANGUAGE and not DOWNLOAD_ONLY_LANGUAGE in str(lang):
			self.log.info("Skipping due to language filter (%s)", lang.div.get('title', "Unknown!") if lang.div else "Unknown and no div?")
			return None


		dateStr = uploadDate.get_text().strip()
		addDate = self.parseDateStr(dateStr)


		item = {}

		item["retreivalTime"] = calendar.timegm(addDate.timetuple())
		item["sourceUrl"] = chapter.a["href"]

		if not "/reader#" in item["sourceUrl"]:
			self.log.error("No batoto reader link in url?")
			return False

		return item


	def fetchItemsForSeries(self, seriesUrl, historical):
		# for item in items:
		# 	self.log.info( item)
		#

		self.log.info("Loading items from '%s'", seriesUrl)


		try:
			soup = self.wg.getSoup(seriesUrl)
		except urllib.error.URLError:
			self.log.critical("Could not get series from batoto!")
			self.log.critical(traceback.format_exc())
			return []

		# Find the divs containing either new files, or the day a file was uploaded
		itemRows = soup.find_all("tr", class_=re.compile("chapter_row"))
		items = 0
		newItems = 0

		ret = []

		for itemRow in itemRows:

			item = self.getItemFromSeriesPageContainer(itemRow)

			if item:
				items += 1

				# Only fetch an item if it's less then 48 hours old, or we're running
				# in historical mode (which means fetch all the things)
				# if item["retreivalTime"] > (time.time() - 60*60*48) or historical:

				# Fukkit, just grab everything.
				if True:
					newItems += 1
					ret.append(item)


		self.log.info("Found %s of %s items recent enough to download for %s.", newItems, items, seriesUrl)
		return ret


	def getItemsFromSeriesUrls(self, seriesItems, historical):
		ret = []
		self.log.info("Have %s items to fetch data for.", len(seriesItems))
		with ThreadPoolExecutor(max_workers=5) as executor:
			tmp = []
			for seriesUrl in seriesItems:
				tmp.append(executor.submit(self.fetchItemsForSeries, seriesUrl, historical))
			for future in tmp:
				# items = self.fetchItemsForSeries(seriesUrl, historical)
				try:
					items = future.result()

					for item in items:
						ret.append(item)
					if not runStatus.run:
						self.log.info( "Breaking due to exit flag being set")
						break
				except WebRequest.FetchFailureError:
					self.log.error("Failed fetching future!")
					for line in traceback.format_exc().split("\n"):
						self.log.error(line)

		return ret

	def getSeriesUrl(self, row):

		cells = row.find_all("td")
		if len(cells) == 2:
			surl = cells.pop(0).a['href']
			print("Series url:", surl)
			return surl

		return None



	def getFeed(self, rangeOverride=None, rangeOffset=None, historical=False):
		# for item in items:
		# 	self.log.info( item)
		#

		self.log.info( "Loading BT Main Feed")


		seriesPages = []

		if not rangeOverride:
			dayDelta = 2
		else:
			dayDelta = int(rangeOverride)
		if not rangeOffset:
			rangeOffset = 0

		seriesPages = set()

		for daysAgo in range(1, dayDelta+1):

			url = self.feedUrl % (daysAgo+rangeOffset)
			page = self.wg.getpage(url)
			soup = bs4.BeautifulSoup(page, "lxml")

			# Find the divs containing either new files, or the day a file was uploaded
			itemRow = soup.find_all("tr", class_=re.compile("row[01]"))

			for row in itemRow:

				item = self.getSeriesUrl(row)
				if item:
					seriesPages.add(item)

				if not runStatus.run:
					self.log.info( "Breaking due to exit flag being set")
					break


		ret = self.getItemsFromSeriesUrls(seriesPages, historical)
		return ret

	def setup(self):
		checkLogin(self.wg)





if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):

		run = DbLoader()
		run.do_fetch_feeds(historical=True, rangeOverride=30)

		# run.setup()
		# seriesUrl = 'https://bato.to/comic/_/comics/chousuinou-kei-makafushigi-jiken-file-r9039'
		# historical = False

		# run.fetchItemsForSeries(seriesUrl, historical)
		# run.do_fetch_feeds()
		# run.getMainItems()