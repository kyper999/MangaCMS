
import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import Table
from sqlalchemy import Index

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

# Patch in knowledge of the citext type, so it reflects properly.
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.dialects.postgresql import ENUM

import citext
ischema_names['citext'] = citext.CIText
dlstate_enum   = ENUM('new', 'fetching', 'processing', 'complete', 'error', 'removed', 'disabled', name='dlstate_enum')

from .db_base import Base

db_tags_link = Table(
		'db_tags_link', Base.metadata,
		Column('releases_id', Integer, ForeignKey('db_files.id'), nullable=False),
		Column('tags_id',     Integer, ForeignKey('db_tags.id'),  nullable=False),
		PrimaryKeyConstraint('releases_id', 'tags_id')
	)


class Tags(Base):
	__tablename__ = 'db_tags'
	id          = Column(Integer, primary_key=True)
	tag         = Column(citext.CIText(), nullable=False, index=True)

	__table_args__ = (
			UniqueConstraint('tag'),
		)

def tag_creator(tag):
	tmp = session.query(Tags)    \
		.filter(Tags.tag == tag) \
		.scalar()

	if tmp:
		return tmp

	return Tags(tag=tag)


class ReleaseFile(Base):
	__tablename__ = 'db_files'
	id          = Column(BigInteger, primary_key=True)

	filepath    = Column(citext.CIText(), nullable=False)
	fhash       = Column(Text, nullable=False)

	phash       = Column(BigInteger)
	imgx        = Column(Integer)
	imgy        = Column(Integer)

	tags_rel      = relationship('Tags',       secondary=lambda: db_tags_link)
	tags          = association_proxy('tags_rel',      'tag',       creator=tag_creator)

	__table_args__ = (
		UniqueConstraint('filepath', 'filepath'),
		UniqueConstraint('fhash'),
		Index('phash_bktree_idx', 'phash', postgresql_using="spgist")
		)


class Releases(Base):
	__tablename__ = 'db_releases'
	id          = Column(BigInteger, primary_key=True)
	state       = Column(dlstate_enum, nullable=False, index=True, default='new')
	err_str     = Column(Text)
	postid      = Column(Integer, nullable=False, index=True)

	source      = Column(citext.CIText, nullable=False, index=True)

	fsize       = Column(BigInteger)
	score       = Column(Float)
	favourites  = Column(Integer)

	parent      = Column(Text)

	posted      = Column(DateTime)

	res_x       = Column(Integer)
	res_y       = Column(Integer)


	status      = Column(Text)
	rating      = Column(Text)

	fileid        = Column(BigInteger, ForeignKey('db_files.id'))
	file_rel      = relationship('ReleaseFile')

	__table_args__ = (
		UniqueConstraint('postid', 'source'),
		Index('db_releases_source_state_id_idx', 'source', 'state', 'id')
		)





