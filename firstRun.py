

'''
Do the initial database setup, so a functional system can be bootstrapped from an empty database.
'''

import MangaCMS.ScrapePlugins.M.BuMonitor.MonitorRun
import MangaCMS.ScrapePlugins.M.BuMonitor.ChangeMonitor
import MangaCMS.ScrapePlugins.H.DjMoeLoader.DbLoader

import MangaCMS.ScrapePlugins.M.BtSeriesFetcher.SeriesEnqueuer
import MangaCMS.ScrapePlugins.M.BtLoader.DbLoader


'''
We need one instance of each type of plugin (series, manga, hentai), plus some extra for no particular reason (safety!)

Each plugin is instantiated, and then the plugin database setup method is called.

'''
toInit = [
	MangaCMS.ScrapePlugins.M.BuMonitor.MonitorRun.BuWatchMonitor,
	MangaCMS.ScrapePlugins.M.BuMonitor.ChangeMonitor.BuDateUpdater,
	MangaCMS.ScrapePlugins.H.DjMoeLoader.DbLoader.DbLoader,
	MangaCMS.ScrapePlugins.M.BtSeriesFetcher.SeriesEnqueuer.SeriesEnqueuer,
	MangaCMS.ScrapePlugins.M.BtLoader.DbLoader.DbLoader,
	]


def checkInitTables():
	for plg in toInit:
		print(plg)
		tmp = plg()
		tmp.checkInitPrimaryDb()
		if hasattr(tmp, "checkInitSeriesDb"):
			tmp.checkInitSeriesDb()

if __name__ == "__main__":
	import MangaCMS.lib.logSetup
	MangaCMS.lib.logSetup.initLogging()
	checkInitTables()
