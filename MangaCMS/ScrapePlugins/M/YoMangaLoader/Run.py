
import runStatus
from .Loader import Loader

import MangaCMS.ScrapePlugins.RunBase

import time


class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.Yo.Run"

	pluginName = "YoLoader"


	def _go(self):

		self.log.info("Checking YoManga feeds for updates")
		fl = Loader()
		fl.go()



if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():

		run = Runner()
		run.go()

