
from flask import g
from flask import render_template
from flask import make_response
from flask import request

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import max as sql_max
from sqlalchemy.sql.expression import desc as sql_desc

print("Manga View import!")
from MangaCMS.app import app
from MangaCMS.app import all_scrapers_ever
from MangaCMS.app.utilities import paginate
import MangaCMS.db as db

def parse_table_args(**kwargs):
	print(request.args)
	ret = {
		'distinct'        : False,
		'include-deleted' : False,
		'limit-by-source' : False,
		'filter-tag'      : None,
	}

	# Override the return parameters with the function
	# params (if passed).
	# Note: underscores are replaced with hyphens in the keys!
	for key, val in kwargs.items():
		key = key.replace("_", "-")
		if key in ret:
			ret[key] = val

	if 'distinct' in request.args and request.args['distinct'].lower() == "true":
		ret['distinct'] = True
	if 'include-deleted' in request.args and request.args['include-deleted'].lower() == "true":
		ret['include-deleted'] = True
	if 'limit-by-source' in request.args:
		val = request.args['limit-by-source'].lower()
		if val in [tmp['dbKey'] for tmp in all_scrapers_ever.all_scrapers]:
			ret['limit-by-source'] = val

	if 'filter-tag' in request.args:
		raise ValueError("Implement me!")
	return ret

def select_from_table(table, page, site=False, tag=None, category=None):
	params = parse_table_args(limit_by_source=site)

	query = g.session.query(table) \
				.options(joinedload("file"), joinedload("file.hentai_tags_rel"), joinedload("tags_rel"), )


	if not params['include-deleted']:
		query = query.filter(table.deleted == False)
	if params['limit-by-source']:
		query = query.filter(table.source_site == params['limit-by-source'])
	if params['distinct']:
		query = query.distinct(table.series_name) \
			.order_by(sql_desc(sql_max(table.downloaded_at)))
	else:
		query = query.order_by(table.downloaded_at.desc())

	return params, paginate(query, page=page)


@app.route('/manga/', methods=['GET'])
@app.route('/manga/page/<int:page>', methods=['GET'])
def manga_only_view(page=1):
	params, items = select_from_table(db.MangaReleases, page=page)
	return render_template('manga_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   url_for_param = "manga_only_view"
						   )

@app.route('/manga/by-site/<source_site>/', methods=['GET'])
@app.route('/manga/by-site/<source_site>/<int:page>', methods=['GET'])
def manga_by_site_view(source_site, page=1):
	params, items = select_from_table(db.MangaReleases, page=page, site=source_site)
	return render_template('manga_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   url_for_param = "manga_only_view"
						   )

@app.route('/hentai/', methods=['GET'])
@app.route('/hentai/page/<int:page>', methods=['GET'])
def hentai_only_view(page=1):
	params, items = select_from_table(db.HentaiReleases, page=page)
	return render_template('hentai_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   url_for_param = "hentai_only_view"
						   )

@app.route('/hentai/by-site/<source_site>/', methods=['GET'])
@app.route('/hentai/by-site/<source_site>/<int:page>', methods=['GET'])
def hentai_by_site_view(source_site, page=1):
	params, items = select_from_table(db.HentaiReleases, page=page, site=source_site)
	return render_template('hentai_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   url_for_param = "hentai_by_site_view"
						   )

@app.route('/hentai/by-tag/<tag>/', methods=['GET'])
@app.route('/hentai/by-tag/<tag>/<int:page>', methods=['GET'])
def hentai_tag_view(tag, page=1):
	params, items = select_from_table(db.HentaiReleases, page=page, tag=tag)
	return render_template('hentai_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   tag           = tag,
						   url_for_param = "hentai_tag_view"
						   )

@app.route('/hentai/by-category/<category>/', methods=['GET'])
@app.route('/hentai/by-category/<category>/<int:page>', methods=['GET'])
def hentai_category_view(category, page=1):
	params, items = select_from_table(db.HentaiReleases, page=page, category=category)
	return render_template('hentai_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   category      = category,
						   url_for_param = "hentai_category_view"
						   )


