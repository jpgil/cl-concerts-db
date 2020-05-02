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
from sqlalchemy import or_, and_
from werkzeug.local import LocalProxy
import os

log = LocalProxy(lambda: current_app.logger)


def list2csv(some_list):
    return ','.join(map(str, some_list)) 

def addHistoryEntry(operation,description):
    db.session.add(History(
            user_id=current_user.id,
            timestamp=datetime.now(),
            operation=operation,
            description=description))

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
 
def getStringForModel(model):
    string4model={  'Instrument'      :  _('Instrumentos'),
                    'Country'         :  _('Países'),
                    'EventType'       :  _('Tipo de Evento'),
                    'Cycle'           :  _('Ciclos'),
                    'Event'           :  _('Eventos'),
                    'City'            :  _('Ciudades'),
                    'InstrumentType'  :  _('Tipos de Instrumento'),
                    'PremiereType'    :  _('Tipos de Estreno'),
                    'Activity'        :  _('Actividades'),
                    'Location'        :  _('Lugares'),
                    'Organization'    :  _('Organizaciones'),
                    'Person'          :  _('Personas'),
                    'Participant'     :  _('Participante'),
                    'MediaLink'       :  _('Archivo'),
                    'MusicalPiece'    :  _('Obras Musicales'),
                    'MusicalEnsemble'     :  _('Agrupaciones Musicales'),
                    'MusicalEnsembleType' :  _('Tipo de Agrupaciones Musicales'),
                    'Performance'     : _('Participación'),
                    'MusicalEnsembleMember' : _('Miembro de Agrupación Musical')                    
                    }    
    return string4model[model]

@bp.route('/view/element/<model>')
@login_required
def viewElement(model):
    return render_template('main/showlist.html', title=getStringForModel(model),model=model)    

    
@bp.route('/view/history')
@login_required
def viewHistory():
    return render_template('main/history.html')

def getItemList(dbmodel,q,page):    
    itemslist=db.session.query(dbmodel).filter(dbmodel.name.ilike('%'+q+'%')).order_by(dbmodel.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        data["results"].append( { 'id' : item.id , 'text': item.name} )
    return jsonify(data)

def getItem(dbmodel,id):
    item=dbmodel.query.filter_by(id=id).first()
    data={} if not item else { 'id' : item.id , 'text': item.name }
    return jsonify(data)

def getPeople(q,page):    
    itemslist=db.session.query(Person).filter(or_(Person.last_name.ilike('%'+q+'%'),Person.first_name.ilike('%'+q+'%'))).order_by(Person.last_name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        text = item.get_name()
        data["results"].append( { 'id' : item.id , 'text': text } )
    return jsonify(data)

def getPerson(id):
    item=Person.query.filter_by(id=id).first()
    data={} if not item else { 'id' : item.id , 'text': item.get_name() }
    return jsonify(data)

def getMusicalPiece(id):
    item=MusicalPiece.query.filter_by(id=id).first()
    data={} if not item else { 'id' : item.id , 'text': '{}'.format(item.get_name()) }
    return jsonify(data)

def getMusicalPieces(q,page):    
    itemslist=db.session.query(MusicalPiece).filter(MusicalPiece.name.ilike('%'+q+'%')).order_by(MusicalPiece.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        text = '{}'.format(item.get_name())
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

@bp.route('/list/cycles')
def getCycleList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Cycle,q,page)

@bp.route('/list/cycles/<id>')
def getCycleItem(id):
    return getItem(Cycle,id)



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

@bp.route('/list/musicalensembletypes')
def getMusicalEnsembleTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(MusicalEnsembleType,q,page)

@bp.route('/list/musicalensembletypes/<id>')
def getMusicalEnsembleTypeItem(id):
    return getItem(MusicalEnsembleType,id)

@bp.route('/list/instruments')
def getInstrumentList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Instrument,q,page)

@bp.route('/list/instruments/<id>')
def getInstrumentItem(id):
    return getItem(Instrument,id)

@bp.route('/list/musicalensembles')
def getMusicalEnsembleList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(MusicalEnsemble,q,page)

@bp.route('/list/musicalensembles/<id>')
def getMusicalEnsembleItem(id):
    return getItem(MusicalEnsemble,id)

@bp.route('/list/musicalpieces')
def getMusicalPieceList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getMusicalPieces(q,page)

@bp.route('/list/mmusicalpieces/<id>')
def getMusicalPieceItem(id):
    return getMusicalPiece(id)

@bp.route('/list/genders')
def getGenderList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Gender,q,page)

