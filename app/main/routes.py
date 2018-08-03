from datetime import datetime
import json
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from guess_language import guess_language
from app import db
#from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.main.forms import *
from app.models import *
#from app.translate import translate
from app.main import bp
from flask_uploads import UploadSet, configure_uploads, DEFAULTS, AUDIO, ARCHIVES, IMAGES
import os





def list2csv(some_list):
    return ','.join(map(str, some_list)) 

@bp.route('/favicon.ico')
def hello():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@bp.before_app_request
def before_request():
    pass
#    if current_user.is_authenticated:
#        current_user.last_seen = datetime.utcnow()
#        db.session.commit()
#        g.search_form = SearchForm()
#    g.locale = str(get_locale())
    
def view_elements(dbmodel,elementsname,title):
    page = request.args.get('page', 1, type=int)
    elements = dbmodel.query.order_by(dbmodel.name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('main/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)
    
@bp.route('/view/countries')
@login_required
def view_countries():
    return view_elements(Country,'countries',_('Países'))

@bp.route('/view/eventtypes')
@login_required
def view_eventtypes():
    return view_elements(EventType,'eventtypes',_('Tipos de Eventos'))

@bp.route('/view/event')
@login_required
def view_event():
    return view_elements(Event,'events',_('Eventos'))

@bp.route('/view/cities')
@login_required
def view_cities():
    return view_elements(City,'cities',_('Ciudades'))

@bp.route('/view/instrumenttypes')
@login_required
def view_instrumenttypes():
    return view_elements(InstrumentType,'instrumenttypes',_('Tipos de Instrumento'))

@bp.route('/view/premieretypes')
@login_required
def view_premieretypes():
    return view_elements(PremiereType,'premieretypes',_('Tipos de Estreno'))

@bp.route('/view/instruments')
@login_required
def view_instruments():
    return view_elements(Instrument,'instruments',_('Instrumentos'))

@bp.route('/view/activities')
@login_required
def view_activities():
    return view_elements(Activity,'activities',_('Actividades'))



@bp.route('/view/locations')
@login_required
def view_locations():
    return view_elements(Location,'locations',_('Lugares'))

@bp.route('/view/organizations')
@login_required
def view_organizations():
    return view_elements(Organization,'organizations',_('Organizaciones'))


@bp.route('/view/people')
@login_required
def view_people():
    elementsname='people'
    title=_('Personas')
    page = request.args.get('page', 1, type=int)
    elements = Person.query.order_by(Person.last_name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('main/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/view/musicalpieces')
@login_required
def view_musicalpieces():
    elementsname='musicalpieces'
    title=_('Obras Musicales')
    page = request.args.get('page', 1, type=int)
    elements = MusicalPiece.query.order_by(MusicalPiece.name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('main/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)


def getItemList(dbmodel,q,page):    
    itemslist=db.session.query(dbmodel).filter(dbmodel.name.ilike(q+'%')).order_by(dbmodel.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        data["results"].append( { 'id' : item.id , 'text': item.name} )
    return jsonify(data)

def getItem(dbmodel,id):
    item=dbmodel.query.filter_by(id=id).first_or_404()
    data={ 'id' : item.id , 'text': item.name }
    return jsonify(data)

def getPeople(q,page):    
    itemslist=db.session.query(Person).filter(Person.last_name.ilike(q+'%')).order_by(Person.last_name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        text = item.get_full_name()
        data["results"].append( { 'id' : item.id , 'text': text } )
    return jsonify(data)

def getPerson(id):
    item=Person.query.filter_by(id=id).first_or_404()
    text = item.get_full_name()
    data={ 'id' : item.id , 'text': text }
    return jsonify(data)

def getMusicalPiece(id):
    item=MusicalPiece.query.filter_by(id=id).first_or_404()
    text = '{} ({})'.format(item.name, item.composer.get_full_name())
    data={ 'id' : item.id , 'text': text }
    return jsonify(data)

def getMusicalPieces(q,page):    
    itemslist=db.session.query(MusicalPiece).filter(MusicalPiece.name.ilike(q+'%')).order_by(MusicalPiece.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        text = '{} ({})'.format(item.name, item.composer.get_full_name())
        data["results"].append( { 'id' : item.id , 'text': text } )
    return jsonify(data)

@bp.route('/list/people')
def getPeopleList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getPeople(q,page)

@bp.route('/list/people/<id>')
def getPeopleItem(id):
    return getPerson(id)


@bp.route('/list/countries')
def getCountryList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Country,q,page)

@bp.route('/list/countries/<id>')
def getCountryItem(id):
    return getItem(Country,id)


@bp.route('/list/eventtypes')
def getEventTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(EventType,q,page)

@bp.route('/list/eventtypes/<id>')
def getEventTypeItem(id):
    return getItem(EventType,id)


@bp.route('/list/events')
def getEventList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Event,q,page)

@bp.route('/list/events/<id>')
def getEventItem(id):
    return getItem(Event,id)

@bp.route('/list/cities')
def getCityList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(City,q,page)

@bp.route('/list/cities/<id>')
def getCityItem(id):
    return getItem(City,id)

@bp.route('/list/organizations')
def getOrganizationList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Organization,q,page)

@bp.route('/list/organizations/<id>')
def getOrganizationItem(id):
    return getItem(Organization,id)

@bp.route('/list/instrumenttypes')
def getInstrumentTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(InstrumentType,q,page)

@bp.route('/list/instrumenttypes/<id>')
def getInstrumentTypeItem(id):
    return getItem(InstrumentType,id)

@bp.route('/list/instruments')
def getInstrumentList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Instrument,q,page)

@bp.route('/list/instruments/<id>')
def getInstrumentItem(id):
    return getItem(Instrument,id)

@bp.route('/list/musicalpieces')
def getMusicalPieceList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getMusicalPieces(q,page)

@bp.route('/list/mmusicalpieces/<id>')
def getMusicalPieceItem(id):
    return getMusicalPiece(id)

@bp.route('/list/locations')
def getLocationList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Location,q,page)

@bp.route('/list/locations/<id>')
def getLocationItem(id):
    return getItem(Location,id)

@bp.route('/list/activities')
def getActivityList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Activity,q,page)

@bp.route('/list/activities/<id>')
def getActivityItem(id):
    return getItem(Activity,id)


@bp.route('/list/premieretypes')
def getPremiereTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(PremiereType,q,page)

@bp.route('/list/premieretypes/<id>')
def getPremiereTypeItem(id):
    return getItem(PremiereType,id)

@bp.route('/listtable/participants/<event_id>')
def getParticipantsListTable(event_id):
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        participants=event.participants.order_by(Participant.person_id).all()
        for participant in participants:
            data["rows"].append({ 'name': participant.person.get_full_name(),
                'activity': participant.activity.name,
                'id': participant.id, 
                'text': '{} ({})'.format(participant.person.get_full_name(),participant.activity.name) })
        data["total"]=participants.__len__() 
    return jsonify(data)

@bp.route('/listtable/medialink/<event_id>')
def getMediaLinkListTable(event_id):
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        medialinks=event.medialinks.order_by(MediaLink.filename).all()
        for file in medialinks:
            (path,filename)=os.path.split(file.filename)
            data["rows"].append({ 'filename': filename ,
                'description': file.description,
                'id': file.id, 
                'type': file.mime_type,
                'url': file.url })
        data["total"]=medialinks.__len__() 
    return jsonify(data)

@bp.route('/list/participants/<event_id>')
def getParticipantsList(event_id):
    data={ "results": [], "pagination": { "more": False} }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        participants=event.participants.order_by(Participant.person_id).all()
        for participant in participants:
            data["results"].append({ 'name': participant.person.get_full_name(),
                'activity': participant.activity.name,
                'id': participant.id, 
                'text': '{} ({})'.format(participant.person.get_full_name(),participant.activity.name) })
    return jsonify(data)


@bp.route('/listtable/performances/<event_id>')
def getPerformancesListTable(event_id):
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        performances=event.performances.order_by(Performance.musical_piece_id).all()
        for performance in performances:
            premiere_type_string=' [{}] '.format(performance.premiere_type.name) if performance.premiere_type.name != 'No' else ''                
            data["rows"].append({ 'text': '{}«{}» ({})'.format(premiere_type_string, 
                                                    performance.musical_piece.name,
                                                    performance.musical_piece.composer.get_full_name()),
                                   'id':performance.id})
        data["total"]=performances.__len__() 
    return jsonify(data)

@bp.route('/list/performances/<event_id>')
def getPerformancesList(event_id):
    data={ "results": [], "pagination": { "more": False} }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        performances=event.performances.order_by(Performance.musical_piece_id).all()
        for performance in performances:
            #premiere_type_string='[{}] '.format(performance.premiere_type.name) if performance.premiere_type.name != 'No' else ''                
            data["results"].append({ 'text': '«{}» ({})'.format(
                            performance.musical_piece.name,
                            performance.musical_piece.composer.get_full_name()),'id':performance.id})
    return jsonify(data)



@bp.route('/listtable/performancesdetails/<event_id>') 
def getPerformanceDetailList(event_id):
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    total=0
    if event:
       
        performances=event.performances.order_by(Performance.musical_piece_id).all()
        for performance in performances:
            for participant in performance.participants:
                total=total+1
                performance_name='«{}» ({}) '.format(performance.musical_piece.name,performance.musical_piece.composer.get_full_name())
                participant_name=participant.person.get_full_name()
                participant_activity=participant.activity.name
                data["rows"].append({ 'performance_name': performance_name,
                                  'participant_name': participant_name, 
                                  'participant_activity': participant_activity,
                                  'performance_participant_id': '{},{}'.format(performance.id,participant.id) })
    data["total"]=total
    return jsonify(data)
    
def EditSimpleElement(dbmodel,title,original_name):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    db_element = dbmodel.query.filter_by(name=original_name).first_or_404()
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name=original_name)
    if form.validate_on_submit():
        db_element.name = form.name.data
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = original_name
    return render_template('main/edit_simple_element.html',title=title,form=form)


@bp.route('/edit/country/<country>',methods = ['GET','POST'])
@login_required
def EditCountry(country):
    return EditSimpleElement(Country,_('Editar País'),country)


@bp.route('/edit/eventtype/<event_type>',methods = ['GET','POST'])
@login_required
def EditEventType(event_type):
    return EditSimpleElement(EventType,_('Editar Tipo de Evento'),event_type)

 
@bp.route('/edit/city/<city>',methods = ['GET','POST'])
@login_required
def EditCity(city):
    return EditSimpleElement(City,_('Editar Ciudad'),city)


@bp.route('/edit/instrumenttype/<instrumenttype>',methods = ['GET','POST'])
@login_required
def EditInstrumentType(instrumenttype):
    return EditSimpleElement(InstrumentType,_('Editar Tipo de Instrumento'),instrumenttype) 

@bp.route('/edit/premieretype/<premieretype>',methods = ['GET','POST'])
@login_required
def EditPremiereType(premieretype):
    return EditSimpleElement(PremiereType,_('Editar Tipo de Instrumento'),premieretype) 

def NewSimpleElement(dbmodel,title):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name='')   
    if form.validate_on_submit():
        if  dbmodel.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
        else:
            db.session.add(dbmodel(name=form.name.data))
            flash(_('Tus cambios han sido guardados.'),'info') 
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/edit_simple_element.html',title=title,form=form)
 
