

if __name__ == "__main__":
	import MangaCMS.lib.logSetup
	MangaCMS.lib.logSetup.initLogging()

import MangaCMS.ScrapePlugins.M.BuMonitor.Run
import MangaCMS.ScrapePlugins.M.BtBaseManager.Run


import MangaCMS.ScrapePlugins.H.ASMHentaiLoader.Run
import MangaCMS.ScrapePlugins.H.DjMoeLoader.Run
import MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.Run
import MangaCMS.ScrapePlugins.H.HBrowseLoader.Run
import MangaCMS.ScrapePlugins.H.Hentai2Read.Run
import MangaCMS.ScrapePlugins.H.HitomiLoader.Run
import MangaCMS.ScrapePlugins.H.NHentaiLoader.Run
import MangaCMS.ScrapePlugins.H.PururinLoader.Run
import MangaCMS.ScrapePlugins.H.SadPandaLoader.Run
import MangaCMS.ScrapePlugins.H.TsuminoLoader.Run



import MangaCMS.ScrapePlugins.M.McLoader.Run
import MangaCMS.ScrapePlugins.M.CxLoader.Run
import MangaCMS.ScrapePlugins.M.WebtoonLoader.Run            # Yeah. There is webtoon.com. and WebtoonsReader.com. Confusing much?
import MangaCMS.ScrapePlugins.M.KissLoader.Run
import MangaCMS.ScrapePlugins.M.DynastyLoader.Run
import MangaCMS.ScrapePlugins.M.Crunchyroll.Run
import MangaCMS.ScrapePlugins.M.IrcGrabber.IrcEnqueueRun
import MangaCMS.ScrapePlugins.M.IrcGrabber.BotRunner
import MangaCMS.ScrapePlugins.M.Kawaii.Run
import MangaCMS.ScrapePlugins.M.ZenonLoader.Run
import MangaCMS.ScrapePlugins.M.MangaBox.Run
import MangaCMS.ScrapePlugins.M.MangaHere.Run
import MangaCMS.ScrapePlugins.M.MangaStreamLoader.Run
import MangaCMS.ScrapePlugins.M.MerakiScans.Run
import MangaCMS.ScrapePlugins.M.YoMangaLoader.Run
import MangaCMS.ScrapePlugins.M.SurasPlace.Run
import MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.Run

import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.CanisMajorRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ChibiMangaRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.DokiRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.GoMangaCoRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.IlluminatiMangaRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.JaptemMangaRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangatopiaRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.RoseliaRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.S2Run
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.SenseRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ShoujoSenseRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TripleSevenRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TwistedHelRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.VortexRun
import MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangazukiRun



import MangaCMS.ScrapePlugins.M.MangaMadokami.Run
import MangaCMS.ScrapePlugins.M.BooksMadokami.Run

# Convenience functions to make intervals clearer.
def days(num):
	return 60*60*24*num
def hours(num):
	return 60*60*num
def minutes(num):
	return 60*num

# Plugins in this dictionary are the active plugins. Comment out a plugin to disable it.
# plugin keys specify when plugins will start, and cannot be duplicates.
# All they do is specify the order in which plugins
# are run, initially, starting after 1-minue*{key} intervals
scrapePlugins = {
	0   : (MangaCMS.ScrapePlugins.M.BtBaseManager.Run,                   hours( 1)),
	1   : (MangaCMS.ScrapePlugins.M.MangaStreamLoader.Run,               hours( 6)),
	2   : (MangaCMS.ScrapePlugins.M.BuMonitor.Run,                       hours( 1)),

	11  : (MangaCMS.ScrapePlugins.M.McLoader.Run,                        hours(12)),  # every 12 hours, it's just a single scanlator site.
	12  : (MangaCMS.ScrapePlugins.M.IrcGrabber.IrcEnqueueRun,            hours(12)),  # Queue up new items from IRC bots.
	# 13  : (MangaCMS.ScrapePlugins.M.CxLoader.Run,                        hours(12)),  # every 12 hours, it's just a single scanlator site.
	15  : (MangaCMS.ScrapePlugins.M.IrcGrabber.BotRunner,                hours( 1)),  # Irc bot never returns. It runs while the app is live. Rerun interval doesn't matter, as a result.
	16  : (MangaCMS.ScrapePlugins.M.MangaHere.Run,                       hours(12)),
	17  : (MangaCMS.ScrapePlugins.M.WebtoonLoader.Run,                   hours( 8)),
	18  : (MangaCMS.ScrapePlugins.M.DynastyLoader.Run,                   hours( 8)),
	19  : (MangaCMS.ScrapePlugins.M.KissLoader.Run,                      hours( 1)),
	20  : (MangaCMS.ScrapePlugins.M.Crunchyroll.Run,                     hours( 4)),
	22  : (MangaCMS.ScrapePlugins.M.Kawaii.Run,                          hours(12)),
	23  : (MangaCMS.ScrapePlugins.M.ZenonLoader.Run,                     hours(24)),
	24  : (MangaCMS.ScrapePlugins.M.MangaBox.Run,                        hours(12)),
	25  : (MangaCMS.ScrapePlugins.M.YoMangaLoader.Run,                   hours(12)),
	26  : (MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.Run,          hours(12)),
	27  : (MangaCMS.ScrapePlugins.M.MerakiScans.Run,                     hours(12)),


	41  : (MangaCMS.ScrapePlugins.H.HBrowseLoader.Run,                   hours( 2)),
	42  : (MangaCMS.ScrapePlugins.H.PururinLoader.Run,                   hours( 2)),
	44  : (MangaCMS.ScrapePlugins.H.NHentaiLoader.Run,                   hours( 2)),
	45  : (MangaCMS.ScrapePlugins.H.SadPandaLoader.Run,                  hours(12)),
	46  : (MangaCMS.ScrapePlugins.H.DjMoeLoader.Run,                     hours( 4)),
	47  : (MangaCMS.ScrapePlugins.H.HitomiLoader.Run,                    hours( 4)),
	48  : (MangaCMS.ScrapePlugins.H.ASMHentaiLoader.Run,                 hours( 4)),
	49  : (MangaCMS.ScrapePlugins.H.Hentai2Read.Run,                     hours( 6)),
	50  : (MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.Run,              hours( 6)),
	51  : (MangaCMS.ScrapePlugins.H.TsuminoLoader.Run,                   hours( 6)),

	# FoolSlide modules

	61 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.CanisMajorRun,      hours(12)),
	62 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ChibiMangaRun,      hours(12)),
	63 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.DokiRun,            hours(12)),
	64 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.GoMangaCoRun,       hours(12)),
	65 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.IlluminatiMangaRun, hours(12)),
	# 66 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.JaptemMangaRun,     hours(12)),
	67 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangatopiaRun,      hours(12)),
	# 68 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.RoseliaRun,         hours(12)),
	69 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.S2Run,              hours(12)),
	70 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.SenseRun,           hours(12)),
	71 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ShoujoSenseRun,     hours(12)),
	72 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TripleSevenRun,     hours(12)),
	73 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TwistedHelRun,      hours(12)),
	74 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.VortexRun,          hours(12)),
	75 : (MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangazukiRun,       hours(12)),

	80 : (MangaCMS.ScrapePlugins.M.MangaMadokami.Run,                    hours(4)),
	81 : (MangaCMS.ScrapePlugins.M.BooksMadokami.Run,                    hours(4)),

}


