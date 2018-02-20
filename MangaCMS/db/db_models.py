
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import Table
from sqlalchemy import Index

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
import sqlalchemy_jsonfield

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

# Patch in knowledge of the citext type, so it reflects properly.
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.dialects.postgresql import ENUM

import citext
ischema_names['citext'] = citext.CIText

import settings

from .db_base import Base
from .db_types import dir_type
from .db_types import dlstate_enum

manga_tags_link = Table(
		'db_tags_link', Base.metadata,
		Column('releases_id', Integer, ForeignKey('manga_files.id'), nullable=False),
		Column('tags_id',     Integer, ForeignKey('manga_tags.id'),  nullable=False),
		PrimaryKeyConstraint('releases_id', 'tags_id')
	)

class MangaTags(Base):
	__tablename__ = 'manga_tags'
	id          = Column(Integer, primary_key=True)
	tag         = Column(citext.CIText(), nullable=False, index=True)

	__table_args__ = (
			UniqueConstraint('tag'),
		)

def manga_tag_creator(tag):
	tmp = session.query(MangaTags)    \
		.filter(MangaTags.tag == tag) \
		.scalar()

	if tmp:
		return tmp

	return MangaTags(tag=tag)


class MangaReleaseFile(Base):
	__tablename__ = 'manga_files'
	id             = Column(BigInteger, primary_key=True)

	dirpath        = Column(Text, nullable=False)
	filename       = Column(Text, nullable=False)
	fhash          = Column(Text, nullable=False)

	last_dup_check = Column(DateTime, nullable=False, default=datetime.datetime.min)

	tags_rel       = relationship('MangaTags',            secondary=lambda: manga_tags_link)
	tags           = association_proxy('tags_rel',   'tag',       creator=manga_tag_creator)

	# releases       = relationship('MangaReleases')

	__table_args__ = (
		UniqueConstraint('dirpath', 'filename'),
		UniqueConstraint('fhash'),
		)


class MangaReleases(Base):
	__tablename__ = 'manga_releases'
	id                  = Column(BigInteger, primary_key=True)
	state               = Column(dlstate_enum, nullable=False, index=True, default='new')
	err_str             = Column(Text)

	source_site         = Column(Text, nullable=False, index=True)  # Actual source site
	source_id           = Column(Text, nullable=False, index=True)  # ID On source site. Usually (but not always) the item URL

	posted_at           = Column(DateTime, nullable=False, default=datetime.datetime.min)
	downloaded_at       = Column(DateTime, nullable=False, default=datetime.datetime.min)
	last_checked        = Column(DateTime, nullable=False, default=datetime.datetime.min)

	was_duplicate       = Column(Boolean, default=False, nullable=False)
	phash_duplicate     = Column(Boolean, default=False, nullable=False)
	uploaded            = Column(Boolean, default=False, nullable=False)

	dirstate            = Column(dir_type, nullable=False, default="unknown")

	origin_name         = Column(Text)

	additional_metadata = Column(sqlalchemy_jsonfield.JSONField())

	fileid              = Column(BigInteger, ForeignKey('manga_files.id'))
	file                = relationship('MangaReleaseFile')

	__table_args__ = (
		UniqueConstraint('source_site', 'source_id'),
		Index('db_releases_source_site_id_idx', 'source_site', 'source_id')
		)





