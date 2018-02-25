
import os
import datetime
import urllib.parse
import sys
from ipaddress import IPv4Address, IPv4Network
import settings

from flask import Flask
from flask import g
from flask import request
from flask_wtf.csrf import CsrfProtect
from babel.dates import format_datetime



print("App import!")

app = Flask(__name__)

if "debug" in sys.argv:
	print("Flask running in debug mode!")
	app.debug = True
app.config.from_object('MangaCMS.app.config.BaseConfig')

CsrfProtect(app)


if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	os.makedirs("tmp", exist_ok=True)
	file_handler = RotatingFileHandler('tmp/MangaCMS.log', 'a', 1 * 1024 * 1024, 10)
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(logging.Formatter(
		'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.addHandler(file_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info('MangaCMS startup')


from MangaCMS.app import all_scrapers_ever
from MangaCMS.app import views

@app.context_processor
def utility_processor():

	def format_date(value, format='medium'):

		return format_datetime(value, "EE yyyy.MM.dd")

	def date_now():
		return format_datetime(datetime.datetime.today(), "yyyy/MM/dd, hh:mm:ss")

	def ago(then):
		if then == None:
			return "Never"
		now = datetime.datetime.now()
		delta = now - then

		d = delta.days
		h, s = divmod(delta.seconds, 3600)
		m, s = divmod(s, 60)
		labels = ['d', 'h', 'm', 's']
		dhms = ['%s %s' % (i, lbl) for i, lbl in zip([d, h, m, s], labels)]
		for start in range(len(dhms)):
			if not dhms[start].startswith('0'):
				break
		for end in range(len(dhms)-1, -1, -1):
			if not dhms[end].startswith('0'):
				break
		return ', '.join(dhms[start:end+1])

	def fixed_width_ago(then):
		if then == None:
			return "Never"
		now = datetime.datetime.now()
		delta = now - then

		d = delta.days
		h, s = divmod(delta.seconds, 3600)
		m, s = divmod(s, 60)
		labels = ['d', 'h', 'm', 's']
		dhms = ['%s %s' % (str(i).zfill(2), lbl) for i, lbl in zip([d, h, m, s], labels)]
		for start in range(len(dhms)):
			if not dhms[start].startswith('0'):
				break
		for end in range(len(dhms)-1, -1, -1):
			if not dhms[end].startswith('0'):
				break
		ret = ', '.join(dhms)
		return ret


	def terse_ago(then):
		if then is None or then is False:
			return "Never"

		# print("Then: ", then)
		now = datetime.datetime.now()
		delta = now - then

		d = delta.days
		h, s = divmod(delta.seconds, 3600)
		m, s = divmod(s, 60)
		labels = ['d', 'h', 'm', 's']
		dhms = ['%s %s' % (i, lbl) for i, lbl in zip([d, h, m, s], labels)]
		for start in range(len(dhms)):
			if not dhms[start].startswith('0'):
				break
		# for end in range(len(dhms)-1, -1, -1):
		# 	if not dhms[end].startswith('0'):
		# 		break
		if d > 0:
			dhms = dhms[:2]
		elif h > 0:
			dhms = dhms[1:3]
		else:
			dhms = dhms[2:]
		return ', '.join(dhms)


	def compact_date_str(dateStr):
		dateStr = dateStr.replace("months", "mo")
		dateStr = dateStr.replace("month", "mo")
		dateStr = dateStr.replace("weeks", "w")
		dateStr = dateStr.replace("week", "w")
		dateStr = dateStr.replace("days", "d")
		dateStr = dateStr.replace("day", "d")
		dateStr = dateStr.replace("hours", "hr")
		dateStr = dateStr.replace("hour", "hr")
		dateStr = dateStr.replace("minutes", "m")
		dateStr = dateStr.replace("seconds", "s")
		dateStr = dateStr.replace("years", "yrs")
		dateStr = dateStr.replace("year", "yr")
		return dateStr


	def ip_in_whitelist():
		user_ip = IPv4Address(request.remote_addr)

		w_ip = IPv4Network(settings.pronWhiteList)
		if user_ip in w_ip:
			return True
		return False


	def f_size_to_str(fSize):
		if fSize == 0:
			return ''

		fStr = fSize/1.0e6
		if fStr < 100:
			fStr = "%0.2f M" % fStr
		else:
			fStr = "%0.1f M" % fStr

		return fStr


	return dict(
			compact_date_str   = compact_date_str,
			ip_in_whitelist    = ip_in_whitelist,
			f_size_to_str      = f_size_to_str,
			format_date        = format_date,
			date_now           = date_now,
			ago                = ago,
			fixed_width_ago    = fixed_width_ago,
			terse_ago          = terse_ago,
			manga_scrapers     = all_scrapers_ever.manga_scrapers,
			hentai_scrapers    = all_scrapers_ever.hentai_scrapers,
			other_scrapers     = all_scrapers_ever.other_scrapers,
			)

