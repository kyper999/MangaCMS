#!/bin/bash

set -e

alembic -n testing downgrade base
alembic -n testing upgrade head
alembic -n testing downgrade base


python3 $(which nosetests)                       \
	--with-coverage                              \
	--exe                                        \
	--cover-package=MangaCMS                     \
	--stop \
	MangaCMS.test
	# --nocapture \
	# Tests.Test_db_BKTree_Compare
	# Tests.Test_db_BKTree_Issue_2
	# Tests.Test_db_BKTree_Issue_1
	# Tests.Test_db_BKTree_2
	# Tests.Test_db_BKTree

coverage report --show-missing


coverage erase