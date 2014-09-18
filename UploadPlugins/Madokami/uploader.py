

import ftplib
import settings
import logging
import os
import nameTools as nt
import Levenshtein as lv
import time

COMPLAIN_ABOUT_DUPS = False

import urllib.parse
import ScrapePlugins.RetreivalDbBase

class MkUploader(ScrapePlugins.RetreivalDbBase.ScraperDbBase):
	log = logging.getLogger("Main.Mk.Uploader")

	loggerPath = "Main.Mk.Up"
	pluginName = "Manga.Madokami Content Retreiver"
	tableKey = "mk"
	dbName = settings.dbName

	tableName = "MangaItems"

	def __init__(self):

		super().__init__()

		self.ftp = ftplib.FTP(host=settings.mkSettings["ftpAddr"])
		self.ftp.login()

		self.mainDirs     = {}
		self.unsortedDirs = {}

	def go(self):
		pass

	def moveItemsInDir(self, srcDirPath, dstDirPath):
		# FTP is /weird/. Rename apparently really wants to use the cwd for the srcpath param, even if the
		# path starts with "/". Therefore, we have to reset the CWD.
		self.ftp.cwd("/")
		for itemName, dummy_stats in self.ftp.mlsd(srcDirPath):
			if itemName == ".." or itemName == ".":
				continue
			srcPath = os.path.join(srcDirPath, itemName)
			dstPath = os.path.join(dstDirPath, itemName)
			self.ftp.rename(srcPath, dstPath)
			self.log.info("	Moved from '%s'", srcPath)
			self.log.info("	        to '%s'", dstPath)


	def aggregateDirs(self, pathBase, dir1, dir2):
		canonName = nt.getCanonicalMangaUpdatesName(dir1)
		canonNameAlt = nt.getCanonicalMangaUpdatesName(dir2)
		if canonName != canonNameAlt:
			print(dir1, dir2)
			print(canonName, canonNameAlt)
			raise ValueError("Identical and yet not?")
		self.log.info("Aggregating directories for canon name '%s':", canonName)

		n1 = lv.distance(dir1, canonName)
		n2 = lv.distance(dir2, canonName)

		self.log.info("	%s - '%s'", n1, dir1)
		self.log.info("	%s - '%s'", n2, dir2)

		# I'm using less then or equal, so situations where
		# both names are equadistant get aggregated anyways.
		if n1 <= n2:
			src = dir2
			dst = dir1
		else:
			src = dir1
			dst = dir2

		src = os.path.join(pathBase, src)
		dst = os.path.join(pathBase, dst)

		self.moveItemsInDir(src, dst)
		self.log.info("Removing directory '%s'", src)
		self.ftp.rmd(src)

		return dst

	def loadRemoteDirectory(self, fullPath, aggregate=False):
		ret = {}
		for dirName, stats in self.ftp.mlsd(fullPath):

			# Skip items that aren't directories
			if stats["type"]!="dir":
				continue

			canonName = nt.getCanonicalMangaUpdatesName(dirName)
			matchingName = nt.prepFilenameForMatching(canonName)

			fqPath = os.path.join(fullPath, dirName)

			if matchingName in ret:
				if aggregate:
					fqPath = self.aggregateDirs(fullPath, dirName, ret[matchingName])
				else:
					if COMPLAIN_ABOUT_DUPS:
						self.log.warning("Duplicate directories for series '%s'!", canonName)
						self.log.warning("	'%s'", dirName)
						self.log.warning("	'%s'", matchingName)
					ret[matchingName].append(fqPath)
			if aggregate:
				ret[matchingName] = fqPath
			else:
				ret[matchingName] = [fqPath]

		return ret

	def loadMainDirs(self):
		ret = {}
		try:
			dirs = list(self.ftp.mlsd(settings.mkSettings["mainContainerDir"]))
		except ftplib.error_perm:
			self.log.critical("Container dir ('%s') does not exist!", settings.mkSettings["mainContainerDir"])
		for dirPath, dummy_stats in dirs:
			if dirPath == ".." or dirPath == ".":
				continue
			dirPath = os.path.join(settings.mkSettings["mainContainerDir"], dirPath)
			items = self.loadRemoteDirectory(dirPath)
			for key, value in items.items():
				if key not in ret:
					ret[key] = value
				else:
					for item in value:
						ret[key].append(item)

			self.log.info("Loading contents of FTP dir '%s'.", dirPath)
		self.log.info("Have '%s remote directories on FTP server.", len(ret))
		return ret

	def checkInitDirs(self):
		try:
			dirs = list(self.ftp.mlsd(settings.mkSettings["uploadContainerDir"]))
		except ftplib.error_perm:
			self.log.critical("Container dir for uploads ('%s') does not exist!", settings.mkSettings["uploadContainerDir"])
			raise

		fullPath = os.path.join(settings.mkSettings["uploadContainerDir"], settings.mkSettings["uploadDir"])
		if settings.mkSettings["uploadDir"] not in [item[0] for item in dirs]:
			self.log.info("Need to create base container path")
			self.ftp.mkd(fullPath)
		else:
			self.log.info("Base container directory exists.")

		self.mainDirs     = self.loadMainDirs()
		self.unsortedDirs = self.loadRemoteDirectory(fullPath, aggregate=True)


	def migrateTempDirContents(self):
		for key in self.unsortedDirs.keys():
			if key in self.mainDirs and len(self.mainDirs[key]) == 1:
				print("Should move", key)
				print("	Src:", self.unsortedDirs[key])
				print("	Dst:", self.mainDirs[key][0])
				src = self.unsortedDirs[key]
				dst = self.mainDirs[key][0]

				self.moveItemsInDir(src, dst)
				self.log.info("Removing directory '%s'", src)
				self.ftp.rmd(src)

	def uploadFile(self, seriesName, filePath):
		seriesName = nt.getCanonicalMangaUpdatesName(seriesName)
		safeFilename = nt.makeFilenameSafe(seriesName)
		matchName = nt.prepFilenameForMatching(seriesName)

		# if matchName in self.mainDirs and len(self.mainDirs[matchName]) == 1:
		# 	newDir = self.mainDirs[matchName][0]

		# elif matchName in self.unsortedDirs:
		if matchName in self.unsortedDirs:
			newDir = self.unsortedDirs[matchName]
		else:

			self.log.info("Need to create container directory for %s", seriesName)
			newDir = os.path.join(settings.mkSettings["uploadContainerDir"], settings.mkSettings["uploadDir"], safeFilename)
			self.ftp.mkd(newDir)

		dummy_path, filename = os.path.split(filePath)
		self.log.info("Uploading file %s", filePath)
		self.log.info("From series %s", seriesName)
		self.log.info("To container directory %s", newDir)
		self.ftp.cwd(newDir)


		self.ftp.storbinary("STOR %s" % filename, open(filePath, "rb"))
		self.log.info("File Uploaded")


		dummy_fPath, fName = os.path.split(filePath)
		url = urllib.parse.urljoin("http://manga.madokami.com", urllib.parse.quote(filePath.strip("/")))

		self.insertIntoDb(retreivalTime = time.time(),
							sourceUrl   = url,
							originName  = fName,
							dlState     = 3,
							seriesName  = seriesName,
							flags       = '',
							tags="uploaded",
							commit = True)  # Defer commiting changes to speed things up





def uploadFile(seriesName, filePath):
	uploader = MkUploader()
	uploader.checkInitDirs()
	uploader.uploadFile(seriesName, filePath)


def test():
	pass

if __name__ == "__main__":
	test()
