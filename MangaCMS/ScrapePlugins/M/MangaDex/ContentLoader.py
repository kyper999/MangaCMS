


import os
import os.path
import sys

import nameTools as nt

import ast
import time

import urllib.parse
import pprint
import traceback
import bs4
import re
import json
import MangaCMS.ScrapePlugins.RetreivalBase

from concurrent.futures import ThreadPoolExecutor

import MangaCMS.lib.logSetup
import MangaCMS.cleaner.processDownload

class ContentLoader(MangaCMS.ScrapePlugins.RetreivalBase.RetreivalBase):

	loggerPath = "Main.Manga.MDx.Cl"
	pluginName = "MangaDex Content Retreiver"
	tableKey = "mdx"
	tableName = "MangaItems"


	retreivalThreads = 4
	urlBase    = "https://mangadex.com/"



	def getImageUrls(self, chapUrl):
		soup = self.wg.getSoup(chapUrl)


		js_segments = soup.find_all("script", type="text/javascript")

		# print(js_segments)
		literal_regex = re.compile(r'(?<=var)(.+?)(?=;)', re.DOTALL)


		js_vars = {}
		for js_segment in js_segments:
			matches = literal_regex.findall(str(js_segment))
			for match in matches:
				key, val = match.split("=", 1)
				key = key.strip()
				val = val.strip()
				try:
					js_vars[key] = ast.literal_eval(val)
				except Exception as e:
					# print("Wat", val, e)
					pass

		expect_keys = ['page_array', 'server', 'dataurl']
		if not all([key in js_vars for key in expect_keys]):
			self.log.error("Missing content variables from manga page: '%s'", chapUrl)
			return []

		image_urls = []
		for img_file in js_vars['page_array']:
			img_url = js_vars['server'] + js_vars['dataurl'] + "/" + img_file
			img_url = urllib.parse.urljoin(self.urlBase, img_url)
			image_urls.append((img_url, chapUrl))


		self.log.info("Found %s images", len(image_urls))

		return image_urls



	def getImages(self, link):

		imageUrls = self.getImageUrls(link)

		images = []

		image_counter = 1
		for imgUrl, referrerUrl in imageUrls:
			imageContent, imageName = self.wg.getFileAndName(imgUrl, addlHeaders={'Referer': referrerUrl})
			img_postf = urllib.parse.urlsplit(imgUrl).path.split("/")[-1]
			imageName = "{:04d} - {} {}".format(image_counter, imageName, img_postf)
			self.log.info("Found %s byte image named %s", len(imageContent), imageName)
			images.append([imageName, imageContent])
			image_counter += 1
		return images


	def getLink(self, link):

		sourceUrl  = link["sourceUrl"]
		seriesName = link['seriesName']

		try:
			self.log.info( "Should retreive url - %s", sourceUrl)
			self.updateDbEntry(sourceUrl, dlState=1)

			seriesName = nt.getCanonicalMangaUpdatesName(seriesName)

			self.log.info("Downloading = '%s', '%s'", seriesName, link["originName"])
			dlPath, newDir = self.locateOrCreateDirectoryForSeries(seriesName)

			if link["flags"] == None:
				link["flags"] = ""

			if newDir:
				self.updateDbEntry(sourceUrl, flags=" ".join([link["flags"], "haddir"]))

			chapterName = nt.makeFilenameSafe(link["originName"])

			fqFName = os.path.join(dlPath, chapterName+".zip")

			loop = 1
			prefix, ext = os.path.splitext(fqFName)
			while os.path.exists(fqFName):
				fqFName = "%s (%d)%s" % (prefix, loop,  ext)
				loop += 1
			self.log.info("Saving to archive = %s", fqFName)

			images = self.getImages(sourceUrl)

			self.log.info("Creating archive with %s images", len(images))

			if not images:
				self.updateDbEntry(sourceUrl, dlState=-1, tags="error-404")
				return

			fqFName = self.save_image_set(fqFName, images)

			dedupState = MangaCMS.cleaner.processDownload.processDownload(seriesName, fqFName, deleteDups=True, includePHash=True, rowId=link['dbId'])
			self.log.info( "Done")

			filePath, fileName = os.path.split(fqFName)
			self.updateDbEntry(sourceUrl, dlState=2, downloadPath=filePath, fileName=fileName, tags=dedupState)
			return

		except Exception:
			self.log.critical("Failure on retrieving content at %s", sourceUrl)
			self.log.critical("Traceback = %s", traceback.format_exc())
			self.updateDbEntry(sourceUrl, dlState=-1)
			raise

