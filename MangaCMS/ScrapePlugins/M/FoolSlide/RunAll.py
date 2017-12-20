



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
import utilities.testBase as tb

modules = [
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.CanisMajorRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ChibiMangaRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.DokiRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.GoMangaCoRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.IlluminatiMangaRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.JaptemMangaRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.MangatopiaRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.RoseliaRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.S2Run.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.SenseRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.ShoujoSenseRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TripleSevenRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.TwistedHelRun.Runner,
	MangaCMS.ScrapePlugins.M.FoolSlide.Modules.VortexRun.Runner,
]

if __name__ == '__main__':

	with tb.testSetup():
		for module in modules:
			mod = module()
			mod.go()