@bp.route('/new/country', methods = ['GET','POST'])
@login_required
def NewCountry():
    return NewSimpleElement(Country,_('Agregar País'))

@bp.route('/new/eventtype', methods = ['GET','POST'])
@login_required
def NewEventType():
    return NewSimpleElement(EventType,_('Agregar Tipo de Evento'))

@bp.route('/new/city', methods = ['GET','POST'])
@login_required
def NewCity():
    return NewSimpleElement(City,_('Agregar Ciudad'))

@bp.route('/new/instrumenttype', methods = ['GET','POST'])
@login_required
def NewInstrumentType():
    return NewSimpleElement(InstrumentType,_('Agregar Tipo de Instrumento'))
    
@bp.route('/new/premieretype', methods = ['GET','POST'])
@login_required
def NewPremiereType():
    return NewSimpleElement(PremiereType,_('Agregar Tipo de Estreno'))

@bp.route('/editelements')
@login_required
def edit_elements():
    return render_template('main/edit_elements.html')    

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
  return render_template('main/index.html',user=current_user.first_name)


@bp.route('/new/instrument', methods = ['GET','POST'])
@login_required
def NewInstrument():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditInstrumentForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Instrument.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editinstrument.html',form=form,title=_('Agregar Instrumento'),selectedElements=None)
        else:
            instrument_type = InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first_or_404()
            db.session.add(Instrument(name=form.name.data,instrument_type=instrument_type))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editinstrument.html',form=form,title=_('Agregar Instrumento'),selectedElements=None)

