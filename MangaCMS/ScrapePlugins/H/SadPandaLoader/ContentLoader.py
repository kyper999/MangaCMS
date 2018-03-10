
# -*- coding: utf-8 -*-

import os
import os.path
import time
import re
import nameTools as nt
import runStatus
import urllib.request, urllib.parse, urllib.error
import traceback

import WebRequest

import settings
import random
random.seed()

from . import LoginMixin
import MangaCMS.cleaner.processDownload
import MangaCMS.ScrapePlugins.RetreivalBase

class ContentLoader(MangaCMS.ScrapePlugins.RetreivalBase.RetreivalBase, LoginMixin.ExLoginMixin):



	logger_path = "Main.Manga.SadPanda.Cl"
	plugin_name = "SadPanda Content Retreiver"
	plugin_key  = "sp"
	is_manga    = False

	urlBase = "http://exhentai.org/"

	retreivalThreads = 1

	shouldCanonize = False
	outOfCredits   = False


	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)

	def setup(self):
		self.checkLogin()
		if not self.checkExAccess():
			raise ValueError("Cannot access ex! Wat?")

	def getTags(self, inSoup):

		tagDiv = inSoup.find('div', id='taglist')

		formatters = {
						'character:'   : 'character',
						'parody:'      : "parody",
						'artist:'      : "artist",
						'group:'       : "group",
					}

		tagList = []
		for row in tagDiv.find_all("tr"):
			tagType, tags = row.find_all("td")

			tagType = tagType.get_text().strip()
			if tagType in formatters:
				prefix = formatters[tagType]
			else:
				prefix = ''

			for tag in tags.find_all('div'):
				tag = '%s %s' % (prefix, tag.get_text())
				while tag.find("  ") + 1:
					tag = tag.replace("  ", " ")
				tag = tag.strip()
				tag = tag.replace(" ", "-")
				tagList.append(tag.lower())


		for tag in settings.sadPanda['sadPandaExcludeTags']:
			if tag in tagList:
				self.log.info("Blocked item! Deleting row from database.")
				self.log.info("Item tags = '%s'", tagList)
				self.log.info("Blocked tag = '%s'", tag)
				return False

		# We sometimes want to do compound blocks.
		# For example, if something is tagged 'translated', but not 'english', it's
		# probably not english, but not the original item either (assuming you want
		# either original items, or the english tranlsation).
		# Therefore, if settings.sadPanda['excludeCompoundTags'][n][0] is in the taglist,
		# and not settings.sadPanda['excludeCompoundTags'][n][1], we skip the item.
		for exclude, when in settings.sadPanda['excludeCompoundTags']:
			if exclude in tagList:
				if when not in tagList:
					self.log.info("Blocked item! Deleting row from database.")
					self.log.info("Item tags = '%s'", tagList)
					self.log.info("Triggering tags: = '%s', '%s'", exclude, when)
					return False

		if not any([tmp in tagList for tmp in settings.tagHighlight]):
			self.log.info("Missing any highlighted tag. Not fetching!")
			self.log.info("Item tags = '%s'", tagList)
			return False

		self.log.info("Adding tags: '%s'", tagList)
		return tagList


	def getDownloadPageUrl(self, inSoup):
		dlA = inSoup.find('a', onclick=re.compile('archiver.php'))

		clickAction = dlA['onclick']
		clickUrl = re.search("(https?://exhentai.org/archiver.php.*)'", clickAction)
		return clickUrl.group(1)


	def getDownloadInfo(self, link_row_id):

		with self.row_context(dbid=link_row_id) as row:
			source_url = row.source_id
			row.state = 'fetching'

		self.log.info("Retrieving item: %s", source_url)

		try:
			soup = self.wg.getSoup(source_url, addlHeaders={'Referer': self.urlBase})

		except Exception as e:
			self.log.critical("No download at url %s! SourceUrl = %s", source_url)
			for line in traceback.format_exc().split("\n"):
				self.log.critical(""+line)

			raise IOError("Invalid webpage")

		if "This gallery has been removed, and is unavailable." in soup.get_text():
			self.log.info("Gallery deleted. Removing.")
			with self.row_sess_context(dbid=link_row_id) as row_tup:
				row, sess = row_tup
				sess.delete(row)
			return False

		item_tags = self.getTags(soup)
		if not item_tags:
			with self.row_sess_context(dbid=link_row_id) as row_tup:
				row, sess = row_tup
				sess.delete(row)
			return False

		# self.addTags(sourceUrl=sourceUrl, tags=tags)
		# return True

		ret = {
			'dlPage'    :  self.getDownloadPageUrl(soup),
			'item_tags' : item_tags,
		}



		return ret

	def getDownloadUrl(self, dlPageUrl, referrer):

		soup = self.wg.getSoup(dlPageUrl, addlHeaders={'Referer': referrer})

		if 'Insufficient funds'.lower() in str(soup).lower():
			self.outOfCredits = True
			raise ValueError("Out of credits. Cannot download!")

		if 'Download Cost:' in soup.get_text():
			self.log.info("Accepting download.")
			acceptForm = soup.find('form')
			formPostUrl = acceptForm['action']
			soup = self.wg.getSoup(formPostUrl, addlHeaders={'Referer': referrer}, postData={'dlcheck': 'Download Original Archive', 'dltype' : 'org'})
		else:
			self.log.warn("Already accepted download?")



		contLink = soup.find('p', id='continue')
		if not contLink:
			self.log.error("No link found!")
			self.log.error("Page Contents: '%s'", soup)


		downloadUrl = contLink.a['href']+"?start=1"

		return downloadUrl

	def doDownload(self, link_info, link_row_id):


		# linkDict['dirPath'] = os.path.join(settings.sadPanda["dlDir"], linkDict['seriesName'])

		# if not os.path.exists(linkDict["dirPath"]):
		# 	os.makedirs(linkDict["dirPath"])

		# self.log.info("Folderpath: %s", linkDict["dirPath"])

		with self.row_context(dbid=link_row_id) as row:
			source_url  = row.source_id
			origin_name = row.origin_name
			series_name = row.series_name

		downloadUrl = self.getDownloadUrl(link_info['dlPage'], source_url)


		if not downloadUrl:
			with self.row_context(dbid=link_row_id) as row:
				row.state = 'error'
			return False



		fCont, fName = self.wg.getFileAndName(downloadUrl)


		# self.log.info(len(content))
		if origin_name in fName:
			fileN = fName
		else:
			fileN = '%s - %s.zip' % (origin_name, fName)
			fileN = fileN.replace('.zip .zip', '.zip')


		fileN = nt.makeFilenameSafe(fileN)
		fqFName = os.path.join(settings.sadPanda["dlDir"], series_name, fileN)


		# This call also inserts the file parameters into the row
		with self.row_sess_context(dbid=link_row_id) as row_tup:
			row, sess = row_tup
			fqFName = self.save_archive(row, sess, fqFName, fCont)

		#self.log.info( filePath)

		with self.row_context(dbid=link_row_id) as row:
			row.state = 'processing'

		# We don't want to upload the file we just downloaded, so specify doUpload as false.
		# As a result of this, the seriesName paramerer also no longer matters
		MangaCMS.cleaner.processDownload.processDownload(seriesName=False, archivePath=fqFName, doUpload=False)


		self.log.info( "Done")
		with self.row_context(dbid=link_row_id) as row:
			row.state = 'complete'

		return True


	def get_link(self, link_row_id):


		if self.outOfCredits:
			self.log.warn("Out of credits. Skipping!")
			return False
		try:

			link_info = self.getDownloadInfo(link_row_id)
			if link_info:
				self.doDownload(link_info=link_info, link_row_id=link_row_id)

				sleeptime = random.randint(10,60*5)
			else:
				sleeptime = 5

			self.log.info("Sleeping %s seconds.", sleeptime)
			for dummy_x in range(sleeptime):
				time.sleep(1)
				if not runStatus.run:
					self.log.info( "Breaking due to exit flag being set")
					break

			return True

		except WebRequest.WebGetException:

			self.log.error("Failure retrieving content for link %s", link_row_id)
			self.log.error("Traceback: %s", traceback.format_exc())
			with self.row_context(dbid=link_row_id) as row:
				row.state = 'error'
				row.err_str = traceback.format_exc()
			return False


if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup():

		run = ContentLoader()
		run.do_fetch_content()
