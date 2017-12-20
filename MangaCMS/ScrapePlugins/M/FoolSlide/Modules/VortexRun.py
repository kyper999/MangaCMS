


import runStatus
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase


import MangaCMS.ScrapePlugins.RunBase
import settings
import settings
import time

class FeedLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase.FoolFeedLoader):



	loggerPath = "Main.Manga.Vx.Fl"
	pluginName = "Vortex Scans Link Retreiver"
	tableKey = "vx"
	dbName = settings.DATABASE_DB_NAME


	tableName = "MangaItems"

	urlBase = "http://reader.vortex-scans.com/"
	feedUrl = urlBase+"latest/{num}/"

class ContentLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase.FoolContentLoader):




	loggerPath = "Main.Manga.Vx.Cl"
	pluginName = "Vortex Scans Content Retreiver"
	tableKey = "vx"
	dbName = settings.DATABASE_DB_NAME
	tableName = "MangaItems"
	groupName = "VortexScans"


	retreivalThreads = 1

	contentSelector = ('article', 'content')

class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Vx.Run"

	pluginName = "VortexLoader"

	sourceName = "Vortex Scans"

	feedLoader = FeedLoader
	contentLoader = ContentLoader


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup():
		fl = Runner()

		fl.go()

