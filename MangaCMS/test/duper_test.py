

import unittest
# import os
# print("CWD:", os.getcwd())

# import pdb
# pdb.set_trace()

import MangaCMS
from MangaCMS import db as mdb
from MangaCMS.db import db_models as db_models

class TestSequenceFunctions(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def setUp(self):
		print("Doing Setup!")
		self.addCleanup(self.dropDatabase)

		# self.db = self.getDb()
		# print("Items in DB:", self.db.getItemNum())
		# # Check the table is set up
		# self.assertEqual(self.db.getItemNum(), (len(TEST_DATA),),
		# 		'Setup resulted in an incorrect number of items in database!')

	def dropDatabase(self):
		print("Cleanup!")
		with mdb.session_context() as sess:
			# Delete the link tables
			sess.query(db_models.manga_files_tags_link).all()
			sess.query(db_models.manga_releases_tags_link).all()
			sess.query(db_models.hentai_files_tags_link).all()
			sess.query(db_models.hentai_releases_tags_link).all()

			# And then the releases/tags
			sess.query(db_models.MangaReleases).all()
			sess.query(db_models.HentaiReleases).all()
			sess.query(db_models.MangaTags).all()
			sess.query(db_models.HentaiTags).all()

			# Finally, the files
			sess.query(db_models.ReleaseFile).all()

		# self.db.tearDown()

	def test_wat(self):
		print("Database:", mdb)
		print("Wat?")


