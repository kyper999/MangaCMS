

import colorsys

all_scrapers = [
		{'dbKey' : "SkLoader",         'name' : "Starkana",    'dictKey' : "sk",      'cssClass' : "skId",    'showOnHome' : False, 'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "CzLoader",         'name' : "Crazy's",     'dictKey' : "cz",      'cssClass' : "czId",    'showOnHome' : True,  'renderSideBar' : False, 'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MbLoader",         'name' : "MangaBaby",   'dictKey' : "mb",      'cssClass' : "mbId",    'showOnHome' : True,  'renderSideBar' : False, 'genRow' : True,  'type' : 'Manga-defunct' },
		{'dbKey' : "BtLoader",         'name' : "Batoto",      'dictKey' : "bt",      'cssClass' : "btId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "JzLoader",         'name' : "Japanzai",    'dictKey' : "jz",      'cssClass' : "jzId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "McLoader",         'name' : "MangaCow",    'dictKey' : "mc",      'cssClass' : "mcId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "CxLoader",         'name' : "CXC Scans",   'dictKey' : "cx",      'cssClass' : "cxId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MjLoader",         'name' : "MangaJoy",    'dictKey' : "mj",      'cssClass' : "mjId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "RhLoader",         'name' : "RedHawk",     'dictKey' : "rh",      'cssClass' : "rhId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "LmLoader",         'name' : "LoneManga",   'dictKey' : "lm",      'cssClass' : "lmId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "WtLoader",         'name' : "Webtoon",     'dictKey' : "wt",      'cssClass' : "wtId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "DyLoader",         'name' : "Dynasty",     'dictKey' : "dy",      'cssClass' : "dyId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "KissLoader",       'name' : "KissManga",   'dictKey' : "ki",      'cssClass' : "kiId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "CrunchyRoll",      'name' : "CrunchyRoll", 'dictKey' : "cr",      'cssClass' : "crId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "RoseliaLoader",    'name' : "Roselia",     'dictKey' : "rs",      'cssClass' : "rsId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "SenseLoader",      'name' : "Sense",       'dictKey' : "se",      'cssClass' : "seId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "ShoujoSense",      'name' : "ShoujoSense", 'dictKey' : "sj",      'cssClass' : "sjId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "VortexLoader",     'name' : "Vortex",      'dictKey' : "vx",      'cssClass' : "vxId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "TwistedHel",       'name' : "TwistedHel",  'dictKey' : "th",      'cssClass' : "thId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "Casanova",         'name' : "Casanova",    'dictKey' : "cs",      'cssClass' : "csId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MsLoader",         'name' : "MangaStrm",   'dictKey' : "ms",      'cssClass' : "msId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MangatopiaLoader", 'name' : "Mangatopia",  'dictKey' : "mp",      'cssClass' : "mpId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "WrLoader",         'name' : "WebTnsRdr",   'dictKey' : "wr",      'cssClass' : "wrId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "IrcEnqueue",       'name' : "IRC XDCC",    'dictKey' : "irc-irh", 'cssClass' : "ircId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "IrcEnqueue",       'name' : "IRC Trigger", 'dictKey' : "irc-trg", 'cssClass' : "ircId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "kawaii",           'name' : "Kawaii Scans",'dictKey' : "kw",      'cssClass' : "kawaii",  'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "sura",             'name' : "Sura's Place",'dictKey' : "sura",    'cssClass' : "sura",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "mbx",              'name' : "MangaBox",    'dictKey' : "mbx",     'cssClass' : "mbx",     'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "gos",              'name' : "GosLoader",   'dictKey' : "gos",     'cssClass' : "gos",     'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "ym",               'name' : "YoManga",     'dictKey' : "ym",      'cssClass' : "ym",      'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "ms",               'name' : "MangaStrm",   'dictKey' : "ms",      'cssClass' : "ms",      'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "meraki",           'name' : "Meraki",      'dictKey' : "meraki",  'cssClass' : "meraki",  'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MkLoader",         'name' : "Madokami",    'dictKey' : "mk",      'cssClass' : "mkId",    'showOnHome' : False, 'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "BuMon",            'name' : "MU Mon",      'dictKey' : None,      'cssClass' : "buId",    'showOnHome' : False, 'renderSideBar' : True,  'genRow' : False, 'type' : 'Info'          },
		{'dbKey' : "MangaDex",         'name' : "MangaDex",    'dictKey' : "mdx",     'cssClass' : "mdxId",   'showOnHome' : False, 'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		{'dbKey' : "MangaZuki",        'name' : "MangaZuki",   'dictKey' : "mzk",     'cssClass' : "mzkId",   'showOnHome' : False, 'renderSideBar' : True,  'genRow' : True,  'type' : 'Manga'         },
		########################################################################################################
		{'dbKey' : False,              'name' : "Mt Mon",      'dictKey' : None,      'cssClass' : "mtMonId", 'showOnHome' : True,  'renderSideBar' : True,  'genRow' : False, 'type' : 'Manga-defunct' },
		########################################################################################################
		{'dbKey' : "DjMoe",            'name' : "DjMoe",       'dictKey' : "djm",     'cssClass' : "djmId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "Pururin",          'name' : "Pururin",     'dictKey' : "pu",      'cssClass' : "puId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "SadPanda",         'name' : "ExHentai",    'dictKey' : "sp",      'cssClass' : "spId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "H-Browse",         'name' : "H-Browse",    'dictKey' : "hb",      'cssClass' : "hbId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "FkLoader",         'name' : "Fakku",       'dictKey' : "fk",      'cssClass' : "fkId",    'showOnHome' : False, 'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "NHentai",          'name' : "NHentai",     'dictKey' : "nh",      'cssClass' : "nhId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "EmLoader",         'name' : "ExHenMado",   'dictKey' : "em",      'cssClass' : "emId",    'showOnHome' : True,  'renderSideBar' : False, 'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "Tadanohito",       'name' : "Tadano",      'dictKey' : "ta",      'cssClass' : "taId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "ExArchive",        'name' : "ExArch",      'dictKey' : "exArch",  'cssClass' : "exArId",  'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "Hitomi",           'name' : "Hitomi",      'dictKey' : "hit",     'cssClass' : "hitId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "DoujinOnline",     'name' : "DoujinOnline",'dictKey' : "dol",     'cssClass' : "dolId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "ASMHentai",        'name' : "ASMHentai",   'dictKey' : "asmh",    'cssClass' : "asmhId",  'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "Hentai2R",         'name' : "Hentai2R",    'dictKey' : "h2r",     'cssClass' : "h2rId",   'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },
		{'dbKey' : "Tsumino",          'name' : "Tsumino",     'dictKey' : "ts",      'cssClass' : "tsId",    'showOnHome' : True,  'renderSideBar' : True,  'genRow' : True,  'type' : 'Porn'          },

	]


def tupToHSV(tup):
	r, g, b = (var*(1.0/256) for var in tup)
	return colorsys.rgb_to_hsv(r, g, b)

def hsvToHex(ftup):
	ftup = colorsys.hsv_to_rgb(*ftup)
	r, g, b = (max(0, min(int(var*256), 255)) for var in ftup)
	ret = "#{r:02x}{g:02x}{b:02x}".format(r=r, g=g, b=b)
	return ret

# I don't want to have to add all of numpy as a dependency just to get linspace,
# so we duplicate it here.
def linspace(a, b, n=100):
	if n < 2:
		return [b]
	diff = (float(b) - a)/(n - 1)
	ret = [diff * i + a  for i in range(n)]
	return ret


manga_scrapers = []
hentai_scrapers = []
other_scrapers = []
for index, item in enumerate(all_scrapers):
	if "Manga" in item["type"]:
		manga_scrapers.append(item)
	elif "Porn" in item["type"]:
		hentai_scrapers.append(item)
	else:
		other_scrapers.append(item)

manga_scrapers.sort(key=lambda x: x['name'])
hentai_scrapers.sort(key=lambda x: x['name'])
other_scrapers.sort(key=lambda x: x['name'])
