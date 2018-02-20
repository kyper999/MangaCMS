
import runStatus
from .FeedLoader import FeedLoader
from .ContentLoader import ContentLoader

import MangaCMSOld.ScrapePlugins.RunBase

import time


class Runner(MangaCMSOld.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Dy.Run"

	pluginName = "DyLoader"

	sourceName = "DynastyScans"
	feedLoader = FeedLoader
	contentLoader = ContentLoader



if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():

		run = Runner()
		run.go()