@bp.route('/list/genders/<id>')
def getGenderItem(id):
    return getItem(Gender,id)


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
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        data["total"]=event.participants.count()
        participants=event.participants.order_by(Participant.person_id).limit(limit).offset(offset).all()
        for participant in participants:
            data["rows"].append({ 'name': participant.get_short_name(),
                'activity': participant.activity.name if participant.activity else '',
                'id': participant.id, 
                'text': '{} '.format(participant.get_name()) })
    return jsonify(data)

@bp.route('/listtable/musicalensemblemembers/<musical_ensemble_id>')
def getMusicalEnsembleMemberListTable(musical_ensemble_id):
    data={ "rows": [], "total": 0 }
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    musical_ensemble=MusicalEnsemble.query.filter_by(id=musical_ensemble_id).first()
    if musical_ensemble:
        data["total"]=musical_ensemble.members.count() 
        members=musical_ensemble.members.order_by(MusicalEnsembleMember.id).limit(limit).offset(offset).all()
        for member in members:
            data["rows"].append({ 'name': member.person.get_name() if member.person else '',
                'activity': member.activity.name if member.activity else '',
                'id': member.id, 
                'text': '{}'.format(member.get_name()) })      
    return jsonify(data)


@bp.route('/listtable/medialink/<event_id>')
def getMediaLinkListTable(event_id):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        data["total"]=event.medialinks.count()
        medialinks=event.medialinks.order_by(MediaLink.filename).limit(limit).offset(offset).all()
        for file in medialinks:
            (path,filename)=os.path.split(file.filename)
            data["rows"].append({ 'filename': filename ,
                'description': file.description,
                'id': file.id, 
                'type': file.mime_type,
                'url': file.url })
    return jsonify(data)

@bp.route('/list/participants/<event_id>')
def getParticipantsList(event_id):
    data={ "results": [], "pagination": { "more": False} }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        participants=event.participants.order_by(Participant.person_id).all()
        for participant in participants:
            data["results"].append({ 'name': participant.get_short_name(),
                'activity': participant.activity.name if participant.activity else '',
                'id': participant.id, 
                'text': '{} '.format(participant.get_name()) })
    return jsonify(data)

@bp.route('/list/eventsofmember/<musical_ensemble_member_id>')
def getListOfEventsForEnsembleMemberId(musical_ensemble_member_id):
    data={ 'events': [] }
    musical_ensemble_member=MusicalEnsembleMember.query.filter_by(id=musical_ensemble_member_id).first()
    if musical_ensemble_member:
        participants=Participant.query.filter(and_(Participant.musical_ensemble_id == musical_ensemble_member.musical_ensemble_id,
                                                    Participant.person_id == musical_ensemble_member.person_id,
                                                    Participant.activity_id == musical_ensemble_member.activity_id))
        for participant in participants:
            data['events'].append(participant.event.get_name())
    return jsonify(data)
      

@bp.route('/list/musicalensemblemembers/<musical_ensemble_id>')
def getMusicalEnsembleMemberList(musical_ensemble_id):
    data={ "results": [], "pagination": { "more": False} }
    musical_ensemble=MusicalEnsemble.query.filter_by(id=musical_ensemble_id).first()
    if musical_ensemble:
        members=musical_ensemble.memebers.order_by(MusicalEnsembleMember.person_id).all()
        for member in members:
            data["results"].append({ 
                'name': member.person.get_name(),
                'activity': member.activity.name if participant.activity else '',
                'id': member.id, 
                'text': '{} ({})'.format(member.person.get_name(),member.activity.name if member.activity else '') })
    return jsonify(data)

@bp.route('/listtable/performances/<event_id>')
def getPerformancesListTable(event_id):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        data["total"] = event.performances.count()
        performances=event.performances.order_by(Performance.musical_piece_id).limit(limit).offset(offset).all()
        for performance in performances:
            premiere_type_string=' [{}] '.format(performance.premiere_type.name) if performance.premiere_type.name != 'No' else ''                
            data["rows"].append({ 'text': '{} {} '.format(premiere_type_string, 
                                                    performance.musical_piece.get_name()),
                                   'id':performance.id})
    return jsonify(data)