if __name__ == "__main__":

	# scrapePlugins = {
		# 0 : (TextScrape.BakaTsuki.Run,                       60*60*24*7),  # Every 7 days, because books is slow to update
		# 1 : (TextScrape.JapTem.Run,                          60*60*24*5),
		# 3 : (TextScrape.Guhehe.Run,                          60*60*24*5),
		# 2 : (TextScrape.ReTranslations.Run,                  60*60*24*1)   # There's not much to actually scrape here, and it's google, so I don't mind hitting their servers a bit.
	# }

	print("Test run!")
	import nameTools as nt

	def callGoOnClass(passedModule):
		print("Passed module = ", passedModule)
		print("Calling class = ", passedModule.Runner)
		instance = passedModule.Runner()
		instance.go()
		print("Instance:", instance)


	nt.dirNameProxy.startDirObservers()
	import signal
	import runStatus

	def signal_handler(dummy_signal, dummy_frame):
		if runStatus.run:
			runStatus.run = False
			print("Telling threads to stop (activePlugins)")
		else:
			print("Multiple keyboard interrupts. Raising")
			raise KeyboardInterrupt

	run = [
			MangaCMS.ScrapePlugins.H.PururinLoader.Run,
			MangaCMS.ScrapePlugins.H.NHentaiLoader.Run,
			MangaCMS.ScrapePlugins.H.SadPandaLoader.Run,
			MangaCMS.ScrapePlugins.H.DjMoeLoader.Run,
			MangaCMS.ScrapePlugins.H.DjMoeLoader.Retag,
			MangaCMS.ScrapePlugins.H.HitomiLoader.Run,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.CanisMajorRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ChibiMangaRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.DokiRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.GoMangaCoRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.IlluminatiMangaRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.JaptemMangaRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangatopiaRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.RoseliaRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.S2Run,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.SenseRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ShoujoSenseRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TripleSevenRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangazukiRun,
			MangaCMS.ScrapePlugins.M.MangaMadokami.Run,
			MangaCMS.ScrapePlugins.M.BooksMadokami.Run,
			MangaCMS.ScrapePlugins.M.CxLoader.Run,
			MangaCMS.ScrapePlugins.M.ZenonLoader.Run,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TwistedHelRun,
			MangaCMS.ScrapePlugins.M.FoolSlide.Modules.VortexRun,
			MangaCMS.ScrapePlugins.M.McLoader.Run,
			MangaCMS.ScrapePlugins.M.MangaHere.Run,
			MangaCMS.ScrapePlugins.M.WebtoonLoader.Run,
			MangaCMS.ScrapePlugins.M.DynastyLoader.Run,
			MangaCMS.ScrapePlugins.M.KissLoader.Run,
			MangaCMS.ScrapePlugins.M.Crunchyroll.Run,
			MangaCMS.ScrapePlugins.M.Kawaii.Run,
			MangaCMS.ScrapePlugins.M.MangaBox.Run,
			MangaCMS.ScrapePlugins.M.YoMangaLoader.Run,
			MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.Run,
			MangaCMS.ScrapePlugins.H.HBrowseLoader.Run,
		]
	signal.signal(signal.SIGINT, signal_handler)
	import sys
	import traceback
	print("Starting")
	try:
		if len(sys.argv) > 1 and int(sys.argv[1]) in scrapePlugins:
			plugin, interval = scrapePlugins[int(sys.argv[1])]
			print(plugin, interval)
			callGoOnClass(plugin)
		else:

			print("Loopin!", scrapePlugins)
			for plugin in run:
				print(plugin)
				try:
					callGoOnClass(plugin)
				except Exception:
					print()
					print("Wat?")
					traceback.print_exc()
					# raise
					print("Continuing on with next source.")

	except:
		traceback.print_exc()


	print("Complete")

	nt.dirNameProxy.stop()
	sys.exit()
