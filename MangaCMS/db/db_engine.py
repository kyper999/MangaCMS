
import sys
import multiprocessing
import threading
import contextlib

from settings import MAX_DB_SESSIONS

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import time


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

import queue

from settings import NEW_DATABASE_IP            as C_DATABASE_IP
from settings import NEW_DATABASE_DB_NAME       as C_DATABASE_DB_NAME
from settings import NEW_DATABASE_USER          as C_DATABASE_USER
from settings import NEW_DATABASE_PASS          as C_DATABASE_PASS


if '__pypy__' in sys.builtin_module_names:
	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2cffi://{user}:{passwd}@{host}:5432/{database}'.format(user=C_DATABASE_USER, passwd=C_DATABASE_PASS, host=C_DATABASE_IP, database=C_DATABASE_DB_NAME)
else:
	SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{passwd}@{host}:5432/{database}'.format(user=C_DATABASE_USER, passwd=C_DATABASE_PASS, host=C_DATABASE_IP, database=C_DATABASE_DB_NAME)


# I was having issues with timeouts because the default connection pool is 5 connections.
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size = MAX_DB_SESSIONS, isolation_level='REPEATABLE_READ')

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session = scoped_session(SessionFactory)



