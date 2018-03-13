
from . import MonitorRun
from . import ChangeMonitor
import MangaCMS.ScrapePlugins.RunBase

class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):

	loggerPath = "Main.Manga.Bu.BuRescan"
	pluginName = "BuRescan"

	def _go(self):

		runner = MonitorRun.BuWatchMonitor()
		runner.getAllManga()




if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():
		mon = Runner()
		mon.go()

