
import settings
def checkLogin(log, wg):

	checkPage = wg.getpage("https://www.mangaupdates.com/mylist.html")
	if "You must be a user to access this page." in checkPage:
		log.info("Whoops, need to get Login cookie")
	else:
		log.info("Still logged in")
		return

	logondict = {"username" : settings.buSettings["login"], "password" : settings.buSettings["passWd"], "act" : "login", 'x' : 0, 'y' : 0}
	getPage = wg.getpage(r"https://www.mangaupdates.com/login.html", postData=logondict)

	# with open("LoginPage.html", "w") as fp:
	# 	fp.write(getPage)

	if "You are currently logged in as" in getPage:
		log.info("Logged in successfully!")
	else:
		log.error("Login failed!")
		raise ValueError("Cannot login to MangaUpdates. Is your login/password valid?")

	wg.saveCookies()