@bp.route('/listtable/historytable')
def getHistoryTable():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    order = request.args.get('order', '', type=str)
    search = request.args.get('search', '', type=str)
    
    query=History.query.filter(History.description.ilike('%{}%'.format(search)))
    data={ "rows": [], "total":  query.count() }
    if order.upper() == 'ASC':
        entries=query.order_by(History.timestamp.asc()).limit(limit).offset(offset).all()
    else:
        entries=query.order_by(History.timestamp.desc()).limit(limit).offset(offset).all()
    for entry in entries:
        data["rows"].append({ "user" : "{} {}".format(entry.user.first_name,entry.user.last_name),
                              "datetime" : entry.timestamp.isoformat(),
                              "operation" : entry.operation,
                              "description" : entry.description })
    return jsonify(data)    

def getTableData(requests,dbmodel,searchables):
    edit_button_string='<a href="{}" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></a>'
    delete_button_string='<a onclick="checkDeleteElement(\'{}\',\'{}\')" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a>'

    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    order = request.args.get('order', '', type=str)
    search = request.args.get('search', '', type=str)
    filters=[]
    for field in searchables:
        filters.append(field.ilike('%{}%'.format(search)))
    query=dbmodel.query.filter(or_(*filters))
    data={ "rows": [], "total":  query.count() }
    entries=query.limit(limit).offset(offset).all()
    for entry in entries:
        data["rows"].append({ "name" : entry.get_name(),
                              "editlink" : edit_button_string.format(url_for('main.Edit{}'.format(dbmodel.__name__),id=entry.id)),
                              "deletelink" : delete_button_string.format(dbmodel.__name__,entry.id)
                             })
    return jsonify(data)  

def getMusicalPieceTableData(requests):
    button_string='<a href="{}" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></a>'
    delete_button_string='<a onclick="checkDeleteElement(\'{}\',\'{}\')" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a>'

    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    order = request.args.get('order', '', type=str)
    search = '%{}%'.format(request.args.get('search', '', type=str))
    query=MusicalPiece.query.outerjoin(Person,MusicalPiece.composers).filter(or_(MusicalPiece.composers.any(or_(Person.first_name.ilike(search),
                                                                       Person.last_name.ilike(search))),MusicalPiece.name.ilike(search)))
    data={ "rows": [], "total":  query.count() }
    entries=query.limit(limit).offset(offset).all()
    for entry in entries:
        data["rows"].append({ "name" : entry.get_name(),
                              "editlink" : button_string.format(url_for('main.EditMusicalPiece',id=entry.id)),
                               "deletelink" : delete_button_string.format('MusicalPiece',entry.id)
                             })
    return jsonify(data)  

def getEventTableData(requests):
    button_string='<a href="{}" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></a>'
    delete_button_string='<a onclick="checkDeleteElement(\'{}\',\'{}\')" class="btn btn-default btn-sm" role="button"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a>'

    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    order = request.args.get('order', '', type=str)
    search = '{}'.format(request.args.get('search', '', type=str))    
    
    or_search_term=[]
    for search_term in search.split(' '):
        filters = []
        if search_term.isnumeric():
            filters.append(Event.year.contains(str(int(search_term))))
            filters.append(Event.month.contains(str(int(search_term))))
            filters.append(Event.day.contains(str(int(search_term))))
        filters.append(EventType.name.contains(search_term))
        filters.append(Event.name.contains(search_term))
        filters.append(Location.name.contains(search_term))
        or_search_term.append(or_(*filters))
    
        
    query=db.session.query(Event).join(EventType,Event.event_type).join(Location,Event.location).filter(and_(*or_search_term))    
    data={ "rows": [], "total":  query.count() }
    entries=query.limit(limit).offset(offset).all()
    for entry in entries:
        data["rows"].append({ "name" : entry.get_name(),
                              "editlink" : button_string.format(url_for('main.EditEvent',event_id=entry.id)),
                               "deletelink" : delete_button_string.format('Event',entry.id)
                             })
    return jsonify(data)  


@bp.route('/listtable/Instrument')
def getInstrumentTable():
    return getTableData(request,Instrument,[Instrument.name])

@bp.route('/listtable/Country')
def getCountryTable():
    return getTableData(request,Country,[Country.name])  

