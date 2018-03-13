
import sys

import os.path
import runStatus
from utilities.dedupDir import DirDeduper
import signal
import MangaCMS.activePlugins


def customHandler(dummy_signum, dummy_stackframe):
	if runStatus.run:
		runStatus.run = False
		print("Telling threads to stop")
	else:
		print("Multiple keyboard interrupts. Raising")
		raise KeyboardInterrupt

def install_signal_handler():
	signal.signal(signal.SIGINT, customHandler)

def print_plgs(keylist, plugins):
	for plg_key in keylist:

		print("	key: '{}'".format(plg_key))
		print("		Name: ", plugins[plg_key]['name'])
		print("		Runner Module: ", plugins[plg_key]['runner'])


def listPlugins():
	plgs = MangaCMS.activePlugins.PLUGIN_MAP
	keys = list(plgs.keys())
	keys.sort()

	mk = [key for key in keys if not plgs[key]["is_h"]]
	hk = [key for key in keys if plgs[key]["is_h"]]

	print("Manga Scrapers:")
	print_plgs(mk, plgs)
	print("")
	print("Hentai Scrapers:")
	print_plgs(hk, plgs)

def runPlugin(plug):
	install_signal_handler()

	plgs = MangaCMS.activePlugins.PLUGIN_MAP
	if not plug in plgs:
		print("Key {} not in available plugins!".format(plug))
		for key, plgd in plgs.items():
			print("	Plugin {} -> {}!".format(key, plgd['name']))
		return

	import nameTools as nt
	nt.dirNameProxy.startDirObservers()

	to_run = plgs[plug]
	runner = to_run['runner']()
	runner.go()


def retagPlugin(plug):
	install_signal_handler()

	plgs = MangaCMS.activePlugins.PLUGIN_MAP
	if not plug in plgs:
		print("Key {} not in available plugins ({})!".format(plug, list(plgs.keys())))
		return

	print("NOT IMPLEMENTED YET (OR EVER?)")
	# to_run = plgs[plug]
	# runner = to_run['runner']()
	# runner.go()






