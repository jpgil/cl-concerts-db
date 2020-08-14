import json
from app.public import bp
from flask import Flask, render_template, jsonify, url_for, request, redirect, abort
from jinja2 import TemplateNotFound

import app.public.search as searchClDb

# Make some objects available to templates.
@bp.context_processor
def inject_userquery():
    return dict(userquery=request.args.get('keywords', default=''))

# Defaults to Start Page
@bp.route('/')
def index():
    return redirect(url_for('.inicio'))

# Start Page
@bp.route('/inicio')
def inicio():
    return render_template('public/inicio.html')

# Search Result
@bp.route('/list/events')
def get_events():
    # Prepare parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    keywords = request.args.get('keywords', '', type=str)
    query = searchClDb.event_list(keywords=keywords, offset=offset, limit=limit)

    # DB result
    data={ "rows": [], "total":  len(query) }
    # data={ "rows": [], "total":  query.count() }
    # entries=query.limit(limit).offset(offset).all()
    entries = query[ offset:offset+limit ]

    # Form JSON for bootstrap-table
    data['rows'] = json.loads( 
        render_template('public/event_table_TEST.json', entries=entries).replace("\n", "")
        )[:-1]
    return data
@bp.route('/search')
def search():
    return render_template('public/search.html')


# Event Detail
@bp.route('/event/<id>')
def show_event(id):
    pass

# Plain pages
@bp.route('/<page>')
def show(page):
    try:
        return render_template('public/%s.html' % page)
    except TemplateNotFound:
        abort(404)