@bp.route('/listtable/EventType')
def getEventTypeTable():
    return getTableData(request,EventType,[EventType.name])  

@bp.route('/listtable/Cycle')
def getCycleTable():
    return getTableData(request,Cycle,[Cycle.name])  

@bp.route('/listtable/Event')
def getEventTable():
    return getEventTableData(request)  

@bp.route('/listtable/City')
def getCityTable():
    return getTableData(request,City,[City.name])  

@bp.route('/listtable/InstrumentType')
def getInstrumentTypeTable():
    return getTableData(request,InstrumentType,[InstrumentType.name])  

@bp.route('/listtable/MusicalEnsemble')
def getMusicalEnsembleTable():
    return getTableData(request,MusicalEnsemble,[MusicalEnsemble.name])  

@bp.route('/listtable/MusicalEnsembleType')
def getMusicalEnsembleTypeTable():
    return getTableData(request,MusicalEnsembleType,[MusicalEnsembleType.name])  

@bp.route('/listtable/PremiereType')
def getPremiereTypeTable():
    return getTableData(request,PremiereType,[PremiereType.name])  

@bp.route('/listtable/Location')
def getLocationTable():
    return getTableData(request,Location,[Location.name])  

@bp.route('/listtable/Organization')
def getOrganizationTable():
    return getTableData(request,Organization,[Organization.name])  

@bp.route('/listtable/Activity')
def getActivityTable():
    return getTableData(request,Activity,[Activity.name])  

@bp.route('/listtable/Person')
def getPersonTable():
    return getTableData(request,Person,[Person.first_name, Person.last_name])  

@bp.route('/listtable/MusicalPiece')
def getMusicalPieceTable():
    return getMusicalPieceTableData(request)
    
   
@bp.route('/list/performances/<event_id>')
def getPerformancesList(event_id):
    data={ "results": [], "pagination": { "more": False} }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        performances=event.performances.order_by(Performance.musical_piece_id).all()
        for performance in performances:
            #premiere_type_string='[{}] '.format(performance.premiere_type.name) if performance.premiere_type.name != 'No' else ''                
            data["results"].append({ 'text': '{}'.format(
                            performance.musical_piece.get_name()),
                           'id':performance.id})
    return jsonify(data)



@bp.route('/listtable/performancesdetails/<event_id>') 
def getPerformanceDetailList(event_id):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    data={ "rows": [], "total": 0 }
    event=Event.query.filter_by(id=event_id).first()
    if event:
        data["total"] = event.performances.count()
        performances=event.performances.order_by(Performance.musical_piece_id).limit(limit).offset(offset).all()
        for performance in performances:
            for participant in performance.participants:
                performance_name='{}'.format(performance.musical_piece.get_name())
                participant_name=participant.get_short_name()
                participant_activity=participant.activity.name  if participant.activity else ''
                data["rows"].append({ 'performance_name': performance_name,
                                  'participant_name': participant_name, 
                                  'participant_activity': participant_activity,
                                  'performance_participant_id': '{},{}'.format(performance.id,participant.id) })
    return jsonify(data)
    
def EditSimpleElement(dbmodel,title,id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    db_element = dbmodel.query.filter_by(id=id).first_or_404()
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name=db_element.name)
    if form.validate_on_submit():
        db_element.name = form.name.data
        addHistoryEntry('Modificado','{}: {}'.format(' '.join(title.split(' ')[1:]),form.name.data))
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = db_element.name
    return render_template('main/edit_simple_element.html',title=title,form=form)


@bp.route('/edit/country/<id>',methods = ['GET','POST'])
@login_required
def EditCountry(id):
    return EditSimpleElement(Country,_('Editar País'),id)


@bp.route('/edit/eventtype/<id>',methods = ['GET','POST'])
@login_required
def EditEventType(id):
    return EditSimpleElement(EventType,_('Editar Tipo de Evento'),id)

@bp.route('/edit/cycle/<id>',methods = ['GET','POST'])
@login_required
def EditCycle(id):
    return EditSimpleElement(Cycle,_('Editar Ciclo'),id)
 
@bp.route('/edit/city/<id>',methods = ['GET','POST'])
@login_required
def EditCity(id):
    return EditSimpleElement(City,_('Editar Ciudad'),id)


