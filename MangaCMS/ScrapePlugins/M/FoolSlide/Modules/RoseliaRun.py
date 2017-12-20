


import runStatus
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase
import MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase


import MangaCMS.ScrapePlugins.RunBase
import settings
import time

class ContentLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideDownloadBase.FoolContentLoader):


	loggerPath = "Main.Manga.Rs.Cl"
	pluginName = "Roselia Scans Content Retreiver"
	tableKey = "rs"
	dbName = settings.DATABASE_DB_NAME
	tableName = "MangaItems"
	groupName = "RoseliaScans"


	retreivalThreads = 1

	contentSelector = ('article', 'content')


class FeedLoader(MangaCMS.ScrapePlugins.M.FoolSlide.FoolSlideFetchBase.FoolFeedLoader):


	loggerPath = "Main.Manga.Rs.Fl"
	pluginName = "Roselia Scans Link Retreiver"
	tableKey = "rs"
	dbName = settings.DATABASE_DB_NAME


	tableName = "MangaItems"

	urlBase = "http://reader.roseliascans.com/"
	feedUrl = urlBase+"latest/{num}/"



class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Rs.Run"

	pluginName = "RoseliaLoader"


	sourceName = "Roselia"

	feedLoader = FeedLoader
	contentLoader = ContentLoader


if __name__ == '__main__':
	import utilities.testBase as tb

	with tb.testSetup():
		fl = Runner()

		fl.go()

