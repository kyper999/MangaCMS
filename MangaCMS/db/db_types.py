
from sqlalchemy.dialects.postgresql import ENUM

dlstate_enum   = ENUM('new', 'fetching', 'processing', 'complete', 'error', 'removed', 'disabled', 'upload', name='dlstate_enum')
dir_type       = ENUM('had_dir', 'created_dir', 'unknown', name='dirtype_enum')
