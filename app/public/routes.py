import json
from flask import Flask, render_template, jsonify, url_for, request, redirect, abort
from jinja2 import TemplateNotFound
from app.public import bp
from app.public import search as searchClDb

# Make some objects available to templates.
@bp.context_processor
def inject_userquery():
    return dict(
        userquery=request.args.get('keywords', default=''),
        filters = searchClDb.SideBarFilters()
        )

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
from app.models import Event

@bp.route('/event/<id>')
def show_event(id):
    try:
        event = Event.query.filter_by(id=id).first_or_404()
    except:
        abort(404)

    # I need to prefill these variables here to simplify the template
    participantes, compositores, personas = set(), set(), set()
    for i in event.participants:
        if i.person and i.activity.name == "Compositor/a":
            compositores.add(i.person)
            personas.add(i.person)
        else:
            participantes.add(i)
            if i.person:
                personas.add(i.person)

    # Now, iterate in performances to extract other composers
    for p in event.performances:
        for c in p.musical_piece.composers:
            compositores.add(c)
            personas.add(c)

    compositores = sorted(compositores, key=lambda e: e.get_name() )
    participantes = sorted(participantes, key=lambda e: e.get_name() )

    return render_template(
        'public/detalle.html',
        e=event,
        participantes=participantes,
        compositores=compositores,
        personas=personas
    )
    
# def show_event_test(id):
#     # try:
#         event = searchClDb.get_event(id=id)
#         return render_template('public/detalle.html', e=event )
#     # except:
#         # abort(404)

# Plain pages
@bp.route('/<page>')
def show(page):
    try:
        return render_template('public/%s.html' % page)
    except TemplateNotFound:
        abort(404)