

import pprint
import calendar
import traceback

from dateutil import parser
import settings
import parsedatetime
import urllib.parse
import time
import calendar

import MangaCMS.ScrapePlugins.LoaderBase
import concurrent.futures

class NotEnglishException(RuntimeError): pass

class DbLoader(MangaCMS.ScrapePlugins.LoaderBase.LoaderBase):


	dbName = settings.DATABASE_DB_NAME
	loggerPath = "Main.Manga.Hentai2Read.Fl"
	pluginName = "Hentai2Read Link Retreiver"
	tableKey   = "h2r"
	urlBase    = "https://hentai2read.com/"


	tableName = "HentaiItems"

	def loadFeed(self, pageOverride=None):
		self.log.info("Retreiving feed content...")
		if not pageOverride:
			pageOverride = 1

		url = "https://hentai2read.com/hentai-list/all/any/all/last-updated/{}/".format(pageOverride)

		soup = self.wg.getSoup(url, addlHeaders={"Referer" : self.urlBase})

		return url, soup


	def process_row(self, row_name, row_content):
		ret = []

		tag_buttons = row_content.find_all('a', class_='tagButton')

		tag_buttons = [tmp for tmp in tag_buttons if tmp.get_text(strip=True) != "-"]

		if row_name == 'Parody':
			for button in tag_buttons:
				ret.append("parody " + button.get_text(strip=True))

		elif row_name == 'Ranking':
			pass
		elif row_name == 'Status':
			pass
		elif row_name == 'Rating':
			pass
		elif row_name == 'View':
			pass

		elif row_name == 'Storyline':
			pass

		elif row_name == 'Release Year':
			for button in tag_buttons:
				ret.append("release year " + button.get_text(strip=True))
		elif row_name == 'Author':
			for button in tag_buttons:
				ret.append("author " + button.get_text(strip=True))
		elif row_name == 'Artist':
			for button in tag_buttons:
				ret.append("artist " + button.get_text(strip=True))
		elif row_name == 'Category':
			for button in tag_buttons:
				ret.append(button.get_text(strip=True))
		elif row_name == 'Content':
			for button in tag_buttons:
				ret.append(button.get_text(strip=True))
		elif row_name == 'Character':
			for button in tag_buttons:
				if button.get('href', "Wat").startswith("http"):
					ret.append("character " + button.get_text(strip=True))
		elif row_name == 'Language':
			if row_content.get_text(strip=True) != "English":
				raise NotEnglishException("Language is not english: %s" %  row_content.get_text(strip=True))
			else:
				ret.append("language english")

		else:
			self.log.error("Unknown tag: '%s'", row_name)
			self.log.error("%s", row_content)
			raise RuntimeError("Unknown category tag: '{}' -> '{}'".format(row_name, row_content.prettify()))

		return ret

	def getInfo(self, soup):
		meta_list = soup.find("ul", class_='list')

		meta_dict = {
				'tags'       : [],
				"seriesName" : None,
			}
		for list_entry in meta_list.find_all("li"):
			if list_entry.get('class', None) == ['text-muted']:
				sname = list_entry.get_text(strip=True)
				if sname == "-":
					sname = None
				meta_dict["seriesName"] = sname

			elif list_entry.b:
				item_name = list_entry.b.get_text(strip=True)
				list_entry.b.decompose()

				meta_dict['tags'].extend(self.process_row(item_name, list_entry))


			else:
				if list_entry.get_text(strip=True):
					self.log.error("Missing heading in section")
					self.log.error("%s", list_entry)


		if meta_dict['seriesName'] is None:
			header_div = soup.find("section", class_='content')
			titletag = header_div.find('h3', class_='block-title')
			if titletag.small:
				titletag.small.decompose()

			meta_dict['seriesName'] = titletag.get_text(strip=True)

		while any(["  " in tag for tag in meta_dict['tags']]):
			meta_dict['tags'] = [tag.replace("  ", " ") for tag in meta_dict['tags']]
		meta_dict['tags'] = [tag.replace(" ", "-") for tag in meta_dict['tags']]
		meta_dict['tags'] = [tag.lower() for tag in meta_dict['tags']]


		while any(["--" in tag for tag in meta_dict['tags']]):
			meta_dict['tags'] = [tag.replace("--", "-") for tag in meta_dict['tags']]

		# Colons break the tsvector
		meta_dict['tags'] = [tag.replace(":", "-") for tag in meta_dict['tags']]

		meta_dict['tags'] = " ".join(meta_dict['tags'])


		# print("Series metadata: ", ret)
		return meta_dict


	def parseItem(self, itemurl, refurl):
		ret = []

		soup = self.wg.getSoup(itemurl, addlHeaders={"Referer" : refurl})

		series_meta = self.getInfo(soup)

		chap_list = soup.find("ul", class_='nav-chapters')

		if not chap_list:
			return ret

		for chap in chap_list.find_all('li', recursive=False):
			chap_d = {**series_meta}

			chap_d['sourceUrl'] = chap.a['href']

			dateinfo = chap.a.small.get_text()
			chap.a.small.decompose()

			timestr = dateinfo.split(" on ")[-1].strip()

			itemDate, status = parsedatetime.Calendar().parse(timestr)

			if status >= 1:
				chap_d['retreivalTime'] = calendar.timegm(itemDate)
			else:
				self.log.warning("Parsing relative date '%s' failed (%s). Using current timestamp.", timestr, status)
				chap_d['retreivalTime'] = time.time()



			if chap_d['seriesName'] is None:
				chap_d['originName'] = chap.a.get_text(strip=True)
				chap_d["seriesName"] = chap.a.get_text(strip=True)
			else:
				chap_d["originName"] = chap_d['seriesName'] + " – " + chap.a.get_text(strip=True)

			# assert not chap_d["seriesName"].startswith("1")
			# assert not chap_d["seriesName"].startswith("2")
			# assert not chap_d["seriesName"].startswith("3")
			# assert not chap_d["seriesName"].startswith("4")
			# assert not chap_d["seriesName"].startswith("5")
			# assert not chap_d["seriesName"].startswith("6")
			# assert not chap_d["seriesName"].startswith("7")
			# assert not chap_d["seriesName"].startswith("8")
			# assert not chap_d["seriesName"].startswith("9")

			ret.append(chap_d)


		self.log.info("Found %s chapters on item page", len(ret))


		return ret


	def getFeed(self, pageOverride=None):

		refurl, soup = self.loadFeed(pageOverride)


		divs = soup.find_all("div", class_='img-container')

		ret = []

		for itemDiv in divs:
			series_page =  urllib.parse.urljoin(self.urlBase, itemDiv.h2.parent["href"])
			chapters = self.parseItem(series_page, refurl)
			if chapters:
				ret.extend(chapters)

		# if retag:
		# 	self.update_tags(ret)
		# 	ret = []

		return ret

def process(runner, pageOverride):
	print("Executing with page offset: pageOverride")
	runner.do_fetch_feeds(pageOverride=pageOverride)


def getHistory():
	print("Getting history")
	run = DbLoader()
	with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
		futures = [executor.submit(process, runner=run, pageOverride=x) for x in range(0, 410)]
		print("Waiting for executor to finish.")
		executor.shutdown()

def test():
	print("Test!")
	run = DbLoader()

	dat = run.getFeed()
	print(dat)
	# print(run.go())
	# print(run)
	# pprint.pprint(run.getFeed())

if __name__ == "__main__":
	import utilities.testBase as tb

	with tb.testSetup(load=False):
		getHistory()
		# test()

		# run = DbLoader()
		# run.do_fetch_feeds()
