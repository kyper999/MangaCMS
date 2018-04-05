

import traceback

import re
import copy
import urllib.parse
import time
import calendar
import random
import runStatus

import dateutil.parser

import nameTools as nt
import settings
from . import LoginMixin
import MangaCMS.ScrapePlugins.LoaderBase

class DbLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase, LoginMixin.ExLoginMixin):


	logger_path = "Main.Manga.SadPanda.Fl"
	plugin_name = "SadPanda Link Retreiver"
	plugin_key  = "sp"
	is_manga    = False


	urlBase = "https://exhentai.org/"
	urlFeed = "https://exhentai.org/?page={num}&f_search={search}"


	# -----------------------------------------------------------------------------------
	# The scraping parts
	# -----------------------------------------------------------------------------------



	def loadFeed(self, tag,
				pageOverride=None,
				includeExpunge=False,
				includeLowPower=False,
				includeDownvoted=False
			):
		self.log.info("Retrieving feed content...",)
		if not pageOverride:
			pageOverride = 0  # Pages start at zero. Yeah....
		try:
			# tag = tag.replace(" ", "+")
			tag = urllib.parse.quote_plus(tag)
			pageUrl = self.urlFeed.format(search=tag, num=pageOverride)
			if includeExpunge:
				pageUrl = pageUrl + '&f_sh=on'
			if includeLowPower:
				pageUrl = pageUrl + '&f_sdt1=on'
			if includeDownvoted:
				pageUrl = pageUrl + '&f_sdt2=on'
			soup = self.wg.getSoup(pageUrl)
		except urllib.error.URLError:
			self.log.critical("Could not get page from SadPanda!")
			self.log.critical(traceback.format_exc())
			return None

		# with open("sp_search_{}_{}.html".format(nt.makeFilenameSafe(tag), time.time()), "w") as fp:
		# 	fp.write(soup.prettify())


		return soup


	def getUploadTime(self, dateStr):
		# ParseDatetime COMPLETELY falls over on "YYYY-MM-DD HH:MM" formatted strings. Not sure why.
		# Anyways, dateutil.parser.parse seems to work ok, so use that.
		updateDate = dateutil.parser.parse(dateStr, yearfirst=True)
		# ret = calendar.timegm(updateDate.timetuple())

		# # Patch times for the local-GMT offset.
		# # using `calendar.timegm(time.gmtime()) - time.time()` is NOT ideal, but it's accurate
		# # to a second or two, and that's all I care about.
		# gmTimeOffset = calendar.timegm(time.gmtime()) - time.time()
		# ret = ret - gmTimeOffset
		return updateDate



	def parseItem(self, inRow):
		ret = {}
		itemType, pubDate, name, uploader = inRow.find_all("td")

		# Do not download any galleries we uploaded.
		if uploader.get_text().lower().strip() == settings.sadPanda['login'].lower():
			return None

		category = itemType.img['alt']
		if category.lower() in settings.sadPanda['sadPandaExcludeCategories']:
			self.log.info("Excluded category: '%s'. Skipping.", category)
			return False


		ret['series_name'] = category.title()
		# If there is a torrent link, decompose it so the torrent link doesn't
		# show up in our parsing of the content link.
		if name.find("div", class_='it3'):
			name.find("div", class_='it3').decompose()

		ret['source_id']   = name.a['href']
		ret['origin_name'] = name.a.get_text().strip()
		ret['posted_at']   = self.getUploadTime(pubDate.get_text())

		return ret

	def get_feed(self, searchTag,
				includeExpunge=False,
				includeLowPower=False,
				includeDownvoted=False,
				pageOverride=None
			):
		ret = []

		self.log.info("Loading feed for search: '%s'", searchTag)
		soup = self.loadFeed(searchTag, pageOverride, includeExpunge, includeLowPower, includeDownvoted)

		itemTable = soup.find("table", class_="itg")

		if not itemTable:
			return []

		rows = itemTable.find_all("tr", class_=re.compile("gtr[01]"))
		self.log.info("Found %s items on page.", len(rows))
		for row in rows:

			item = self.parseItem(row)
			if item:
				ret.append(item)


		return ret

	# TODO: Add the ability to re-acquire downloads that are
	# older then a certain age.
	# We have to override the parent class here, since we're doing some more complex stuff.
	def do_fetch_feeds(self):
		self._resetStuckItems()
		self.checkLogin()
		if not self.checkExAccess():
			raise ValueError("Cannot access ex! Wat?")

		for searchTag, includeExpunge, includeLowPower, includeDownvoted in settings.sadPanda['sadPandaSearches']:

			dat = self.get_feed(searchTag, includeExpunge, includeLowPower, includeDownvoted)

			self._process_links_into_db(dat)

			sleeptime = random.randrange(5, 60)
			self.log.info("Sleeping %s seconds.", sleeptime)
			for dummy_x in range(sleeptime):
				time.sleep(1)
				if not runStatus.run:
					self.log.info( "Breaking due to exit flag being set")
					return



# def getHistory():

# 	run = DbLoader()
# 	for x in range(18, 1150):
# 		dat = run.getFeed(pageOverride=x)
# 		run._processLinksIntoDB(dat)



def login():

	run = DbLoader()
	# run.checkLogin()
	# run.checkExAccess()
	for feed in settings.sadPanda['sadPandaSearches']:
		for x in range(8):
			ret = run.getFeed(feed, pageOverride=x)
			if not ret:
				break
			run._processLinksIntoDB(ret)

			time.sleep(5)
	# run.go()


if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):
		# login()
		run = DbLoader()
		run.checkLogin()
		run.do_fetch_feeds()


