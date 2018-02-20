

from .DbLoader import DbLoader
from .ContentLoader import ContentLoader

import runStatus

import MangaCMSOld.ScrapePlugins.RunBase

class Runner(MangaCMSOld.ScrapePlugins.RunBase.ScraperBase):


	loggerPath = "Main.Manga.ASMHentai.Run"
	pluginName = "ASMHentai"


	sourceName = "ASMHentai"
	feedLoader = DbLoader
	contentLoader = ContentLoader


if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():
		run = Runner()
		run.go()
