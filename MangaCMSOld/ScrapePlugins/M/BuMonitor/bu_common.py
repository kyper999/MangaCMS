
import settings
import time
import WebRequest
import ChromeController


def fetch_retrier(soup=True, wg=None, log=None, *args, **kwargs):
	assert wg
	assert log
	for x in range(9999):
		try:

			if not args and len(kwargs) == 1 and 'requestedUrl' in kwargs:
				wg.navigate_timeout_secs = 40
				content, fileN, mType = wg.getItemChromium(itemUrl=kwargs['requestedUrl'])
				ret = content
			else:
				ret = wg.getpage(*args, **kwargs)

			if soup:
				ret = WebRequest.as_soup(ret)

			time.sleep(5)
			return ret

		except (WebRequest.FetchFailureError, ChromeController.ChromeResponseNotReceived) as e:
			if x > 5:
				raise
			sleep_interval = 15 * (x+1)
			log.warning("Fetching page failed. Retrying after %s seconds.", sleep_interval)
			time.sleep(sleep_interval)


def checkLogin(log, wg):
	log.info("Validating login state")

	checkPage = fetch_retrier(requestedUrl="https://www.mangaupdates.com/", wg=wg, log=log)
	if "You are currently logged in as" in checkPage:
		log.info("Still logged in")
		return
	else:
		log.info("Whoops, need to get Login cookie")

	logondict = {"username" : settings.buSettings["login"], "password" : settings.buSettings["passWd"], "act" : "login", 'x' : 0, 'y' : 0}
	getPage = fetch_retrier(requestedUrl="https://www.mangaupdates.com/login.html", postData=logondict, wg=wg, log=log)


	if "You are currently logged in as" in getPage:
		log.info("Logged in successfully!")
	else:
		log.error("Login failed!")
		raise ValueError("Cannot login to MangaUpdates. Is your login/password valid?")

	wg.saveCookies()
