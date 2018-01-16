
import settings
import os
import os.path

import nameTools as nt

import time

import urllib.parse
import html.parser
import zipfile
import runStatus
import traceback
import bs4
import re

from concurrent.futures import ThreadPoolExecutor



def checkLogin(wg):

	soup = wg.getSoup("https://bato.to/forums/index.php?app=core&module=global&section=login")
	userl = soup.find("a", id='user_link')
	if userl and "Welcome, {}".format(settings.batotoSettings['login'].lower()) in userl.get_text().lower():
		return True
	elif userl:
		print("Warning: Found user link, but not login info")
		print("This is possibly a problem")

	auth_key = soup.find("input", attrs={"name":'auth_key'})

	login_data = {
		"auth_key"     : auth_key['value'],
		"ips_username" : settings.batotoSettings['login'],
		"ips_password" : settings.batotoSettings['passWd'],
		"rememberMe"   : "1",
		"referer"      : "https://bato.to/forums/index.php?app=core&amp;module=global&amp;section=login",
		}

	login = wg.getSoup("https://bato.to/forums/index.php?app=core&module=global&section=login&do=process", postData=login_data)


	userl = login.find("a", id='user_link')
	if userl and "Welcome, {}".format(settings.batotoSettings['login'].lower()) in userl.get_text().lower():
		print("Logged in successfully")
		return True
	raise ValueError("Failed to log in!")