if __name__ == '__main__':
	import utilities.testBase as tb

	# with tb.testSetup():
	with tb.testSetup():
		cl = ContentLoader()
		# cl.proceduralGetImages('http://www.MangaDex.co/manga/totsugami/v05/c030/')
		# cl.getLink(
		# 		{
		# 		    'originName': 'D-Frag! - Ch. 69 Thank you very much! [MangaDex, Hot Chocolate Scans]',
		# 		    'downloadPath': None,
		# 		    'sourceUrl': 'https://mangadex.com/chapter/19083',
		# 		    'sourceId': None,
		# 		    # 'retreivalTime': time.struct_time(tm_year = 2018, tm_mon = 1, tm_mday = 28, tm_hour = 5, tm_min = 29, tm_sec = 31, tm_wday = 6, tm_yday = 28, tm_isdst = 0),
		# 		    'dbId': 2943680,
		# 		    'flags': None,
		# 		    'tags': None,
		# 		    'lastUpdate': 0.0,
		# 		    'note': None,
		# 		    'seriesName': 'D-Frag!',
		# 		    'dlState': 0,
		# 		    'fileName': None
		# 		}
		# 	)
		# cl.getLink(
		# 		{
		# 		    'originName': "Mousou Telepathy - Ch. 166 That's Where He's Different [MangaDex, Helvetica Scans]",
		# 		    'downloadPath': None,
		# 		    'sourceUrl': 'https://mangadex.com/chapter/19131',
		# 		    'sourceId': None,
		# 		    # 'retreivalTime': time.struct_time(tm_year = 2018, tm_mon = 1, tm_mday = 28, tm_hour = 5, tm_min = 48, tm_sec = 7, tm_wday = 6, tm_yday = 28, tm_isdst = 0),
		# 		    'dbId': 2943321,
		# 		    'flags': None,
		# 		    'tags': None,
		# 		    'lastUpdate': 0.0,
		# 		    'note': None,
		# 		    'seriesName': 'Mousou Telepathy',
		# 		    'dlState': 0,
		# 		    'fileName': None
		# 		}
		# 	)
		# cl.getLink(
		# 		{
		# 		    'sourceUrl': 'https://mangadex.com/chapter/19151',
		# 		    'lastUpdate': 0.0,
		# 		    'dbId': 2943493,
		# 		    # 'retreivalTime': time.struct_time(tm_year = 2018, tm_mon = 1, tm_mday = 28, tm_hour = 6, tm_min = 25, tm_sec = 24, tm_wday = 6, tm_yday = 28, tm_isdst = 0),
		# 		    'note': None,
		# 		    'sourceId': None,
		# 		    'flags': None,
		# 		    'seriesName': 'Yakumo-san wa Edzuke ga Shitai.',
		# 		    'fileName': None,
		# 		    'dlState': 0,
		# 		    'tags': None,
		# 		    'originName': "Yakumo-san wa Edzuke ga Shitai. - Vol. 5 Ch. 29 Yamato's Answer [MangaDex, /a/nonymous]",
		# 		    'downloadPath': None
		# 		}
		# 	)

		# inMarkup = cl.wg.getpage(pg)
		# cl.getImageUrls(inMarkup, pg)
		cl.do_fetch_content()


