"""empty message

Revision ID: 7cae4f4fa42d
Revises:
Create Date: 2018-02-20 00:54:47.444389

"""

# revision identifiers, used by Alembic.
revision = '7cae4f4fa42d'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import sqlalchemy_jsonfield
import sqlalchemy_utils

# Patch in knowledge of the citext type, so it reflects properly.
from sqlalchemy.dialects.postgresql.base import ischema_names
import citext
import queue
import datetime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
ischema_names['citext'] = citext.CIText

from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('manga_files',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('dirpath', sa.Text(), nullable=False),
    sa.Column('filename', sa.Text(), nullable=False),
    sa.Column('fhash', sa.Text(), nullable=False),
    sa.Column('last_dup_check', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dirpath', 'filename'),
    sa.UniqueConstraint('fhash')
    )
    op.create_table('manga_tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', citext.CIText(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag')
    )
    op.create_index(op.f('ix_manga_tags_tag'), 'manga_tags', ['tag'], unique=False)
    op.create_table('db_tags_link',
    sa.Column('releases_id', sa.Integer(), nullable=False),
    sa.Column('tags_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['releases_id'], ['manga_files.id'], ),
    sa.ForeignKeyConstraint(['tags_id'], ['manga_tags.id'], ),
    sa.PrimaryKeyConstraint('releases_id', 'tags_id')
    )
    op.create_table('manga_releases',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('state', postgresql.ENUM('new', 'fetching', 'processing', 'complete', 'error', 'removed', 'disabled', 'upload', 'missing', name='dlstate_enum'), nullable=False),
    sa.Column('err_str', sa.Text(), nullable=True),
    sa.Column('source_site', sa.Text(), nullable=False),
    sa.Column('source_id', sa.Text(), nullable=False),
    sa.Column('posted_at', sa.DateTime(), nullable=False),
    sa.Column('downloaded_at', sa.DateTime(), nullable=False),
    sa.Column('last_checked', sa.DateTime(), nullable=False),
    sa.Column('was_duplicate', sa.Boolean(), nullable=False),
    sa.Column('dirstate', postgresql.ENUM('had_dir', 'created_dir', 'unknown', name='dirtype_enum'), nullable=False),
    sa.Column('origin_name', sa.Text(), nullable=True),
    sa.Column('additional_metadata', sqlalchemy_jsonfield.jsonfield.JSONField(), nullable=True),
    sa.Column('fileid', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['fileid'], ['manga_files.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_site', 'source_id')
    )
    op.create_index('db_releases_source_site_id_idx', 'manga_releases', ['source_site', 'source_id'], unique=False)
    op.create_index(op.f('ix_manga_releases_source_id'), 'manga_releases', ['source_id'], unique=False)
    op.create_index(op.f('ix_manga_releases_source_site'), 'manga_releases', ['source_site'], unique=False)
    op.create_index(op.f('ix_manga_releases_state'), 'manga_releases', ['state'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_manga_releases_state'), table_name='manga_releases')
    op.drop_index(op.f('ix_manga_releases_source_site'), table_name='manga_releases')
    op.drop_index(op.f('ix_manga_releases_source_id'), table_name='manga_releases')
    op.drop_index('db_releases_source_site_id_idx', table_name='manga_releases')
    op.drop_table('manga_releases')
    op.drop_table('db_tags_link')
    op.drop_index(op.f('ix_manga_tags_tag'), table_name='manga_tags')
    op.drop_table('manga_tags')
    op.drop_table('manga_files')
    # ### end Alembic commands ###
