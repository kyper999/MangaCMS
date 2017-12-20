# import sys
# sys.path.insert(0,"..")
import os.path
import os
import MangaCMS.lib.logSetup
if __name__ == "__main__":
	MangaCMS.lib.logSetup.initLogging()

import UniversalArchiveInterface
import traceback

import runStatus
runStatus.preloadDicts = False

import MangaCMS.cleaner.archCleaner

def cleanArchives(baseDir):
	print(baseDir)
	cleaner = MangaCMS.cleaner.archCleaner.ArchCleaner()

	for root, dirs, files in os.walk(baseDir):
		for name in files:
			fileP = os.path.join(root, name)
			print("Processing", fileP)

			try:
				if UniversalArchiveInterface.ArchiveReader.isArchive(fileP):
					cleaner.cleanZip(fileP)

			except KeyboardInterrupt:
				raise

			except:
				print("ERROR")
				traceback.print_exc()
				pass