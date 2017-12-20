
import inspect
import logSetup
logSetup.initLogging()

import DbBase

import ScrapePlugins.H.ASMHentaiLoader.ContentLoader
import ScrapePlugins.H.ASMHentaiLoader.DbLoader
import ScrapePlugins.H.DjMoeLoader.ContentLoader
import ScrapePlugins.H.DjMoeLoader.DbLoader
import ScrapePlugins.H.DoujinOnlineLoader.ContentLoader
import ScrapePlugins.H.DoujinOnlineLoader.DbLoader
import ScrapePlugins.H.HBrowseLoader.ContentLoader
import ScrapePlugins.H.HBrowseLoader.DbLoader
import ScrapePlugins.H.Hentai2Read.ContentLoader
import ScrapePlugins.H.Hentai2Read.DbLoader
import ScrapePlugins.H.HitomiLoader.ContentLoader
import ScrapePlugins.H.HitomiLoader.DbLoader
import ScrapePlugins.H.NHentaiLoader.ContentLoader
import ScrapePlugins.H.NHentaiLoader.DbLoader
import ScrapePlugins.H.PururinLoader.ContentLoader
import ScrapePlugins.H.PururinLoader.DbLoader
import ScrapePlugins.H.SadPandaLoader.ContentLoader
import ScrapePlugins.H.SadPandaLoader.DbLoader
import ScrapePlugins.H.TsuminoLoader.ContentLoader
import ScrapePlugins.H.TsuminoLoader.DbLoader
import ScrapePlugins.M.BooksMadokami.ContentLoader
import ScrapePlugins.M.BooksMadokami.DbLoader
import ScrapePlugins.M.BtLoader.ContentLoader
import ScrapePlugins.M.BtLoader.DbLoader
import ScrapePlugins.M.BtSeriesFetcher.SeriesLoader
import ScrapePlugins.M.Crunchyroll.ContentLoader
import ScrapePlugins.M.Crunchyroll.DbLoader
import ScrapePlugins.M.CxLoader.contentLoader
import ScrapePlugins.M.CxLoader.dbLoader
import ScrapePlugins.M.DynastyLoader.ContentLoader
import ScrapePlugins.M.DynastyLoader.FeedLoader
import ScrapePlugins.M.FoolSlide.VortexLoader.ContentLoader
import ScrapePlugins.M.FoolSlide.VortexLoader.FeedLoader
import ScrapePlugins.M.GameOfScanlationLoader.ContentLoader
import ScrapePlugins.M.GameOfScanlationLoader.FeedLoader
import ScrapePlugins.M.Kawaii.ContentLoader
import ScrapePlugins.M.Kawaii.FeedLoader
import ScrapePlugins.M.KissLoader.ContentLoader
import ScrapePlugins.M.KissLoader.FeedLoader
import ScrapePlugins.M.MangaBox.Loader
import ScrapePlugins.M.MangaHere.ContentLoader
import ScrapePlugins.M.MangaHere.FeedLoader
import ScrapePlugins.M.MangaMadokami.ContentLoader
import ScrapePlugins.M.MangaMadokami.FeedLoader
import ScrapePlugins.M.MangaStreamLoader.ContentLoader
import ScrapePlugins.M.MangaStreamLoader.FeedLoader
import ScrapePlugins.M.McLoader.ContentLoader
import ScrapePlugins.M.McLoader.FeedLoader
import ScrapePlugins.M.MerakiScans.ContentLoader
import ScrapePlugins.M.MerakiScans.FeedLoader
import ScrapePlugins.M.SurasPlace.ContentLoader
import ScrapePlugins.M.SurasPlace.FeedLoader
import ScrapePlugins.M.WebtoonLoader.ContentLoader
import ScrapePlugins.M.WebtoonLoader.FeedLoader
import ScrapePlugins.M.WebtoonsReader.ContentLoader
import ScrapePlugins.M.WebtoonsReader.FeedLoader
import ScrapePlugins.M.YoMangaLoader.Loader
import ScrapePlugins.M.ZenonLoader.ContentLoader
import ScrapePlugins.M.ZenonLoader.FeedLoader

