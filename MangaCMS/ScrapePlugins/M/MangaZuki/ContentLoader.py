

import MangaCMS.lib.logSetup
import runStatus
if __name__ == "__main__":
	runStatus.preloadDicts = False


import settings
import os
import os.path

import nameTools as nt

import time

import urllib.parse
import html.parser
import zipfile
import traceback
import bs4
import re
import json
import MangaCMS.ScrapePlugins.RetreivalBase


import MangaCMS.cleaner.processDownload

class ContentLoader(MangaCMS.ScrapePlugins.RetreivalBase.RetreivalBase):

	loggerPath = "Main.Manga.Mzk.Cl"
	pluginName = "MangaZuki Content Retreiver"
	tableKey = "mzk"
	tableName = "MangaItems"


	retreivalThreads = 1



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


			file_contents, name_from_source = self.wg.getFileAndName(link['sourceUrl'], addlHeaders={'Referer': 'https://mangazuki.co/'})


			if name_from_source.endswith(".zip"):
				name_from_source = name_from_source[:-4]
			fname = "{} - {}[MangaZuki].zip".format(chapterName, name_from_source)

			fqFName = os.path.join(dlPath, fname)

			loop = 1
			prefix, ext = os.path.splitext(fqFName)
			while os.path.exists(fqFName):
				fqFName = "%s (%d)%s" % (prefix, loop,  ext)
				loop += 1
			self.log.info("Saving to archive = %s", fqFName)

			with open(fqFName, "wb") as fp:
				fp.write(file_contents)

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
		# cl.proceduralGetImages('http://www.MangaZuki.co/manga/totsugami/v05/c030/')
		# cl.getLink({'seriesName': 'Totsugami', 'originName': 'Totsugami 32 - Vol 05', 'retreivalTime': 1414512000.0, 'dlState': 0, 'sourceUrl': 'http://www.MangaZuki.co/manga/totsugami/v05/c032/', 'flags':None})

		# inMarkup = cl.wg.getpage(pg)
		# cl.getImageUrls(inMarkup, pg)
		cl.do_fetch_content()


