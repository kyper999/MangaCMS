
# -*- coding: utf-8 -*-

import webFunctions
import os
import os.path

import random
import sys

import nameTools as nt

import runStatus
import time
import urllib.request, urllib.parse, urllib.error
import traceback

import settings
import bs4
import logging

import processDownload
import ScrapePlugins.RetreivalBase

class UnwantedContentError(RuntimeError):
	pass
class PageContentError(RuntimeError):
	pass

class ContentLoader(ScrapePlugins.RetreivalBase.RetreivalBase):
	log = logging.getLogger("Main.Manga.DjM.Cl")


	dbName = settings.DATABASE_DB_NAME
	loggerPath = "Main.Manga.DjM.Cl"
	pluginName = "DjMoe Content Retreiver"
	tableKey   = "djm"
	urlBase = "http://doujins.com/"

	wg = webFunctions.WebGetRobust(logPath=loggerPath+".Web")
	tableName = "HentaiItems"

	shouldCanonize = False


	def getDirAndFName(self, soup):
		title = soup.find("div", class_="folder-title")
		if not title:
			raise ValueError("Could not find title. Wat?")
		titleSplit = title.get_text().split("»")
		safePath = [nt.makeFilenameSafe(item.strip()) for item in titleSplit]
		fqPath = os.path.join(settings.djSettings["dlDir"], *safePath)
		dirPath, fName = fqPath.rsplit("/", 1)
		self.log.info("dirPath = %s", dirPath)
		self.log.info("fName = %s", fName)
		return dirPath, fName, titleSplit[-1].strip()

	def getDownloadInfo(self, linkDict):

		content_id = linkDict["sourceUrl"]
		self.log.info("Retreiving metadata for item: %s", content_id)


		if not content_id.startswith("http"):
			sourcePage = urllib.parse.urljoin(self.urlBase, "/gallery/{gid}".format(gid=content_id))
		else:
			sourcePage = content_id

		soup = self.wg.getSoup(sourcePage)
		if not soup:
			self.log.critical("No download at url %s! SourceUrl = %s", sourcePage, content_id)
			raise PageContentError()

		try:
			linkDict["dirPath"], linkDict["originName"], linkDict["seriesName"] = self.getDirAndFName(soup)
		except AttributeError:
			self.log.critical("No download at url %s! SourceUrl = %s", sourcePage, content_id)
			raise PageContentError()

		except ValueError:
			self.log.critical("No download at url %s! SourceUrl = %s", sourcePage, content_id)
			raise PageContentError()

		image_container = soup.find("div", id='image-container')

		ret_link_list = []
		for img_tag in image_container.find_all("img"):
			ret_link_list.append((img_tag['data-file'], sourcePage))

		note = soup.find("div", class_="message")
		if note is None or note.string is None:
			linkDict["note"] = " "
		else:
			linkDict["note"] = nt.makeFilenameSafe(note.string)

		tags = soup.find("li", class_="tag-area")
		if tags:
			tagList = []
			for tag in tags.find_all("a"):
				tagStr = tag.get_text()
				tagList.append(tagStr.lower().rstrip(", ").lstrip(", ").replace(" ", "-"))
		else:
			tagList = []

		artist_area = soup.find('div', class_='gallery-artist')
		aList = []
		for artist_link in artist_area.find_all("a"):
			a_tag = artist_link.get_text(strip=True)
			aList.append(a_tag)
			a_tag = "artist " + a_tag
			tagList.append(a_tag.lower().rstrip(", ").lstrip(", ").replace(" ", "-"))

		linkDict['artist'] = ",".join(aList)
		tagStr = ' '.join(tagList)

		for skipTag in settings.skipTags:
			if skipTag in tagStr:
				errtxt = "Skipped tag '%s' in tags '%s'. Do not want." % (skipTag, tagStr)
				self.log.info(errtxt)
				raise UnwantedContentError(errtxt)

		linkDict["tags"] = tagStr

		if not os.path.exists(linkDict["dirPath"]):
			os.makedirs(linkDict["dirPath"])
		else:
			self.log.info("Folder Path already exists?: %s", linkDict["dirPath"])


		self.log.info("Folderpath: %s", linkDict["dirPath"])
		#self.log.info(os.path.join())

		self.log.debug("Linkdict = ")
		for key, value in list(linkDict.items()):
			self.log.debug("		%s - %s", key, value)


		if "tags" in linkDict and "note" in linkDict:
			self.updateDbEntry(content_id, tags=linkDict["tags"], note=linkDict["note"], lastUpdate=time.time())

		return ret_link_list


	def getImage(self, imageUrl, referrer):

		content, handle = self.wg.getpage(imageUrl, returnMultiple=True, addlHeaders={'Referer': referrer})
		if not content or not handle:
			raise ValueError("Failed to retreive image from page '%s'!" % referrer)

		fileN = urllib.parse.unquote(urllib.parse.urlparse(handle.geturl())[2].split("/")[-1])
		fileN = bs4.UnicodeDammit(fileN).unicode_markup
		self.log.info("retreived image '%s' with a size of %0.3f K", fileN, len(content)/1000.0)
		return fileN, content

	def getImages(self, imageurls):

		images = []

		for imageurl, referrer in imageurls:
			images.append(self.getImage(imageurl, referrer))

		return images


	def getLink(self, link):

		try:
			self.updateDbEntry(link["sourceUrl"], dlState=1)
			image_url_list = self.getDownloadInfo(link)

			images = self.getImages(image_url_list)
			title  = link['seriesName']
			artist = link['artist']

		except webFunctions.ContentError:
			self.updateDbEntry(link["sourceUrl"], dlState=-2, downloadPath="ERROR", fileName="ERROR: FAILED")
			return False
		except UnwantedContentError:
			self.updateDbEntry(link["sourceUrl"], dlState=-3, downloadPath="ERROR", fileName="ERROR: Unwanted Tags applied to series!")
			return False
		except PageContentError:
			self.updateDbEntry(link["sourceUrl"], dlState=-3, downloadPath="ERROR", fileName="ERROR: FAILED (PageContentError)")
			return False

		if images and title:
			fileN = title+" "+artist+".zip"
			fileN = nt.makeFilenameSafe(fileN)
			wholePath = os.path.join(link["dirPath"], fileN)

			wholePath = self.save_image_set(wholePath, images)

			self.updateDbEntry(link["sourceUrl"], downloadPath=link["dirPath"], fileName=fileN)

			# Deduper uses the path info for relinking, so we have to dedup the item after updating the downloadPath and fileN
			dedupState = processDownload.processDownload(None, wholePath, pron=True, deleteDups=True, includePHash=True, rowId=link['dbId'])
			self.log.info( "Done")

			if dedupState:
				self.addTags(sourceUrl=link["sourceUrl"], tags=dedupState)

			self.updateDbEntry(link["sourceUrl"], dlState=2)

			delay = random.randint(5, 30)
			self.log.info("Sleeping %s", delay)
			time.sleep(delay)



if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):

		# run = HBrowseRetagger()
		run = ContentLoader()
		run.do_fetch_content()


