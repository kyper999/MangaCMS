
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

	print((request.args, kwargs))

	filter_params = {
		'distinct'        : [],
		'include-deleted' : [],
		'limit-by-source' : [],
		'filter-tags'      : [],
		'filter-category' : [],
	}

	# Override the return parameters with the function
	# params (if passed).
	# Note: underscores are replaced with hyphens in the keys!
	for key, val in request.args.items():
		key = key.replace("_", "-")
		if key in filter_params and val:
			filter_params[key].append(val)
	for key, val in kwargs.items():
		key = key.replace("_", "-")
		if key in filter_params and val:
			filter_params[key].append(val)

	print("Filter params: ", filter_params)

	if 'distinct' in filter_params and filter_params['distinct'] and filter_params['distinct'][0].lower() == "true":
		filter_params['distinct'] = True
	if 'include-deleted' in filter_params and filter_params['include-deleted'] and filter_params['include-deleted'][0].lower() == "true":
		filter_params['include-deleted'] = True
	if 'limit-by-source' in filter_params and filter_params['limit-by-source']:
		for val in filter_params['limit-by-source']:
			if not val:
				continue
			val = val.lower()
			new = []
			if val in [tmp['dbKey'] for tmp in all_scrapers_ever.all_scrapers]:
				new.append(val)
			filter_params['limit-by-source'] = new

	if 'filter-tags' in filter_params and filter_params['filter-tags']:
		filter_params['filter-tags'] = [str(tmp) for tmp in filter_params['filter-tags']]
	if 'filter-category' in filter_params and filter_params['filter-category']:
		filter_params['filter-category'] = [str(tmp) for tmp in filter_params['filter-category']]

	return filter_params

def select_from_table(table, page, site=False, filter_tags=None, filter_category=None):
	params = parse_table_args(limit_by_source=site, filter_tags=filter_tags, filter_category=filter_category)

	query = g.session.query(table) \
				.options(joinedload("file"), joinedload("file.hentai_tags_rel"), joinedload("tags_rel"), )

	tags_table = db.MangaTags if table == db.MangaReleases else db.HentaiTags
	# query = query.join(tags_table)
	query = query.join(db.ReleaseFile)
	# query = query.filter( table = AC.id )


	if not params['include-deleted']:
		query = query.filter(table.deleted == False)
	if params['limit-by-source']:
		for source in params['limit-by-source']:
			query = query.filter(table.source_site == source)
	if params['filter-category']:
		for filter_cat in params['filter-category']:
			query = query.filter(table.series_name == filter_cat)

	print("params['filter-tags']", params['filter-tags'])

	if params['filter-tags']:

		for filter_tag in params['filter-tags']:
			print("Adding filter:", tags_table, tags_table.tag, filter_tag, tags_table.tag == filter_tag)
			query = query.filter(filter_tag in table.tags_rel)

	if params['distinct']:
		query = query.distinct(table.series_name)             \
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
						   source_site   = source_site,
						   url_for_param = "hentai_by_site_view"
						   )

@app.route('/hentai/by-tag/<tag>/', methods=['GET'])
@app.route('/hentai/by-tag/<tag>/<int:page>', methods=['GET'])
def hentai_tag_view(tag, page=1):
	params, items = select_from_table(db.HentaiReleases, page=page, filter_tags=tag)
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
	params, items = select_from_table(db.HentaiReleases, page=page, filter_category=category)
	return render_template('hentai_view.html',
						   whole_page    = True,
						   items         = items,
						   params        = params,
						   category      = category,
						   url_for_param = "hentai_category_view"
						   )


