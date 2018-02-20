

from .dbLoader import DbLoader
from .contentLoader import ContentLoader

import MangaCMSOld.ScrapePlugins.RunBase

import time

import runStatus


class Runner(MangaCMSOld.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Cx.Run"

	pluginName = "CxLoader"

	sourceName = "CxC Scans"
	feedLoader = DbLoader
	contentLoader = ContentLoader


if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():
		run = Runner()
		run.go()