files = [
	ScrapePlugins.H.ASMHentaiLoader.ContentLoader,
	ScrapePlugins.H.ASMHentaiLoader.DbLoader,
	ScrapePlugins.H.DjMoeLoader.ContentLoader,
	ScrapePlugins.H.DjMoeLoader.DbLoader,
	ScrapePlugins.H.DoujinOnlineLoader.ContentLoader,
	ScrapePlugins.H.DoujinOnlineLoader.DbLoader,
	ScrapePlugins.H.HBrowseLoader.ContentLoader,
	ScrapePlugins.H.HBrowseLoader.DbLoader,
	ScrapePlugins.H.Hentai2Read.ContentLoader,
	ScrapePlugins.H.Hentai2Read.DbLoader,
	ScrapePlugins.H.HitomiLoader.ContentLoader,
	ScrapePlugins.H.HitomiLoader.DbLoader,
	ScrapePlugins.H.NHentaiLoader.ContentLoader,
	ScrapePlugins.H.NHentaiLoader.DbLoader,
	ScrapePlugins.H.PururinLoader.ContentLoader,
	ScrapePlugins.H.PururinLoader.DbLoader,
	ScrapePlugins.H.SadPandaLoader.ContentLoader,
	ScrapePlugins.H.SadPandaLoader.DbLoader,
	ScrapePlugins.H.TsuminoLoader.ContentLoader,
	ScrapePlugins.H.TsuminoLoader.DbLoader,
	ScrapePlugins.M.BooksMadokami.ContentLoader,
	ScrapePlugins.M.BooksMadokami.DbLoader,
	ScrapePlugins.M.BtLoader.ContentLoader,
	ScrapePlugins.M.BtLoader.DbLoader,
	ScrapePlugins.M.BtSeriesFetcher.SeriesLoader,
	ScrapePlugins.M.Crunchyroll.ContentLoader,
	ScrapePlugins.M.Crunchyroll.DbLoader,
	ScrapePlugins.M.CxLoader.contentLoader,
	ScrapePlugins.M.CxLoader.dbLoader,
	ScrapePlugins.M.DynastyLoader.ContentLoader,
	ScrapePlugins.M.DynastyLoader.FeedLoader,
	ScrapePlugins.M.FoolSlide.VortexLoader.ContentLoader,
	ScrapePlugins.M.FoolSlide.VortexLoader.FeedLoader,
	ScrapePlugins.M.GameOfScanlationLoader.ContentLoader,
	ScrapePlugins.M.GameOfScanlationLoader.FeedLoader,
	ScrapePlugins.M.Kawaii.ContentLoader,
	ScrapePlugins.M.Kawaii.FeedLoader,
	ScrapePlugins.M.KissLoader.ContentLoader,
	ScrapePlugins.M.KissLoader.FeedLoader,
	ScrapePlugins.M.MangaBox.Loader,
	ScrapePlugins.M.MangaHere.ContentLoader,
	ScrapePlugins.M.MangaHere.FeedLoader,
	ScrapePlugins.M.MangaMadokami.ContentLoader,
	ScrapePlugins.M.MangaMadokami.FeedLoader,
	ScrapePlugins.M.MangaStreamLoader.ContentLoader,
	ScrapePlugins.M.MangaStreamLoader.FeedLoader,
	ScrapePlugins.M.McLoader.ContentLoader,
	ScrapePlugins.M.McLoader.FeedLoader,
	ScrapePlugins.M.MerakiScans.ContentLoader,
	ScrapePlugins.M.MerakiScans.FeedLoader,
	ScrapePlugins.M.SurasPlace.ContentLoader,
	ScrapePlugins.M.SurasPlace.FeedLoader,
	ScrapePlugins.M.WebtoonLoader.ContentLoader,
	ScrapePlugins.M.WebtoonLoader.FeedLoader,
	ScrapePlugins.M.WebtoonsReader.ContentLoader,
	ScrapePlugins.M.WebtoonsReader.FeedLoader,
	ScrapePlugins.M.YoMangaLoader.Loader,
	ScrapePlugins.M.ZenonLoader.ContentLoader,
	ScrapePlugins.M.ZenonLoader.FeedLoader,
]

def go():
	for code_file in files:
		# print(code_file)
		classes = inspect.getmembers(code_file, inspect.isclass)
		for class_name, class_def in classes:
			# print(class_def)
			if issubclass(class_def, DbBase.DbBase):
				print("class:", class_def)
				instance = class_def()


if __name__ == '__main__':
	go()
