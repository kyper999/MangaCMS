"""empty message

Revision ID: 0d077b4cbfbd
Revises: e786b3d63f9b
Create Date: 2018-02-20 05:56:43.746348

"""

# revision identifiers, used by Alembic.
revision = '0d077b4cbfbd'
down_revision = 'e786b3d63f9b'
branch_labels = None
depends_on = None

import datetime
import json
import hashlib
import os.path

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# Patch in knowledge of the citext type, so it reflects properly.
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql.base import ischema_names
import citext
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
ischema_names['citext'] = citext.CIText


import MangaCMSOld.lib.dbPool
import MangaCMS.db as db

def get_add_file(sess, fname, fpath):
	if fpath is None or fname is None:
		return None
	fqname = os.path.join(fpath, fname)
	if not os.path.exists(fqname):
		return None

	have = sess.query(db.MangaReleaseFile)             \
		.filter(db.MangaReleaseFile.dirpath == fpath)  \
		.filter(db.MangaReleaseFile.filename == fname) \
		.scalar()

	if have:
		print("Have row by path")
		return have


	print("Hashing file...", end="", flush=True)
	hash_md5 = hashlib.md5()
	with open(fqname, "rb") as f:
		for chunk in iter(lambda: f.read(4096*16), b""):
			hash_md5.update(chunk)
	fhash = hash_md5.hexdigest()
	print("done.")


	have = sess.query(db.MangaReleaseFile)          \
		.filter(db.MangaReleaseFile.fhash == fhash) \
		.scalar()

	if have:
		print("Have by fhash")
		return have

	new = db.MangaReleaseFile(
		dirpath  = fpath,
		filename = fname,
		fhash    = fhash
		)
	sess.add(new)
	return new


def upgrade():
	# ### commands auto generated by Alembic - please adjust! ###

	old_con = MangaCMSOld.lib.dbPool.pool.getconn()
	old_cur = old_con.cursor()
	bind = op.get_bind()
	sess = Session(bind=bind)
	print("DB Module:", db)
	print("Connection:", old_con)
	print("Cursor:", old_cur)
	print("Session:", sess)
	old_cur.execute("SELECT sourcesite, dlstate, sourceurl, retreivaltime, lastupdate, sourceid, seriesname, filename, originname, downloadpath, flags, tags, note FROM mangaitems")
	fetchchunk = 100
	more = old_cur.fetchmany(size=fetchchunk)
	while more:
		print("Chunk:")
		print(more)
		more = old_cur.fetchmany(size=fetchchunk)

		for item in more:
			sourcesite, dlstate, sourceurl, retreivaltime, lastupdate, sourceid, seriesname, filename, originname, downloadpath, flags, tags, note = item
			file = get_add_file(sess, filename, downloadpath)
			print(file)
			sess.flush()

			# print("'{}', '{}'".format(flags, tags))
			tags = tags if tags else ""
			flags = flags if flags else ""

			additional_metadata = None
			state_val = "new"
			if file is None:
				state_val = 'missing'
				additional_metadata = {
					'filename'     : filename,
					'downloadpath' : downloadpath,
				}
			elif dlstate == 1:
				state_val = 'fetching'
			elif dlstate == 2:
				state_val = 'complete'
			elif dlstate == 3:
				state_val = 'upload'
			elif dlstate > 3:
				state_val = 'disabled'
			elif dlstate < 0:
				state_val = 'error'

			dirstate_val = "unknown"
			if "haddir" in flags:
				dirstate_val = "had_dir"
			elif "new_dir" in flags:
				dirstate_val = "new_dir"

			if sourceid:
				loaded_meta = json.loads(sourceid)
				if additional_metadata is None:
					additional_metadata = {}

				additional_metadata['sourceid'] = loaded_meta

			row = db.MangaReleases(
					state               = state_val,
					err_str             = None,
					source_site         = sourcesite,
					source_id           = sourceurl,
					posted_at           = datetime.datetime.utcfromtimestamp(lastupdate),
					downloaded_at       = datetime.datetime.utcfromtimestamp(retreivaltime),
					phash_duplicate     = "phash-duplicate" in tags,
					was_duplicate       = "was-duplicate" in tags,
					uploaded            = "uploaded" in tags,
					dirstate            = dirstate_val,
					origin_name         = originname,
					additional_metadata = additional_metadata,
					fileid              = file.id if file else None,
				)
			sess.add(row)
		print("Committing!")

		sess.flush()
		sess.commit()
		bind.execute("""COMMIT""")

	raise RuntimeError("Wat?")
	pass
	# ### end Alembic commands ###


def downgrade():
	# ### commands auto generated by Alembic - please adjust! ###
	pass
	# ### end Alembic commands ###
