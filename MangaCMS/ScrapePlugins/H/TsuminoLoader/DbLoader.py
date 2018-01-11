

import pprint
import calendar
import traceback

from dateutil import parser
import settings
import parsedatetime
import urllib.parse
import time
import calendar

import MangaCMS.ScrapePlugins.LoaderBase
class DbLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):


	dbName = settings.DATABASE_DB_NAME
	loggerPath = "Main.Manga.Tsumino.Fl"
	pluginName = "Tsumino Link Retreiver"
	tableKey    = "ts"
	urlBase = "http://www.tsumino.com/"


	tableName = "HentaiItems"

	def loadFeed(self, pageOverride=None):
		self.log.info("Retrieving feed content...",)
		if not pageOverride:
			pageOverride = 1

		try:
			page_params = {
				"PageNumber"         : pageOverride,
				"Text"             : "",
				"Sort"        : "Newest",
				"List"               : 0,
				"Length"             : 0,
				"MinimumRating"      : 0,
			}

			referrer = "http://www.tsumino.com/?PageNumber={num}".format(num=pageOverride)

			soup = self.wg.getJson("http://www.tsumino.com/Books/Operate", postData=page_params, addlHeaders={"Referer" : referrer})

			# print("Response:")
			# pprint.pprint(soup)

		except urllib.error.URLError:
			self.log.critical("Could not get page from Tsumino!")
			self.log.critical(traceback.format_exc())
			return None

		return soup

	def rowToTags(self, content):
		ret = []
		for item in content.find_all("a", class_='book-tag'):
			ret.append(item.get_text().strip().lower())
		return ret

	def getInfo(self, itemUrl):
		ret = {'tags' : []}
		soup = self.wg.getSoup(itemUrl)

		for metarow in soup.find_all("div", class_='book-line'):
			items = metarow.find_all("div", recursive=False)
			assert len(items) == 2

			rowname, rowdat = items

			cat = rowname.get_text().strip()
			if cat == "Title":
				ret['originName'] = rowdat.get_text().strip()

			elif cat == "Uploaded":
				rowtxt = rowdat.get_text().strip()
				ulDate = parser.parse(rowtxt).utctimetuple()

				ultime = calendar.timegm(ulDate)
				if ultime > time.time():
					self.log.warning("Clamping timestamp to now!")
					ultime = time.time()
				ret['retreivalTime'] = ultime
			elif cat == "Category":
				tags = self.rowToTags(rowdat)
				if tags:
					ret["seriesName"] = tags[0]
				else:
					ret["seriesName"] = "Unknown"
			elif cat == "Artist":
				tags = self.rowToTags(rowdat)
				tags = ["artist "+tag for tag in tags]
				ret['tags'].extend(tags)
			elif cat == "Groups" or cat == "Group":
				tags = self.rowToTags(rowdat)
				tags = ["Group "+tag for tag in tags]
				ret['tags'].extend(tags)
			elif cat == "Collections" or cat == "Collection":
				tags = self.rowToTags(rowdat)
				tags = ["Collection "+tag for tag in tags]
				ret['tags'].extend(tags)
			elif cat == "Parody":
				tags = self.rowToTags(rowdat)
				tags = ["Parody "+tag for tag in tags]
				ret['tags'].extend(tags)
			elif cat == "Characters" or cat == "Character":
				tags = self.rowToTags(rowdat)
				tags = ["Character "+tag for tag in tags]
				ret['tags'].extend(tags)
			elif cat == "Tags" or cat == "Tag":
				tags = self.rowToTags(rowdat)
				ret['tags'].extend(tags)


			# Garbage stuff
			elif cat == "Pages" or cat == "Page":
				pass
			elif cat == "Rating":
				pass
			elif cat == "My Rating":
				pass
			elif cat == "Uploader":
				pass

			# The "Download" row has an empty desc
			elif cat == "":
				pass
			else:
				raise RuntimeError("Unknown category tag: '{}' -> '{}'".format(cat, rowdat.prettify()))


		while any(["  " in tag for tag in ret['tags']]):
			ret['tags'] = [tag.replace("  ", " ") for tag in ret['tags']]
		ret['tags'] = [tag.replace(" ", "-") for tag in ret['tags']]
		ret['tags'] = [tag.lower() for tag in ret['tags']]

		# Colons break the tsvector
		ret['tags'] = [tag.replace(":", "-") for tag in ret['tags']]

		ret['tags'] = " ".join(ret['tags'])

		return ret


	def parseItem(self, item):

		if not 'Entry' in item and 'Id' in item['Entry']:
			self.log.error("Missing metadata in item?")
			for line in pprint.pformat(item).split("\n"):
				self.log.error(line.rstrip())
			return None

		ret = {}
		ret['sourceUrl'] = 'http://www.tsumino.com/Book/Info/{}/'.format(item['Entry']['Id'])

		# Do not decend into items where we've already added the item to the DB
		if len(self.getRowsByValue(sourceUrl=ret['sourceUrl'])):
			return None

		ret.update(self.getInfo(ret['sourceUrl']))

		# Yaoi isn't something I'm that in to.
		if "yaoi" in ret["tags"]:
			self.log.info("Yaoi item. Skipping.")
			return None

		return ret

	def getFeed(self, pageOverride=None):
		# for item in items:
		# 	self.log.info(item)
		#

		jdat = self.loadFeed(pageOverride)
		releases = jdat['Data']

		# soup = WebRequest.as_soup(releases)

		# divs = soup.find_all("div", class_='book-grid-item-container')

		ret = []
		for item in releases:
			item = self.parseItem(item)
			if item:
				ret.append(item)


		return ret


def getHistory():

	run = DbLoader()
	# dat = run.getFeed()
	# print(dat)
	for x in range(0, 70):
		dat = run.getFeed(pageOverride=x)
		run._processLinksIntoDB(dat)

def test():
	print("Test!")
	run = DbLoader()
	print(run.do_fetch_feeds())
	# print(run)
	# pprint.pprint(run.getFeed())
	# pprint.pprint(run.getInfo("http://www.tsumino.com/Book/Info/27698/1/sleeping-beauty-dornroschen"))
	pass

if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):
		getHistory()
		# test()
		# run = DbLoader()
		# run.do_fetch_feeds()