@bp.route('/edit/instrument/<instrument>', methods = ['GET','POST'])
@login_required
def EditInstrument(instrument):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    instrument = Instrument.query.filter_by(name=instrument).first_or_404()
    selectedElements=[]
    selectedElements.append(instrument.instrument_type.id)
    form = EditInstrumentForm(original_name=instrument.name)
    if form.validate_on_submit():
         instrument.name = form.name.data
         instrument_type = InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first_or_404()
         instrument.instrument_type = instrument_type
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = instrument.name            
    return render_template('main/editinstrument.html',form=form,title=_('Editar Instrumento'),selectedElements=list2csv(selectedElements))    

@bp.route('/new/musicalpiece', methods = ['GET','POST'])
@login_required
def NewMusicalPiece():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditMusicalPieceForm(dbmodel=MusicalPiece,original_name='')   
    if form.validate_on_submit():
        if  MusicalPiece.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editmusicalpiece.html',form=form,title=_('Agregar Obra Musical'),selectedElements=None)
        else:
            composer = Person.query.filter_by(id=int(form.composer.data[0])).first_or_404()
            db.session.add(MusicalPiece(name=form.name.data,composer=composer,composition_year=form.composition_year.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editmusicalpiece.html',form=form,title=_('Agregar Obra Musical'),selectedElements=None)

@bp.route('/edit/musicalpiece/<id>', methods = ['GET','POST'])
@login_required
def EditMusicalPiece(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    musical_piece = MusicalPiece.query.filter_by(id=id).first_or_404()
    selectedElements=[]
    selectedElements.append(musical_piece.composer.id)
    form = EditMusicalPieceForm(original_name=musical_piece.name)
    if form.validate_on_submit():
         musical_piece.name = form.name.data
         composer = Person.query.filter_by(id=int(form.composer.data[0])).first_or_404()
         musical_piece.composer = composer
         musical_piece.composition_year = form.composition_year.data
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = musical_piece.name  
        form.composition_year.data = musical_piece.composition_year
    return render_template('main/editmusicalpiece.html',form=form,title=_('Editar Obra Musical'),selectedElements=list2csv(selectedElements))    


@bp.route('/new/activity', methods = ['GET','POST'])
@login_required
def NewActivity():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditActivityForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Activity.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editactivity.html',form=form,title=_('Agregar Actividad'),selectedElements=None)
        else:
            instrument = Instrument.query.filter_by(id=int(form.instrument.data[0])).first_or_404()
            db.session.add(Activity(name=form.name.data,instrument=instrument))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editactivity.html',form=form,title=_('Agregar Actividad'),selectedElements=None)

@bp.route('/edit/activity/<id>', methods = ['GET','POST'])
@login_required
def EditActivity(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    original_activity= Activity.query.filter_by(id=id).first_or_404()
    selectedElements=[]
    selectedElements.append(original_activity.instrument.id)
    form = EditActivityForm(original_name=original_activity.name)
    if form.validate_on_submit():
         original_activity.name = form.name.data
         instrument = Instrument.query.filter_by(id=int(form.instrument.data[0])).first_or_404()
         original_activity.instrument = instrument
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = original_activity.name
    return render_template('main/editactivity.html',form=form,title=_('Editar Actividad'),selectedElements=list2csv(selectedElements))    



@bp.route('/new/location', methods = ['GET','POST'])
@login_required
def NewLocation():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditLocationForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Location.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editlocation.html',form=form,title=_('Agregar Lugar'),selectedElements=None)
        else:
            city = City.query.filter_by(id=int(form.city.data[0])).first_or_404()
            db.session.add(Location(name=form.name.data,city=city,additional_info=form.additional_info.data,address=form.address.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editlocation.html',form=form,title=_('Agregar Lugar'),selectedElements=None)

@bp.route('/edit/location/<location>', methods = ['GET','POST'])
@login_required
def EditLocation(location):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    original_location = Location.query.filter_by(name=location).first_or_404()
    selectedElements=[]
    selectedElements.append(original_location.city.id)
    form = EditLocationForm(original_name=location)
    if form.validate_on_submit():
         original_location.name = form.name.data
         original_location.additional_info=form.additional_info.data
         original_location.address=form.address.data
         city = City.query.filter_by(id=int(form.city.data[0])).first_or_404()
         original_location.city = city
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = original_location.name
        form.additional_info.data = original_location.additional_info
        form.address.data = original_location.address
    return render_template('main/editlocation.html',form=form,title=_('Editar Lugar'),selectedElements=list2csv(selectedElements))    

@bp.route('/new/organization', methods = ['GET','POST'])
@login_required
def NewOrganization():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditOrganizationForm(dbmodel=Organization,original_name='')   
    if form.validate_on_submit():
        if  Organization.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editorganization.html',form=form,title=_('Agregar Organización'))
        else:
            db.session.add(Organization(name=form.name.data,additional_info=form.additional_info.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editorganization.html',form=form,title=_('Agregar Organización'))

@bp.route('/edit/organizatioeventn/<organization>', methods = ['GET','POST'])
@login_required
def EditOrganization(organization):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    original_organization =Organization.query.filter_by(name=organization).first_or_404()
    form = EditOrganizationForm(original_name=organization)
    if form.validate_on_submit():
         original_organization.name = form.name.data
         original_organization.additional_info=form.additional_info.data
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = original_organization.name
        form.additional_info.data = original_organization.additional_info
    return render_template('main/editorganization.html',form=form,title=_('Editar Organización'))    


@bp.route('/new/person', methods = ['GET','POST'])
@login_required
def NewPerson():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditPersonForm(original_person=None)   
    if form.validate_on_submit():
        person = Person(first_name=form.first_name.data,last_name=form.last_name.data)
        person.birth_date = form.birth_date.data
        person.death_date = form.death_date.data
        person.biography= form.biography.data
        for country_id in form.nationalities.data:
            person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
        db.session.add(person)
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editperson.html',form=form,title=_('Agregar Persona'),selectedElements=None)

@bp.route('/edit/person/<person_id>', methods = ['GET','POST'])
@login_required
def EditPerson(person_id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    person = Person.query.filter_by(id=person_id).first_or_404()
    form = EditPersonForm(person)
    selectedElements=[]
    for nationality in person.nationalities:
        selectedElements.append(nationality.id)
    if form.validate_on_submit():
         person.first_name = form.first_name.data
         person.last_name = form.last_name.data
         person.birth_date = form.birth_date.data
         person.death_date = form.death_date.data
         person.biography= form.biography.data
         person.nationalities.clear()
         for country_id in form.nationalities.data:
             person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
         form.first_name.data = person.first_name
         form.last_name.data = person.last_name
         form.birth_date.data = person.birth_date
         form.death_date.data = person.death_date
         form.biography.data = person.biography
    return render_template('main/editperson.html',form=form,title=_('Editar Persona'),selectedElements=list2csv(selectedElements))    


@bp.route('/new/event', methods = ['GET','POST'])
@login_required
def NewEvent():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))
    form = EditEventForm(dbmodel=Event,original_event=None)   
    if form.validate_on_submit():
        if  Event.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/newevent.html',form=form,title=_('Agregar Evento'),
                                   selectedEventTypes=list2csv(form.event_type.data), 
                                   selectedLocation=list2csv(form.location.data),
                                   selectedOrganization=list2csv(form.organization.data))
        else:
            location = Location.query.filter_by(id=int(form.location.data[0])).first_or_404()
            organization = Organization.query.filter_by(id=int(form.organization.data[0])).first_or_404()
            event_type = EventType.query.filter_by(id=int(form.event_type.data[0])).first_or_404()
            newevent=Event(name=form.name.data,
                                 organization=organization,
                                 location=location,
                                 event_type=event_type,
                                 information=form.information.data,
                                 date=form.event_date.data)
            db.session.add(newevent)
            db.session.commit()
            return render_template('main/editevent.html',event_id=newevent.id,form=form,title=_('Agregar Evento'),
                                   selectedEventTypes=list2csv(form.event_type.data), 
                                   selectedLocation=list2csv(form.location.data),
                                   selectedOrganization=list2csv(form.organization.data))
            flash(_('Tus cambios han sido guardados.'),'info')
    return render_template('main/newevent.html',form=form,title=_('Agregar Evento'),
                           selectedEventTypes=None,
                           selectedLocation=None,
                           selectedOrganization=None)

@bp.route('/edit/event/<event_id>', methods = ['GET','POST'])
@login_required
def EditEvent(event_id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return render_template(url_for('users.login'))

    original_event=Event.query.filter_by(id=event_id).first_or_404()
    form = EditEventForm(dbmodel=Event,original_event=original_event)       
    if form.validate_on_submit():
        if  Event.query.filter_by(name=form.name.data).all().__len__() > 0 and (original_event.name  != form.name.data):
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editevent.html',event_id=event_id,form=form,title=_('Editar Evento'))
#                                   selectedEventTypes=list2csv([form.event_type.data)], 
#                                   selectedLocation=list2csv([form.location.data]),
#                                   selectedOrganization=list2csv([form.organization.data]))
        else:
            # the next 3 lines is for checking the values actually exists
            Location.query.filter_by(id=int(form.location.data[0])).first_or_404()
            Organization.query.filter_by(id=int(form.organization.data[0])).first_or_404()
            EventType.query.filter_by(id=int(form.event_type.data[0])).first_or_404()
            original_event.name=form.name.data
            original_event.organization_id=form.organization.data
            original_event.location_id=form.location.data
            original_event.event_type_id=form.event_type.data
            original_event.information=form.information.data
            original_event.date=form.event_date.data
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
            return render_template('main/editevent.html',event_id=event_id,form=form,title=_('Editar Evento'),
                                   selectedEventType=list2csv(form.event_type.data[0]), 
                                   selectedLocation=list2csv(form.location.data[0]),
                                   selectedOrganization=list2csv(form.organization.data[0]))

    else:
        form.name.data=original_event.name
        form.event_date.data=original_event.date
        form.information.data=original_event.information
        return render_template('main/editevent.html',event_id=event_id,form=form,title=_('Editar Evento'),
                           selectedEventType=list2csv([original_event.event_type_id]),
                           selectedLocation=list2csv([original_event.location_id]),
                           selectedOrganization=list2csv([original_event.organization_id]))
    

        



#
#@bp.route('/search')
#@login_required
#def search():
#    if not g.search_form.validate():
#        return redirect(url_for('main.explore'))
#    page = request.args.get('page', 1, type=int)
#    posts, total = Post.search(g.search_form.q.data, page,
#                               current_app.config['POSTS_PER_PAGE'])
#    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
#        if total > page * current_app.config['POSTS_PER_PAGE'] else None
#    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
#        if page > 1 else None
#    return render_template('search.html', title=_('Search'), posts=posts,
#                           next_url=next_url, prev_url=prev_url)
