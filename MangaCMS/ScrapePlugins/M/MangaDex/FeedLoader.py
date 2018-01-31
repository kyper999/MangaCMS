
import runStatus
runStatus.preloadDicts = False



import urllib.parse
import time
import calendar
import parsedatetime
import settings

import MangaCMS.ScrapePlugins.LoaderBase

# Only downlad items in language specified.
# Set to None to disable filtering (e.g. fetch ALL THE FILES).
DOWNLOAD_ONLY_LANGUAGE = "English"

class FeedLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):

	loggerPath = "Main.Manga.MDx.Fl"
	pluginName = "MangaDex Link Retreiver"
	tableKey = "mdx"

	tableName = "MangaItems"

	urlBase    = "https://mangadex.com/"
	seriesBase = "https://mangadex.com/1"

	def setup(self):
		now = int(time.time() * 1000)
		self.wg.getpage("https://mangadex.com/ajax/actions.ajax.php?function=hentai_toggle&mode=1&_={}".format(now))

	def getUpdatedSeries(self, url):
		ret = set()

		soup = self.wg.getSoup(url)

		if soup.find("div", class_='table-responsive'):
			mainDiv = soup.find("div", class_='table-responsive')
		else:
			raise ValueError("Could not find listing table?")

		for child in mainDiv.find_all("a", class_='manga_title'):
			if child:
				seriesUrl = urllib.parse.urljoin(self.urlBase, child['href'])
				ret.add(seriesUrl)


		self.log.info("Found %s series", len(ret))

		return ret


	def getUpdatedSeriesPages(self):
		# Historical stuff goes here, if wanted.

		self.log.info( "Loading MangaDex Items")

		pages = self.getUpdatedSeries(self.seriesBase)



		self.log.info("Found %s total items", len(pages))
		return pages



	def getSeriesInfoFromSoup(self, soup):
		# Should probably extract tagging info here. Laaaaazy
		# MangaUpdates interface does a better job anyways.
		titleA = soup.find("h3", class_='panel-title')
		return {"seriesName": titleA.get_text(strip=True)}

	def getChaptersFromSeriesPage(self, soup):
		sname = soup.find("h3", class_='panel-title').get_text(strip=True)
		table = soup.find('div', id='torrents')

		# import pdb
		# pdb.set_trace()

		items = []
		for row in table.find_all("tr"):
			if not row.a:
				continue  # Skip the table header row

			tds = row.find_all("td")
			if len(tds) != 7:
				self.log.warning("Invalid number of table entries: %s", len(tds))
				self.log.warning("Row: %s", row)
				continue

			chapter_name, lang, group, dummy_uploader, dummy_success, dummy_views, ultime = tds

			lang = lang.img['title']
			if lang != DOWNLOAD_ONLY_LANGUAGE:
				self.log.warning("Skipping non-english item: %s", lang)
				continue

			item = {}

			# Name is formatted "{seriesName} {bunch of spaces}\n{chapterName}"
			# Clean up that mess to "{seriesName} - {chapterName}"
			name = chapter_name.get_text().strip()
			name = name.replace("\n", " - ")
			while "  " in name:
				name = name.replace("  ", " ")

			name = "{} - {} [{}, {}]".format(sname, name, "MangaDex", group.get_text(strip=True))

			item["originName"] = name
			item["sourceUrl"]  = urllib.parse.urljoin(self.urlBase, chapter_name.a['href'])
			dateStr = ultime['title'].strip()
			itemDate, status = parsedatetime.Calendar().parse(dateStr)
			if status < 1:
				continue

			item['retreivalTime'] = calendar.timegm(itemDate)
			items.append(item)


		return items

	def getChapterLinkFromSeriesPage(self, seriesUrl):
		ret = []
		soup = self.wg.getSoup(seriesUrl)

		seriesInfo = self.getSeriesInfoFromSoup(soup)

		chapters = self.getChaptersFromSeriesPage(soup)
		for chapter in chapters:

			for key, val in seriesInfo.items(): # Copy series info into each chapter
				chapter[key] = val

			ret.append(chapter)

		self.log.info("Found %s items on page for series '%s'", len(ret), seriesInfo['seriesName'])

		return ret

	def getFeed(self):
		toScan = self.getUpdatedSeriesPages()

		ret = []

		for url in toScan:
			items = self.getChapterLinkFromSeriesPage(url)
			for item in items:
				if item in ret:
					raise ValueError("Duplicate items in ret?")
				ret.append(item)

		return ret

	def get_history(self):
		idx = 0
		found = 0
		have_spages = True

		while have_spages:
			soup = self.wg.getSoup("https://mangadex.com/titles/{idx}".format(idx=idx))
			idx += 100
			main_div = soup.find("div", class_='table-responsive')
			tmp_list = []
			if main_div:
				for row in main_div.find_all("tr"):
					if row.a:
						surl = urllib.parse.urljoin(self.urlBase, row.a['href'])
						tmp_list.append(surl)

						ret = []
						items = self.getChapterLinkFromSeriesPage(surl)
						for item in items:
							if item in ret:
								raise ValueError("Duplicate items in ret?")
							ret.append(item)
							found += 1
						self._processLinksIntoDB(ret)
						self.log.info("Found %s items so far", found)


			have_spages = len(tmp_list)




		# self.log.info("Found %s total items", len(pages))
		# return pages


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup():
		fl = FeedLoader()
		fl.setup()
		fl.get_history()
		# fl.do_fetch_feeds()
		# print(fl.getUpdatedSeriesPages())
		# print(fl.getAllItems())
		# fl.resetStuckItems()
		# cl = fl.getChapterLinkFromSeriesPage("https://mangadex.com/manga/19969")
		# cl = fl.getChapterLinkFromSeriesPage("https://mangadex.com/manga/9134")
		# print(cl)
		# fl.getSeriesUrls()

		# fl.getAllItems()

