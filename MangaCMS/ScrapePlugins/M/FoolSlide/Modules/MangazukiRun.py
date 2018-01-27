


import runStatus
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase


import MangaCMS.ScrapePlugins.RunBase
import settings
import settings
import time

class FeedLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase.FoolFeedLoader):



	loggerPath = "Main.Manga.Mzk.Fl"
	pluginName = "Mangazuki Link Retreiver"
	tableKey = "mzk"
	dbName = settings.DATABASE_DB_NAME


	tableName = "MangaItems"

	urlBase = "https://mangazuki.co/"
	feedUrl = urlBase+"latest-release?page={num}"

class ContentLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase.FoolContentLoader):




	loggerPath = "Main.Manga.Mzk.Cl"
	pluginName = "Mangazuki Content Retreiver"
	tableKey = "mzk"
	dbName = settings.DATABASE_DB_NAME
	tableName = "MangaItems"
	groupName = "Mangazuki"


	retreivalThreads = 1

	contentSelector = ('article', 'content')

class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Mzk.Run"

	pluginName = "MangazukiLoader"

	sourceName = "Mangazuki Scans"

	feedLoader = FeedLoader
	contentLoader = ContentLoader


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup():
		fl = Runner()

		fl.go()