@bp.route('/edit/instrumenttype/<id>',methods = ['GET','POST'])
@login_required
def EditInstrumentType(id):
    return EditSimpleElement(InstrumentType,_('Editar Tipo de Instrumento'),id) 

@bp.route('/edit/musicalensembletype/<id>',methods = ['GET','POST'])
@login_required
def EditMusicalEnsembleType(id):
    return EditSimpleElement(MusicalEnsembleType,_('Editar Tipo de Agrupación Musical'),id) 

@bp.route('/edit/premieretype/<id>',methods = ['GET','POST'])
@login_required
def EditPremiereType(id):
    return EditSimpleElement(PremiereType,_('Editar Tipo de Instrumento'),id) 

def NewSimpleElement(dbmodel,title):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name='')   
    if form.validate_on_submit():
        if  dbmodel.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
        else:
            db.session.add(dbmodel(name=form.name.data))
            try:
                addHistoryEntry('Agregado','{}: {}'.format(title[8:],form.name.data))
            except:
                log.error('Failed adding history entry')
            db.session.commit()
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

@bp.route('/new/cycle', methods = ['GET','POST'])
@login_required
def NewCycle():
    return NewSimpleElement(Cycle,_('Agregar Ciclo'))

@bp.route('/new/city', methods = ['GET','POST'])
@login_required
def NewCity():
    return NewSimpleElement(City,_('Agregar Ciudad'))

@bp.route('/new/instrumenttype', methods = ['GET','POST'])
@login_required
def NewInstrumentType():
    return NewSimpleElement(InstrumentType,_('Agregar Tipo de Instrumento'))

