
import inspect
import MangaCMS.lib.logSetup
MangaCMS.lib.logSetup.initLogging()

import MangaCMS.cleaner.processDownload
import MangaCMS.DbBase

import MangaCMS.ScrapePlugins.H.ASMHentaiLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.ASMHentaiLoader.DbLoader
import MangaCMS.ScrapePlugins.H.DjMoeLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.DjMoeLoader.DbLoader
import MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.DbLoader
import MangaCMS.ScrapePlugins.H.HBrowseLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.HBrowseLoader.DbLoader
import MangaCMS.ScrapePlugins.H.Hentai2Read.ContentLoader
import MangaCMS.ScrapePlugins.H.Hentai2Read.DbLoader
import MangaCMS.ScrapePlugins.H.HitomiLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.HitomiLoader.DbLoader
import MangaCMS.ScrapePlugins.H.NHentaiLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.NHentaiLoader.DbLoader
import MangaCMS.ScrapePlugins.H.PururinLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.PururinLoader.DbLoader
import MangaCMS.ScrapePlugins.H.SadPandaLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.SadPandaLoader.DbLoader
import MangaCMS.ScrapePlugins.H.TsuminoLoader.ContentLoader
import MangaCMS.ScrapePlugins.H.TsuminoLoader.DbLoader
import MangaCMS.ScrapePlugins.M.BooksMadokami.ContentLoader
import MangaCMS.ScrapePlugins.M.BooksMadokami.DbLoader
import MangaCMS.ScrapePlugins.M.Crunchyroll.ContentLoader
import MangaCMS.ScrapePlugins.M.Crunchyroll.DbLoader
import MangaCMS.ScrapePlugins.M.CxLoader.contentLoader
import MangaCMS.ScrapePlugins.M.CxLoader.dbLoader
import MangaCMS.ScrapePlugins.M.DynastyLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.DynastyLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.FoolSlide.VortexLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.FoolSlide.VortexLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.Kawaii.ContentLoader
import MangaCMS.ScrapePlugins.M.Kawaii.FeedLoader
import MangaCMS.ScrapePlugins.M.KissLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.KissLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.MangaBox.Loader
import MangaCMS.ScrapePlugins.M.MangaHere.ContentLoader
import MangaCMS.ScrapePlugins.M.MangaHere.FeedLoader
import MangaCMS.ScrapePlugins.M.MangaMadokami.ContentLoader
import MangaCMS.ScrapePlugins.M.MangaMadokami.FeedLoader
import MangaCMS.ScrapePlugins.M.MangaStreamLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.MangaStreamLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.McLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.McLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.MerakiScans.ContentLoader
import MangaCMS.ScrapePlugins.M.MerakiScans.FeedLoader
import MangaCMS.ScrapePlugins.M.SurasPlace.ContentLoader
import MangaCMS.ScrapePlugins.M.SurasPlace.FeedLoader
import MangaCMS.ScrapePlugins.M.WebtoonLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.WebtoonLoader.FeedLoader
import MangaCMS.ScrapePlugins.M.WebtoonsReader.ContentLoader
import MangaCMS.ScrapePlugins.M.WebtoonsReader.FeedLoader
import MangaCMS.ScrapePlugins.M.YoMangaLoader.Loader
import MangaCMS.ScrapePlugins.M.ZenonLoader.ContentLoader
import MangaCMS.ScrapePlugins.M.ZenonLoader.FeedLoader

files = [
	MangaCMS.ScrapePlugins.H.ASMHentaiLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.ASMHentaiLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.DjMoeLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.DjMoeLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.DoujinOnlineLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.HBrowseLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.HBrowseLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.Hentai2Read.ContentLoader,
	MangaCMS.ScrapePlugins.H.Hentai2Read.DbLoader,
	MangaCMS.ScrapePlugins.H.HitomiLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.HitomiLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.NHentaiLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.NHentaiLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.PururinLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.PururinLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.SadPandaLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.SadPandaLoader.DbLoader,
	MangaCMS.ScrapePlugins.H.TsuminoLoader.ContentLoader,
	MangaCMS.ScrapePlugins.H.TsuminoLoader.DbLoader,
	MangaCMS.ScrapePlugins.M.BooksMadokami.ContentLoader,
	MangaCMS.ScrapePlugins.M.BooksMadokami.DbLoader,
	MangaCMS.ScrapePlugins.M.Crunchyroll.ContentLoader,
	MangaCMS.ScrapePlugins.M.Crunchyroll.DbLoader,
	MangaCMS.ScrapePlugins.M.CxLoader.contentLoader,
	MangaCMS.ScrapePlugins.M.CxLoader.dbLoader,
	MangaCMS.ScrapePlugins.M.DynastyLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.DynastyLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.FoolSlide.VortexLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.FoolSlide.VortexLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.GameOfScanlationLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.Kawaii.ContentLoader,
	MangaCMS.ScrapePlugins.M.Kawaii.FeedLoader,
	MangaCMS.ScrapePlugins.M.KissLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.KissLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.MangaBox.Loader,
	MangaCMS.ScrapePlugins.M.MangaHere.ContentLoader,
	MangaCMS.ScrapePlugins.M.MangaHere.FeedLoader,
	MangaCMS.ScrapePlugins.M.MangaMadokami.ContentLoader,
	MangaCMS.ScrapePlugins.M.MangaMadokami.FeedLoader,
	MangaCMS.ScrapePlugins.M.MangaStreamLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.MangaStreamLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.McLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.McLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.MerakiScans.ContentLoader,
	MangaCMS.ScrapePlugins.M.MerakiScans.FeedLoader,
	MangaCMS.ScrapePlugins.M.SurasPlace.ContentLoader,
	MangaCMS.ScrapePlugins.M.SurasPlace.FeedLoader,
	MangaCMS.ScrapePlugins.M.WebtoonLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.WebtoonLoader.FeedLoader,
	MangaCMS.ScrapePlugins.M.WebtoonsReader.ContentLoader,
	MangaCMS.ScrapePlugins.M.WebtoonsReader.FeedLoader,
	MangaCMS.ScrapePlugins.M.YoMangaLoader.Loader,
	MangaCMS.ScrapePlugins.M.ZenonLoader.ContentLoader,
	MangaCMS.ScrapePlugins.M.ZenonLoader.FeedLoader,
]

def go():
	print(MangaCMS.cleaner.processDownload)
	for code_file in files:
		# print(code_file)
		classes = inspect.getmembers(code_file, inspect.isclass)
		for class_name, class_def in classes:
			# print(class_def)
			if issubclass(class_def, MangaCMS.DbBase.DbBase):
				print("class:", class_def)
				instance = class_def()
				cur = instance.get_cursor()
				instance.release_cursor(cur)

if __name__ == '__main__':
	go()
