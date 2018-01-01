
# -*- coding: utf-8 -*-

import os
import re
import os.path

import zipfile
import nameTools as nt

import urllib.request, urllib.parse, urllib.error
import traceback

import urllib
import json
import ast
import settings
import bs4
import MangaCMS.cleaner.processDownload
import MangaCMS.ScrapePlugins.RetreivalBase

import MangaCMS.ScrapePlugins.ScrapeExceptions as ScrapeExceptions

class ContentLoader(MangaCMS.ScrapePlugins.RetreivalBase.RetreivalBase):



	dbName = settings.DATABASE_DB_NAME
	loggerPath = "Main.Manga.Hentai2Read.Cl"
	pluginName = "Hentai2Read Content Retreiver"
	tableKey   = "h2r"
	urlBase    = "https://hentai2read.com/"


	tableName = "HentaiItems"

	retreivalThreads = 2

	itemLimit = 1000
	# itemLimit = 1

	shouldCanonize = False

	def getFileName(self, soup):
		title = soup.find("h1", class_="otitle")
		if not title:
			raise ValueError("Could not find title. Wat?")
		return title.get_text()


	def build_links(self, pageurl, root_url, item_meta):
		ret = []

		for imgurl in item_meta['images']:
			imgurl = imgurl.replace("\\", "")
			imgurl = urllib.parse.urljoin(root_url, "/hentai" + imgurl)

			ret.append((imgurl, pageurl))

		return ret

	def getDownloadInfo(self, linkDict):

		self.log.info("Retreiving item: %s", linkDict["sourceUrl"])

		try:
			soup = self.wg.getSoup(linkDict["sourceUrl"], addlHeaders={'Referer': self.urlBase})
		except:
			self.log.critical("No download at url %s! SourceUrl = %s", linkDict["sourceUrl"], linkDict["sourceUrl"])
			raise IOError("Invalid webpage")


		linkDict['dirPath'] = os.path.join(settings.asmhSettings["dlDir"], linkDict['seriesName'])

		if not os.path.exists(linkDict["dirPath"]):
			os.makedirs(linkDict["dirPath"], exist_ok=True)
		else:
			self.log.info("Folder Path already exists?: %s", linkDict["dirPath"])


		self.log.info("Folderpath: %s", linkDict["dirPath"])
		#self.log.info(os.path.join())


		scripts = soup.find_all("script")

		iteminfo = None
		for script in scripts:
			scriptt = script.get_text(strip=True)
			if 'var gData' in scriptt:
				scriptt = scriptt.replace("var gData = ", "").strip(";")
				iteminfo = ast.literal_eval(scriptt)

		if not iteminfo:
			raise IOError("Failed to extract item information")

		first_img_url = soup.find("img", id='arf-reader')

		imageUrls = self.build_links(linkDict["sourceUrl"], first_img_url["src"], iteminfo)

		self.log.info("Found %s image urls!", len(imageUrls))

		linkDict["dlLinks"] = imageUrls

		self.log.debug("Linkdict = ")
		for key, value in list(linkDict.items()):
			self.log.debug("		%s - %s", key, value)

		return linkDict

	def getImage(self, imageUrl, referrer):

		content, handle = self.wg.getpage(imageUrl, returnMultiple=True)
		if not content or not handle:
			raise ValueError("Failed to retreive image from page '%s'!" % referrer)

		fileN = urllib.parse.unquote(urllib.parse.urlparse(handle.geturl())[2].split("/")[-1])
		fileN = bs4.UnicodeDammit(fileN).unicode_markup
		self.log.info("retreived image '%s' with a size of %0.3f K", fileN, len(content)/1000.0)
		return fileN, content



	def fetchImages(self, linkDict):

		images = []
		for imgurl, referrerurl in linkDict["dlLinks"]:
			images.append(self.getImage(imgurl, referrerurl))

		return images



	def doDownload(self, linkDict, link):

		images = self.fetchImages(linkDict)


		# self.log.info(len(content))

		if images:
			fileN = linkDict['originName']+".zip"
			fileN = nt.makeFilenameSafe(fileN)


			# self.log.info("geturl with processing", fileN)
			wholePath = os.path.join(linkDict["dirPath"], fileN)
			self.log.info("Complete filepath: %s", wholePath)

					#Write all downloaded files to the archive.


			chop = len(fileN)-4
			wholePath = "ERROR"
			while 1:

				try:
					fileN = fileN[:chop]+fileN[-4:]
					# self.log.info("geturl with processing", fileN)
					wholePath = os.path.join(linkDict["dirPath"], fileN)
					wholePath = self.insertCountIfFilenameExists(wholePath)
					self.log.info("Complete filepath: %s", wholePath)

					#Write all downloaded files to the archive.

					arch = zipfile.ZipFile(wholePath, "w")
					for imageName, imageContent in images:
						arch.writestr(imageName, imageContent)
					arch.close()

					self.log.info("Successfully Saved to path: %s", wholePath)
					break
				except IOError:
					chop = chop - 1
					self.log.warn("Truncating file length to %s characters.", chop)


			if not linkDict["tags"]:
				linkDict["tags"] = ""



			self.updateDbEntry(linkDict["sourceUrl"], downloadPath=linkDict["dirPath"], fileName=fileN)


			# Deduper uses the path info for relinking, so we have to dedup the item after updating the downloadPath and fileN
			dedupState = MangaCMS.cleaner.processDownload.processDownload(linkDict["seriesName"], wholePath, pron=True, rowId=link['dbId'])
			self.log.info( "Done")

			if dedupState:
				self.addTags(sourceUrl=linkDict["sourceUrl"], tags=dedupState)


			self.updateDbEntry(linkDict["sourceUrl"], dlState=2)

			return wholePath

		else:

			self.updateDbEntry(linkDict["sourceUrl"], dlState=-1, downloadPath="ERROR", fileName="ERROR: FAILED")

			return False


	def getLink(self, link):
		try:
			self.updateDbEntry(link["sourceUrl"], dlState=1)
			linkInfo = self.getDownloadInfo(link)
			self.doDownload(linkInfo, link)
		except urllib.error.URLError:
			self.log.error("Failure retreiving content for link %s", link)
			for line in traceback.format_exc().split("\n"):
				self.log.error("	%s", line)
			self.updateDbEntry(link["sourceUrl"], dlState=-1, downloadPath="ERROR", fileName="ERROR: FAILED")
		except IOError:
			self.log.error("Failure retreiving content for link %s", link)
			for line in traceback.format_exc().split("\n"):
				self.log.error("	%s", line)
			self.updateDbEntry(link["sourceUrl"], dlState=-2, downloadPath="ERROR", fileName="ERROR: MISSING")

if __name__ == "__main__":
	import utilities.testBase as tb

	# with tb.testSetup():
	with tb.testSetup(load=False):

		run = ContentLoader()

		# run.retreivalThreads = 1
		# run._resetStuckItems()
		run.do_fetch_content()
		# test = {
		# 	'sourceUrl'  : 'https://asmhentai.com/g/178575/',
		# 	'seriesName' : 'Doujins',
		# }
		# run.getDownloadInfo(test)



