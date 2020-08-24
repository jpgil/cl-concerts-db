import json
import logging
from flask import Flask, render_template, jsonify, url_for, request, redirect, abort
from jinja2 import TemplateNotFound
from sqlalchemy import or_, and_
from app.public import bp
from app.public import search as searchClDb
from app.models import Event, Person


logger = logging.getLogger('werkzeug')


# Make some objects available to templates.
@bp.context_processor
def inject_userquery():
    sidebar = searchClDb.SideBarFilters()
    if request.args.get('update') == 'search':
        logger.info('update search')
        sidebar.updateFromRequest()
    return dict(
        userquery=request.args.get('keywords', default=''),
        filters=sidebar
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


    # query = app.main.search(  # Johnny elige el nombre!!
    #     keywords=keywords,
    #     filter=filter,
    #     offset=offset,
    #     limit=limit)

    # # Ejemplo real de filter
    # keywords = "simple string"
    # filter = {
    #     "start_date": "YYYY-MM-DD", "end_date": "",
    #     "name": "Texts here",
    #     "cycle": [], "type": [], "organized": [], "city": [], "location": [],
    #     "participant_name": [], "participant_gender": [], "participant_country": [], "activity": [],
    #     "instruments": [], "compositor_name": [], "compositor_gender": [], "compositor_country": [],
    #     "premier_type": [], "musical_piece": [], "instrument_type": [], "musical_ensemble_name": [],
    #     "musical_ensemble_type": []
    # }


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


# Catalogo de Personas

@bp.route(('/person/<initial>'))
def person(initial="A"):
    if initial not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return redirect(url_for('.person', initial='A'))

    
    try:
        # Primer intento fallido, hay gente sin apellido
        # personas = Person.query.filter(Person.last_name.ilike(initial + "%")).all()
        personas = Person.query.filter(or_(and_(Person.last_name == '', Person.first_name.ilike(
            initial + "%")), Person.last_name.ilike(initial + "%"))).all()
        personas = sorted(personas, key=lambda e: e.get_name().upper() )
        return render_template('public/person_initial.html', initial=initial, personas=personas)
    except TemplateNotFound:
        abort(404)


# Event Detail

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


# Plain pages
@bp.route('/<page>')
def show(page):
    try:
        return render_template('public/%s.html' % page)
    except TemplateNotFound:
        abort(404)
