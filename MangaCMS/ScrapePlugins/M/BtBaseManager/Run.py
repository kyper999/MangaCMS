

import MangaCMS.ScrapePlugins.RunBase
import MangaCMS.ScrapePlugins.M.BtLoader.Run
import MangaCMS.ScrapePlugins.M.BtSeriesFetcher.Run

class Bunch:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)

class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):

	loggerPath = "Main.Manga.Bt.Base"

	pluginName = "BtBase"

	feedLoader    = Bunch(tableKey='bt')
	contentLoader = None

	def _go(self):
		self.log.info("BtBase calling plugins.")

		self.log.info("BtBase calling Series Monitor.")
		monitor = MangaCMS.ScrapePlugins.M.BtSeriesFetcher.Run.Runner()
		monitor.go()

		self.log.info("BtBase calling Downloader.")


		loader = MangaCMS.ScrapePlugins.M.BtLoader.Run.Runner()
		loader.go()

		self.log.info("BtBase Finished calling plugins.")



if __name__ == "__main__":

	import utilities.testBase as tb

	with tb.testSetup():
		obj = Runner()
		obj.go()


