import sys
import json
import logging
from flask import Flask, render_template, jsonify, url_for, request, redirect, abort, g, session
from jinja2 import TemplateNotFound
from sqlalchemy import or_, and_
from app.public import bp
from app.public import search as searchClDb
from app.models import Event, Person
from app.api.web_methods import search_events
from pyuca import Collator 






logger = logging.getLogger('werkzeug')


def get_sidebar():
    if 'sidebar' not in g:
        g.sidebar = searchClDb.SideBarFilters()
        if request.args.get('update') == 'search':
            logger.debug('updating search')
            g.sidebar.updateFromRequest()
    return g.sidebar


# Make some objects available to templates.
@bp.context_processor
def inject_userquery():
    sidebar = get_sidebar()
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

# Clear Cache!
# Necesario porque las cookies me habian quedado gigantes al principio.
@bp.route('/clear')
def clearCache():
    remove = []
    for k in session.keys():
        if '_cache_' in k:
            remove.append(k)
    for k in remove:
        session[k] = ''
    return redirect(url_for('.inicio'))

# Search Result
@bp.route('/list/events')
def get_events():
    # Prepare parameterscurrent_app.app_context 
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int) 

    logger.info([offset, limit])
    query = get_sidebar().query

    results = search_events(
        keywords=query['keywords'], filters=query['filters'], offset=offset, limit=limit)

    # defined by nested function in order to access the list of relevances
    def sortByRelevance(event):
        return results["scores"][event.id]    
    
    if query['keywords']:
        entries =sorted( Event.query.filter(Event.id.in_(results['rows'])).all()\
                        ,key=sortByRelevance,reverse=True)
    else:
        entries = Event.query.filter(Event.id.in_(results['rows'])) \
            .order_by(Event.year,Event.month,Event.day)\
            .all()


    data = {}
    data['total'] = results['total']
    rows = render_template('public/event_table.json',
                           entries=entries, causes=results['events_found_causes'])

    data['rows'] = json.loads(rows.replace("\n", ""),)[:-1]
    return jsonify(data)
    # data['rows'] = render_template('public/event_table.json', entries=entries)
    # return data


    # query = searchClDb.event_list(keywords=keywords, offset=offset, limit=limit)

    # DB result
    # data={ "rows": [], "total":  len(query) }
    # data={ "rows": [], "total":  query.count() }
    # entries=query.limit(limit).offset(offset).all()
    # entries = query[ offset:offset+limit ]

    # # Form JSON for bootstrap-table
    # data['rows'] = json.loads( 
    #     render_template(
    #         'public/event_table_TEST.json',
    #         entries=entries).replace("\n", "")
    #     )[:-1]
    # return jsonify(data)
    

@bp.route('/search')
def search():
    return render_template('public/search.html')
    # query = get_sidebar().query
    # try:
    #     results = search_events(keywords=query['keywords'], filters=query['filters'], offset=0, limit=200)
    # except Exception as e:
    #     import traceback
    #     results = traceback.format_exc()
    # return render_template('public/search.html', query=query, results=results)



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
        collator = Collator() 
        personas = sorted(personas, key=lambda e:  collator.sort_key( e.get_name().upper() ) )
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
            i.person.is_composer = True
            compositores.add(i.person)
            personas.add(i.person)
        else:
            participantes.add(i)
            if i.person:
                personas.add(i.person)

    # Now, iterate in performances to extract other composers
    for p in event.performances:
        for c in p.musical_piece.composers:
            c.is_composer = True
            compositores.add(c)
            personas.add(c)
    collator=Collator()
    compositores = sorted(compositores, key=lambda e: collator.sort_key(e.get_name()))
    participantes = sorted(participantes, key=lambda e: collator.sort_key(e.get_name()))

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

@bp.before_app_first_request
def initialize_cache():
    from config import Config
    from app.api.events_cache import refresh_cache_thread, refresh_cache
    from app import scheduler, current_app

    # we'll set the run interval just little less than the CACHE TIMEOUT to avoid
    # the refresh be > CACHE_TIMEOUT
    logger.debug("initializing cache")
    refresh_cache(True)
    logger.debug("starting refresh thread")
    scheduler.add_job(refresh_cache_thread, 'interval', seconds=Config.CACHE_TIMEOUT-10, args=[current_app._get_current_object()])
    scheduler.start()