@bp.route('/new/musicalensembletype', methods = ['GET','POST'])
@login_required
def NewMusicalEnsembleType():
    return NewSimpleElement(MusicalEnsembleType,_('Agregar Tipo de Agrupación Musical'))
    
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
        return redirect(url_for('users.login'))
    form = EditInstrumentForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Instrument.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editinstrument.html',form=form,title=_('Agregar Instrumento'),selectedElements="")
        else:
            try:
                instrument_type =InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first()
            except:
                instrument_type=None
            db.session.add(Instrument(name=form.name.data,instrument_type=instrument_type))
            addHistoryEntry('Agregado','Instrumento: {}'.format(form.name.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editinstrument.html',form=form,title=_('Agregar Instrumento'),selectedElements="")

@bp.route('/edit/instrument/<id>', methods = ['GET','POST'])
@login_required
def EditInstrument(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    instrument = Instrument.query.filter_by(id=id).first()
    selectedElements=[]
    if instrument:
        if instrument.instrument_type:
            selectedElements.append(instrument.instrument_type.id)
    form = EditInstrumentForm(original_name=instrument.name)
    if form.validate_on_submit():
         instrument.name = form.name.data
         try:
             instrument_type = InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first()
         except:
             instrument_type = None
         instrument.instrument_type = instrument_type
         addHistoryEntry('Modificado','Instrumento: {}'.format(form.name.data))
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = instrument.name            
    print(list2csv(selectedElements))
    return render_template('main/editinstrument.html',form=form,title=_('Editar Instrumento'),selectedElements=list2csv(selectedElements))    

@bp.route('/new/musicalpiece', methods = ['GET','POST'])
@login_required
def NewMusicalPiece():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = EditMusicalPieceForm(dbmodel=MusicalPiece,original_name='')   
    if form.validate_on_submit():
#        composer = Person.query.filter_by(id=int(form.composer.data[0])).first_or_404()
        addHistoryEntry('Agregado','Obra Musical: {}'.format(form.name.data))
        new_musical_piece=MusicalPiece(name=form.name.data,composition_year=form.composition_year.data,
                                       instrumental_lineup=form.instrumental_lineup.data,text=form.text.data)
        for instrument_id in form.instruments.data:
            try:
                instrument=Instrument.query.filter_by(id=int(instrument_id)).first()
                if instrument:
                    new_musical_piece.instruments.append(instrument)
            except:
                pass
        for composer_id in form.composers.data:
            try:
                composer=Person.query.filter_by(id=int(composer_id)).first()
                if composer:
                    new_musical_piece.composers.append(composer)
            except:
                pass
        db.session.add(new_musical_piece)
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editmusicalpiece.html',form=form,title=_('Agregar Obra Musical'),selectedElements="")

@bp.route('/new/musicalensemble', methods = ['GET','POST'])
@login_required
def NewMusicalEnsemble():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = EditMusicalEnsembleForm(dbmodel=MusicalEnsemble,original_name='')   
    if form.validate_on_submit():
        if  MusicalEnsemble.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/newmusicalensemble.html',form=form,title=_('Agregar Agrupación Musical'),selectedElements="")
        else:
            try:
                musical_ensemble_type =MusicalEnsembleType.query.filter_by(id=int(form.musical_ensemble_type.data[0])).first()
            except:
                musical_ensemble_type=None
            new_musical_ensemble=MusicalEnsemble(name=form.name.data,musical_ensemble_type=musical_ensemble_type,additional_info=form.additional_info.data)
            db.session.add(new_musical_ensemble)
            addHistoryEntry('Agregado','Agrupación Musical: {}'.format(form.name.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
            return redirect(url_for('main.EditMusicalEnsemble',id=new_musical_ensemble.id))
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/newmusicalensemble.html',form=form,title=_('Agregar Agrupación Musical'),selectedElements="")

@bp.route('/edit/musicalensemble/<id>', methods = ['GET','POST'])
@login_required
def EditMusicalEnsemble(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    musical_ensemble = MusicalEnsemble.query.filter_by(id=id).first()
    selectedElements=[]
    if musical_ensemble:
        if musical_ensemble.musical_ensemble_type:
            selectedElements.append(musical_ensemble.musical_ensemble_type.id)
    form = EditMusicalEnsembleForm(original_name=musical_ensemble.name)
    if form.validate_on_submit():
         musical_ensemble.name = form.name.data
         try:
             musical_ensemble_type = MusicalEnsembleType.query.filter_by(id=int(form.musical_ensemble_type.data[0])).first()
         except:
             musical_ensemble_type = None
         musical_ensemble.musical_ensemble_type = musical_ensemble_type
         musical_ensemble.additional_info=form.additional_info.data
         addHistoryEntry('Modificado','Agrupación Musical: {}'.format(form.name.data))
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = musical_ensemble.name
        form.additional_info.data= musical_ensemble.additional_info
    return render_template('main/editmusicalensemble.html',form=form,title=_('Editar Agrupación Musical'),musical_ensemble_id=id,selectedElements=list2csv(selectedElements))    

@bp.route('/edit/musicalpiece/<id>', methods = ['GET','POST'])
@login_required
def EditMusicalPiece(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    musical_piece = MusicalPiece.query.filter_by(id=id).first_or_404()
    composers_list=[]
    for composer in musical_piece.composers:
        composers_list.append(composer.id)
    selectedComposers=list2csv(composers_list)    
    instruments_list=[]
    for instrument in musical_piece.instruments:
        instruments_list.append(instrument.id)    
    selectedInstruments=list2csv(instruments_list)
    form = EditMusicalPieceForm(original_name=musical_piece.name)
    if form.validate_on_submit():
         musical_piece.name = form.name.data
         musical_piece.text=form.text.data
         musical_piece.instrumental_lineup=form.instrumental_lineup.data
         musical_piece.composers.clear()
         musical_piece.instruments.clear()
         for instrument_id in form.instruments.data:       
             try:
                 intrument=Instrument.query.filter_by(id=int(instrument_id)).first()
             except:
                 instrument=None
             if intrument:
                 musical_piece.instruments.append(intrument)    
         for composer_id in form.composers.data:       
             try:
                 composer=Person.query.filter_by(id=int(composer_id)).first()
             except:
                 composer=None
             if composer:
                 musical_piece.composers.append(composer)    
         musical_piece.composition_year = form.composition_year.data
         addHistoryEntry('Modificado','Obra Musical: {}'.format(form.name.data))
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
        form.name.data = musical_piece.name  
        form.composition_year.data = musical_piece.composition_year
        form.text.data=musical_piece.text
        form.instrumental_lineup.data=musical_piece.instrumental_lineup      
    return render_template('main/editmusicalpiece.html',form=form,title=_('Editar Obra Musical'),selectedComposers=selectedComposers,selectedInstruments=selectedInstruments)    


@bp.route('/new/activity', methods = ['GET','POST'])
@login_required
def NewActivity():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = EditActivityForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Activity.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editactivity.html',form=form,title=_('Agregar Actividad'),selectedElements="")
        else:
            try:
                instrument = Instrument.query.filter_by(id=int(form.instrument.data[0])).first()
            except:
                instrument = None
            db.session.add(Activity(name=form.name.data,instrument=instrument))
            addHistoryEntry('Agregado','Actividad: {}'.format(form.name.data))            
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editactivity.html',form=form,title=_('Agregar Actividad'),selectedElements="")

@bp.route('/edit/activity/<id>', methods = ['GET','POST'])
@login_required
def EditActivity(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    original_activity= Activity.query.filter_by(id=id).first_or_404()
    selectedElements=[]
    if original_activity.instrument:
        selectedElements.append(original_activity.instrument.id)
    form = EditActivityForm(original_name=original_activity.name)
    if form.validate_on_submit():
         original_activity.name = form.name.data
         try:
             instrument = Instrument.query.filter_by(id=int(form.instrument.data[0])).first()
         except:
             instrument = None
         original_activity.instrument = instrument
         addHistoryEntry('Modificado','Actividad: {}'.format(form.name.data))
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
        return redirect(url_for('users.login'))
    form = EditLocationForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Location.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editlocation.html',form=form,title=_('Agregar Lugar'),selectedElements="")
        else:
            city = City.query.filter_by(id=int(form.city.data[0])).first_or_404()
            db.session.add(Location(name=form.name.data,city=city,additional_info=form.additional_info.data,address=form.address.data))
            addHistoryEntry('Agregado','Lugar: {}'.format(form.name.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editlocation.html',form=form,title=_('Agregar Lugar'),selectedElements="")

@bp.route('/edit/location/<id>', methods = ['GET','POST'])
@login_required
def EditLocation(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    original_location = Location.query.filter_by(id=id).first_or_404()
    selectedElements=[]
    selectedElements.append(original_location.city.id)
    form = EditLocationForm(original_name=original_location.name)
    if form.validate_on_submit():
         original_location.name = form.name.data
         original_location.additional_info=form.additional_info.data
         original_location.address=form.address.data
         city = City.query.filter_by(id=int(form.city.data[0])).first_or_404()
         original_location.city = city
         addHistoryEntry('Modificado','Lugar: {}'.format(form.name.data))
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
        return redirect(url_for('users.login'))
    form = EditOrganizationForm(dbmodel=Organization,original_name='')   
    if form.validate_on_submit():
        if  Organization.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'),'error')
            return render_template('main/editorganization.html',form=form,title=_('Agregar Organización'))
        else:
            db.session.add(Organization(name=form.name.data,additional_info=form.additional_info.data))
            addHistoryEntry('Agregado','Organización: {}'.format(form.name.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editorganization.html',form=form,title=_('Agregar Organización'))

@bp.route('/edit/organizatioeventn/<id>', methods = ['GET','POST'])
@login_required
def EditOrganization(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    original_organization =Organization.query.filter_by(id=id).first_or_404()
    form = EditOrganizationForm(original_name=original_organization.name)
    if form.validate_on_submit():
         original_organization.name = form.name.data
         original_organization.additional_info=form.additional_info.data
         addHistoryEntry('Modificado','Organización: {}'.format(form.name.data))
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
        return redirect(url_for('users.login'))
    form = EditPersonForm(original_person=None)   
    if form.validate_on_submit():
        person = Person(first_name=form.first_name.data,last_name=form.last_name.data)
        person.birth_year = form.birth_year.data
        person.death_year = form.death_year.data
        person.biography= form.biography.data
        person.gender=Gender.query.filter_by(id= int(form.gender.data[0])).first_or_404()
        for country_id in form.nationalities.data:
            person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
        db.session.add(person)
        addHistoryEntry('Agregado','Persona: {} {}'.format(form.first_name.data,form.last_name.data))
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.index',user=current_user.first_name))
    return render_template('main/editperson.html',form=form,title=_('Agregar Persona'),selectedElements="")

@bp.route('/edit/person/<id>', methods = ['GET','POST'])
@login_required
def EditPerson(id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    person = Person.query.filter_by(id=id).first_or_404()
    form = EditPersonForm(person)
    selectedElements=[]
    for nationality in person.nationalities:
        selectedElements.append(nationality.id)
    selectedElementGender=str(person.gender.id)
    if form.validate_on_submit():
         person.first_name = form.first_name.data
         person.last_name = form.last_name.data
         person.birth_year = form.birth_year.data
         person.death_year = form.death_year.data
         person.biography= form.biography.data
         person.gender = Gender.query.filter_by(id=int(form.gender.data[0])).first_or_404()
         person.nationalities.clear()
         for country_id in form.nationalities.data:
             person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
         addHistoryEntry('Modificado','Persona: {} {}'.format(form.first_name.data,form.last_name.data))
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'),'info')
         return redirect(url_for('main.index',user=current_user.first_name))
    elif request.method == 'GET':
         form.first_name.data = person.first_name
         form.last_name.data = person.last_name
         form.birth_year.data = person.birth_year
         form.death_year.data = person.death_year
         form.biography.data = person.biography
    return render_template('main/editperson.html',form=form,title=_('Editar Persona'),selectedElements=list2csv(selectedElements),selectedElementGender=selectedElementGender)    


@bp.route('/new/event', methods = ['GET','POST'])
@login_required
def NewEvent():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = EditEventForm(dbmodel=Event,original_event=None)   
    if form.validate_on_submit():
#        if  Event.query.filter_by(name=form.name.data).all().__len__() > 0:
#            flash(_('Este nombre ya ha sido registrado'),'error')
#            return render_template('main/newevent.html',form=form,title=_('Agregar Evento'))
#        else:
        location = Location.query.filter_by(id=int(form.location.data[0])).first_or_404()
#        organization = Organization.query.filter_by(id=int(form.organization.data[0])).first_or_404()
        event_type = EventType.query.filter_by(id=int(form.event_type.data[0])).first_or_404()
        cycle = Cycle.query.filter_by(id=int(form.cycle.data[0])).first_or_404()
        newevent=Event(name=form.name.data,
                             location=location,
                             event_type=event_type,
                             cycle=cycle,
                             information=form.information.data,
                             day=form.event_day.data,
                             month=form.event_month.data,
                             year=form.event_year.data)
        for organization_id in form.organizations.data:
             newevent.organizations.append(Organization.query.filter_by(id=organization_id).first_or_404())
        db.session.add(newevent)
        addHistoryEntry('Agregado','Evento: {}'.format(newevent.get_name()))
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info') 
        return redirect(url_for('main.EditEvent',event_id=newevent.id))
    return render_template('main/newevent.html',form=form,title=_('Agregar Evento'))


@bp.route('/edit/event/<event_id>', methods = ['GET','POST'])
@login_required
def EditEvent(event_id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'),'error')
        return redirect(url_for('users.login'))

    original_event=Event.query.filter_by(id=event_id).first_or_404()
    selectedOrgs=[]
    for organization in original_event.organizations:
        selectedOrgs.append(organization.id)
    form = EditEventForm(dbmodel=Event,original_event=original_event)       
    if form.validate_on_submit():
        Location.query.filter_by(id=int(form.location.data[0])).first_or_404()
        EventType.query.filter_by(id=int(form.event_type.data[0])).first_or_404()
        Cycle.query.filter_by(id=int(form.cycle.data[0])).first_or_404()            
        original_event.name=form.name.data
        original_event.location_id=form.location.data[0]
        original_event.event_type_id=form.event_type.data[0]
        original_event.cycle_id=form.cycle.data[0]
        original_event.information=form.information.data
        original_event.day=form.event_day.data
        original_event.month=form.event_month.data
        original_event.year=form.event_year.data    
        original_event.organizations.clear()
        for organization_id in form.organizations.data:
             original_event.organizations.append(Organization.query.filter_by(id=organization_id).first_or_404())
        addHistoryEntry('Modificado','Evento: {}'.format(original_event.get_name()))
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('main.EditEvent',event_id=event_id))
    else:
        form.name.data=original_event.name
        form.event_day.data=original_event.day
        form.event_month.data=original_event.month
        form.event_year.data=original_event.year
        form.information.data=original_event.information
        return render_template('main/editevent.html',event_id=event_id,form=form,title=_('Editar Evento'),
                                   selectedEventType=str(original_event.event_type_id), 
                                   selectedCycle=str(original_event.cycle_id),
                                   selectedLocation=str(original_event.location_id),
                                   selectedOrganizations=list2csv(selectedOrgs))



