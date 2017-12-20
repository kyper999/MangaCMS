
# XDCC Plugins

import MangaCMS.ScrapePlugins.M.IrcGrabber.IrcOfferLoader.IrcQueue
import MangaCMS.ScrapePlugins.M.IrcGrabber.IMangaScans.ImsScrape
import MangaCMS.ScrapePlugins.M.IrcGrabber.EgScans.EgScrape
import MangaCMS.ScrapePlugins.M.IrcGrabber.IlluminatiManga.IrcQueue
import MangaCMS.ScrapePlugins.M.IrcGrabber.SimpleXdccParser.IrcQueue
import MangaCMS.ScrapePlugins.M.IrcGrabber.ModernXdccParser.IrcQueue
import MangaCMS.ScrapePlugins.M.IrcGrabber.TextPackScraper.IrcQueue

# Trigger loader plugins
import MangaCMS.ScrapePlugins.M.IrcGrabber.CatScans.IrcQueue
import MangaCMS.ScrapePlugins.M.IrcGrabber.RenzokuseiScans.IrcQueue

# Channel grabber
import MangaCMS.ScrapePlugins.M.IrcGrabber.ChannelLister.ChanLister

import MangaCMS.ScrapePlugins.RunBase

import time
import traceback
import runStatus


class Runner(MangaCMS.ScrapePlugins.RunBase.ScraperBase):
	loggerPath = "Main.Manga.IRC.Q.Run"

	pluginName = "IrcEnqueue"

	runClasses = [
		MangaCMS.ScrapePlugins.M.IrcGrabber.IMangaScans.ImsScrape.IMSTriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.EgScans.EgScrape.EgTriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.ModernXdccParser.IrcQueue.TriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.TextPackScraper.IrcQueue.TriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.IlluminatiManga.IrcQueue.TriggerLoader,

		MangaCMS.ScrapePlugins.M.IrcGrabber.CatScans.IrcQueue.TriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.RenzokuseiScans.IrcQueue.TriggerLoader,

		MangaCMS.ScrapePlugins.M.IrcGrabber.ChannelLister.ChanLister.ChannelTriggerLoader,

		MangaCMS.ScrapePlugins.M.IrcGrabber.SimpleXdccParser.IrcQueue.TriggerLoader,
		MangaCMS.ScrapePlugins.M.IrcGrabber.IrcOfferLoader.IrcQueue.TriggerLoader,
	]

	def _go(self):

		self.log.info("Checking IRC feeds for updates")

		for runClass in self.runClasses:

			try:
				fl = runClass()
				fl.go()
			except Exception as e:
				self.log.critical("Error in IRC enqueue system!")
				self.log.critical(traceback.format_exc())
				self.log.critical("Exception:")
				self.log.critical(e)
				self.log.critical("Continuing with next source")



			time.sleep(3)

			if not runStatus.run:
				return

if __name__ == "__main__":
	import MangaCMS.lib.logSetup
	MangaCMS.lib.logSetup.initLogging()
	run = Runner()
	run.go()


