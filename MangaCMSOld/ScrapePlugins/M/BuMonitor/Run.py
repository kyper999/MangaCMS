
from . import MonitorRun
from . import ChangeMonitor
import MangaCMSOld.ScrapePlugins.RunBase

class Runner(MangaCMSOld.ScrapePlugins.RunBase.ScraperBase):

	loggerPath = "Main.Manga.Bu.Run"
	pluginName = "BuMon"

	def _go(self):

		runner = MonitorRun.BuWatchMonitor()
		runner.go()

		chMon = ChangeMonitor.BuDateUpdater()
		chMon.go()



if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():
		mon = Runner()
		mon.go()

