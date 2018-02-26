print("Status view import")

from flask import g
from flask import render_template
from flask import make_response
from flask import request

import pickle
import time
import datetime
from calendar import timegm

from sqlalchemy.sql import text


from MangaCMS.app import app
import MangaCMS.db as db



@app.route('/reader/h/<int:rid>', methods=['GET'])
def view_h_by_id(rid):

	session = g.session
	# session.expire()
	tasks = get_scheduled_tasks(session)
	states = session.query(db.PluginStatus).all()
	session.commit()
	return render_template('status.html',
						   tasks          = tasks,
						   states         = states,
						   )


