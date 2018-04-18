
import runStatus
runStatus.preloadDicts = False



import urllib.parse
import time
import calendar
import parsedatetime
import datetime
import settings

import MangaCMS.ScrapePlugins.LoaderBase

# Only downlad items in language specified.
# Set to None to disable filtering (e.g. fetch ALL THE FILES).
DOWNLOAD_ONLY_LANGUAGE = "English"

class FeedLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):

	logger_path  = "Main.Manga.MDx.Fl"
	plugin_name  = "MangaDex Link Retreiver"
	plugin_key   = "mdx"
	is_manga     = True


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

		self.log.info("Loading MangaDex Items")

		pages = self.getUpdatedSeries(self.seriesBase)



		self.log.info("Found %s total items", len(pages))
		return pages



	def getSeriesInfoFromSoup(self, soup):
		# Should probably extract tagging info here. Laaaaazy
		# MangaUpdates interface does a better job anyways.
		titleA = soup.find("h3", class_='panel-title')
		return {"series_name": titleA.get_text(strip=True)}

	def getChaptersFromSeriesPage(self, soup):
		sname = soup.find("h3", class_='panel-title').get_text(strip=True)

		# import pdb
		# pdb.set_trace()

		items = []
		for row in soup.find_all("tr"):
			if not row.a:
				continue  # Skip the table header row

			# And any other rows
			if not "chapter_" in row.get("id", ""):
				continue

			tds = row.find_all("td")
			if len(tds) != 8:
				self.log.warning("Invalid number of table entries: %s", len(tds))
				self.log.warning("Row: %s", row)
				continue

			dummy_something, chapter_name, dummy_discussion, lang, group, dummy_uploader, dummy_views, ultime = tds

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

			item["origin_name"] = name
			item["source_id"]  = urllib.parse.urljoin(self.urlBase, chapter_name.a['href'])
			dateStr = ultime['title'].strip()
			itemDate, status = parsedatetime.Calendar().parse(dateStr)
			if status < 1:
				continue

			item['posted_at'] = datetime.datetime(*itemDate[:6])
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

		self.log.info("Found %s items on page for series '%s'", len(ret), seriesInfo['series_name'])

		return ret

	def get_feed(self):
		toScan = self.getUpdatedSeriesPages()


		for url in toScan:
			ret = []
			items = self.getChapterLinkFromSeriesPage(url)
			for item in items:
				if item in ret:
					raise ValueError("Duplicate items in ret?")
				ret.append(item)

			self._process_links_into_db(ret)

		return []

	def get_history(self):
		idx = 0
		found = 0
		have_spages = True

		while have_spages:
			soup = self.wg.getSoup("https://mangadex.com/titles/{idx}".format(idx=idx))
			idx += 100
			main_div = soup.find("div", class_='row')
			tmp_list = []
			if main_div:
				divs = main_div.find_all("div", class_='col-sm-6')
				self.log.info("Found %s series links")
				for row in divs:
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
						self._process_links_into_db(ret)
						self.log.info("Found %s items so far", found)


			have_spages = len(tmp_list)




		# self.log.info("Found %s total items", len(pages))
		# return pages


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup(load=False):
		fl = FeedLoader()
		fl.setup()
		fl.get_history()
		# fl.get_feed()
		# fl.do_fetch_feeds()
		# print(fl.getUpdatedSeriesPages())
		# print(fl.getAllItems())
		# fl.resetStuckItems()
		# cl = fl.getChapterLinkFromSeriesPage("https://mangadex.com/manga/8246")
		# cl = fl.getChapterLinkFromSeriesPage("https://mangadex.com/manga/19969")
		# cl = fl.getChapterLinkFromSeriesPage("https://mangadex.com/manga/9134")
		# print(cl)
		# fl.getSeriesUrls()

		# fl.getAllItems()

