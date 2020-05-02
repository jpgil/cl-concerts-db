from app.api import bp
from flask import request, current_app, jsonify
from app import db
from app.api.errors import bad_request, server_error
from app.models import *
from flask_babel import _
from app import files_collection
from app.main.routes import addHistoryEntry,getStringForModel
from sqlalchemy import and_
import sqlalchemy
from sqlalchemy_utils import dependent_objects, get_referencing_foreign_keys
from flask_login import current_user, login_required
import os
DEPS_LIMIT=8
def checkForKeys(keys,form):
    """Returns true if there is a missing key in form"""
    for k in keys:
        if k not in form:
            return True
    return False
        
@bp.route('/participant/add',methods=['POST'])
@login_required
def add_participant():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['event_id', 'person_id','activity_id'],request.form):
        return bad_request(_('debe incluir evento, persona y actividad'))
    event_id = int(request.form['event_id'])
    activity_id = int(request.form['activity_id'])
    person_id = int(request.form['person_id'])
    if activity_id == -1:
        activity_id = None;

    activity=Activity.query.filter_by(id=activity_id).first()
#    if not activity:
 #       return bad_request(_('actividad no encontrada'))
    person=Person.query.filter_by(id=person_id).first()
    if not person:   
        return bad_request(_('persona no encontrada'))
    event=Event.query.filter_by(id=event_id).first()
    if not event:
        return bad_request(_('evento no encontrado'))   
    participants=event.participants.order_by(Participant.person_id).all()
    for participant in participants:
        # if the participant already exists, we return an error
        if ( participant.person_id == person_id  and participant.activity_id == activity_id):
            return bad_request(_('Participante ya agregado'))
    event.participants.append(Participant(person=person,activity=activity))
    addHistoryEntry('Agregado','Participante: {}({}) a {}...'.format(person.get_name(),activity.name if activity else None,event.name[0:40]))
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/participant/delete', methods=['POST'])
@login_required
def remove_participant():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))    
    if checkForKeys(['participant_id'],request.form):
        return bad_request(_('debe incluir participante'))    
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    addHistoryEntry('Eliminado','Participante: {} de {}...'.format(participant.get_name(),
                                                            participant.event.name[0:40]))
    db.session.delete(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response    

@bp.route('/musicalensembleatevent/add',methods=['POST'])
@login_required
def add_musical_ensemble_to_event():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['event_id','musical_ensemble_id'],request.form):
        return bad_request(_('debe incluir evento y agrupación musical'))
    musical_ensemble=MusicalEnsemble.query.filter_by(id=request.form['musical_ensemble_id']).first()
    if not musical_ensemble:
        return bad_request(_('agrupación musical no encontrada'))       
    event=Event.query.filter_by(id=request.form['event_id']).first()
    if not event:
        return bad_request(_('evento no encontrado'))   
    new_participant=Participant(musical_ensemble=musical_ensemble)
    event.participants.append(new_participant)
    for member in musical_ensemble.members:
        event.participants.append(Participant(musical_ensemble=musical_ensemble,person=member.person,activity=member.activity))
    addHistoryEntry('Agregado','Participante: {} a {}...'.format(new_participant.get_name(),event.name[0:40])) 
    addHistoryEntry('Agregado','Participante: Agregados {} miembros de {} al evento {}.'.format(musical_ensemble.members.count(),musical_ensemble.get_name(),event.name[0:40]))    
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
    
@bp.route('/performance/add',methods=['POST'])
@login_required
def add_performance():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['event_id','musical_piece_id','premiere_type_id'],request.form):
        return bad_request(_('debe incluir evento, obra musical y tipo de estreno'))
    musical_piece=MusicalPiece.query.filter_by(id=request.form['musical_piece_id']).first()
    if not musical_piece:
        return bad_request(_('obra no encontrada no encontrada'))
    premiere_type=PremiereType.query.filter_by(id=request.form['premiere_type_id']).first()
    if not premiere_type:   
        return bad_request(_('tipo de estreno no encontrado'))
    event=Event.query.filter_by(id=request.form['event_id']).first()
    if not event:
        return bad_request(_('evento no encontrado'))   
    performances=event.performances.all()
    for performance in performances:
        # if the performance already exists, we return an error
        if performance.musical_piece_id == int(request.form['musical_piece_id']):
            return bad_request(_('obra ya agregada'))
    event.performances.append(Performance(musical_piece=musical_piece,premiere_type=premiere_type))
    addHistoryEntry('Agregado','Interpretación: {} a {}...'.format(musical_piece.get_name(),event.name[0:40]))
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/performance/delete', methods=['POST'])
@login_required
def remove_performance():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['performance_id'],request.form):
        return bad_request(_('debe incluir interpretación'))    
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    addHistoryEntry('Eliminado','Interpretación: {} de {}...'.format(performance.musical_piece.get_name(),performance.event.name[0:40]))
    db.session.delete(performance)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response    

@bp.route('/performancedetail/add', methods=['POST'])
@login_required
def add_performance_detail():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))    
    if checkForKeys(['performance_id'],request.form):
        return bad_request(_('debe incluir interpretación'))    
    if checkForKeys(['participant_id'],request.form):
        return bad_request(_('debe incluir participante'))
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    if not participant:
        return bad_request(_('El participante no existe. ¿Fue borrado recientenmente? id:'))+str(equest.form['performance_id'])
    if not performance:
        return bad_request(_('La participación no existe. ¿Fue borrada recientenmente? id:'))+str(equest.form['participant_id'])
    if participant in performance.participants:
        return bad_request(_('participante ya agregado'))
    addHistoryEntry('Agregado','Detalle de Interpretación: {} agregado a {} en {}'.format(participant.get_name(),
                                                                                              performance.musical_piece.name,
                                                                                              performance.event.name[0:40]))
    performance.participants.append(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
    
    

@bp.route('/performancedetail/delete', methods=['POST'])
@login_required
def delete_performance_detail():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['performance_id'],request.form):
        return bad_request(_('debe incluir interpretación'))    
    if not request.form['participant_id']:
        return bad_request(_('debe incluir participante'))    
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    if participant not in performance.participants:
        return bad_request(_('participante no está agregado a esta presentación'))
    addHistoryEntry('Eliminado','Detalle de Interpretación: {} agregado a {} en {}'.format(participant.get_name(),
                                                                                              performance.musical_piece.name,
                                                                                              performance.event.name[0:40]))
    performance.participants.remove(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/uploadajax', methods=['POST'])
@login_required
def upldfile():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))    
    if checkForKeys(['file'],request.files):
        return bad_request(_('debe incluir al menos un archivo'))    
    if checkForKeys(['event_id'],request.form):
        return bad_request(_('debe incluir el id del evento'))
    if checkForKeys(['description'],request.form):
        return bad_request(_('debe incluir una descripcion'))   
    elif request.form['description'].strip() == '':
        return bad_request(_('debe incluir una descripcion'))   
    files = request.files['file']
    if files:
        filename = files_collection.save(request.files['file'],folder=request.form['event_id'])
        url = files_collection.url(filename)            
        current_app.logger.info('FileName: ' + filename)
        event=Event.query.filter_by(id=request.form['event_id']).first()
        db.session.add(MediaLink(event_id=int(request.form['event_id']), filename=filename, mime_type=files.mimetype,url=url, description=request.form['description']))
        addHistoryEntry('Agregado','Archivo: {} a {}'.format(request.files['file'],event.name))
        db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
        
@bp.route('/medialink/delete', methods=['POST'])
@login_required
def deleteFile():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))    
    if checkForKeys(['medialink_id'],request.form):
        return bad_request(_('id de archivo no incluído'))
    file=MediaLink.query.filter_by(id=request.form['medialink_id']).first()        
    try:
        os.remove(files_collection.path(file.filename))
        addHistoryEntry('Eliminado','Archivo: {} de {}'.format(file.filename,file.event.name))
        db.session.delete(file)
        db.session.commit()
        response = jsonify({})
        response.status_code = 200
        return response
    except:
        return server_error("Error removing {}".format(files_collection.path(file.filename)))
  
@bp.route('/musicalensemblemember/add',methods=['POST'])
@login_required
def add_musical_ensemble_member():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['musical_ensemble_id','person_id','activity_id'],request.form):
            return bad_request(_('debe incluir agrupación, persona y actividad'))
    musicalensemble_id = int(request.form['musical_ensemble_id'])
    activity_id = int(request.form['activity_id']) if request.form['activity_id'] else None
    person_id = int(request.form['person_id'])
    if activity_id == -1:
        activity_id = None
    if person_id == -1 :
        person_id = None
    if not activity_id and not person_id:
        return bad_request(_('debe incluir persona o actividad'))
    activity=Activity.query.filter_by(id=activity_id).first() if activity_id else None
    person=Person.query.filter_by(id=person_id).first() if person_id else None
    if not person and not activity:
        if not person_id:
            return bad_request(_('actividad no encontrada'))
        if not activity_id:
            return bad_request(_('persona no encontrada')) 
    musicalensemble=MusicalEnsemble.query.filter_by(id=musicalensemble_id).first()
    if not musicalensemble:
        return bad_request(_('agrupación musical no encontrada'))   
    members=musicalensemble.members.order_by(MusicalEnsembleMember.person_id).all()
    for member in members:
        # if the participant already exists, we return an error
        if ( member.person_id == person_id  and member.activity_id == activity_id):
            return bad_request(_('Miembro ya agregado'))
    new_member=MusicalEnsembleMember(person=person,activity=activity)
    musicalensemble.members.append(new_member)
    addHistoryEntry('Agregado','Miembro: {} a {}...'.format(new_member.get_name(),musicalensemble.name[0:40]))
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.getimport traceback_user', id=user.id)
    return response


@bp.route('/musicalensemblemember/delete', methods=['POST'])
@login_required
def delete_musical_ensemble_member():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    if checkForKeys(['musical_ensemble_member_id'],request.form):
        return bad_request(_('debe incluir miembro de la agrupación musical'))    
    musical_ensemble_member=MusicalEnsembleMember.query.filter_by(id=request.form['musical_ensemble_member_id']).first()
    if musical_ensemble_member:
        participants=Participant.query.filter(and_(Participant.musical_ensemble_id==musical_ensemble_member.musical_ensemble_id,
                                                    Participant.person_id==musical_ensemble_member.person_id,
                                                    Participant.activity_id==musical_ensemble_member.activity_id))
        for participant in participants:
            addHistoryEntry('Eliminado','Participante: {} de {}...'.format(participant.get_name(),participant.event.get_name()))
            db.session.delete(participant)
        db.session.delete(musical_ensemble_member)
        addHistoryEntry('Eliminado','Miembro: {} de {}...'.format(musical_ensemble_member.get_name(),musical_ensemble_member.musical_ensemble.name[0:40]))
        db.session.commit()
        response = jsonify({})
        response.status_code = 200
#       response.headers['Location'] = url_for('api.get_user', id=user.id)
        return response
    else:
        return bad_request(_('miembro no encontrado'))    

def get_hard_dependencies(element,model,limit):
    return list(dependent_objects(element).limit(DEPS_LIMIT) ) 

def get_soft_dependencies(element,model,limit): 
    # the hard dependencies above manages all the 1 - 1 relations, but the 1 - many or many - many
    # needs to be manually managed
    deps=[]
    if model == 'Instrument':
        deps=deps+element.musical_pieces if element.musical_pieces else deps
    elif model in ['Organization']:
        deps=deps+element.events if element.events else deps
    elif model == 'Country':
        deps=deps+element.people if element.people else deps
    return deps[0:DEPS_LIMIT]
    

@bp.route('/deletecheck/<string:model>/<int:id>', methods = ['GET','POST'])
@login_required
def delete_check_element(model,id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
        
    table=eval(model)
    try:
        element=table.query.filter(table.id==id).first_or_404()
        if model == 'Event':
            response = jsonify({ 'soft_deps': None, 'hard_deps': None} )
            response.status_code = 200
            return response

        soft_deps=get_soft_dependencies(element,model,DEPS_LIMIT)
        hard_deps=get_hard_dependencies(element,model,DEPS_LIMIT)
        if model == 'MusicalEnsemble':
            hard_deps=element.participants[0:DEPS_LIMIT]
            soft_deps=[]
        message_soft_deps=None
        if soft_deps:
            message_soft_deps=_('Este elemento será eliminado de los siguientes objetos:\n')
            message_soft_deps+=_('(mostrando los primeros ')+str(DEPS_LIMIT)+')<hr>'
            for soft_dep in soft_deps:
                table_name=getStringForModel(soft_dep.__repr__().split('(')[0])
                element_name=soft_dep.get_name()
                message_soft_deps+='{}: {}<br>'.format(table_name,element_name)
            message_soft_deps+='\n'+_('<h4>¿Está seguro que desea continuar?</h4>')+'\n'
        message_hard_deps=None
        if hard_deps:
            message_hard_deps=_('Este elemento está siendo usando en los siguientes objetos:\n')
            message_hard_deps+=_('(mostrando los primeros ')+str(DEPS_LIMIT)+')<hr>'
            for hard_dep in hard_deps:
                table_name=getStringForModel(hard_dep.__repr__().split('(')[0])
                element_name=hard_dep.get_name()
                message_hard_deps+='{}: {}<br>'.format(table_name,element_name)
            message_hard_deps+='<hr>'+_('<h4>Por favor, elimine esas dependencias antes de continuar</h4>')+'\n'            
        response = jsonify({ 'soft_deps': message_soft_deps, 'hard_deps': message_hard_deps} )
        response.status_code = 200
        return response
    except Exception as ex:
        message=_('"Ocurrió un error tratando de borrar el elemento:')+str(ex)
        raise ex
        return bad_request(message)
        

@bp.route('/delete/<string:model>/<int:id>', methods = ['GET','POST'])
@login_required
def delete_element(model,id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    table=eval(model)
    element=table.query.filter(table.id==id).first_or_404()
    if model == 'Event':
        for file in element.medialinks.all():   
            found = True
            try:
                os.remove(files_collection.path(file.filename))
            except:
                found = False
                # file no found in the sever, but since we want to delete it...
            addHistoryEntry('Eliminado','Archivo: {} {} de {}'.format(file.filename,"" if found else "(No encontrado)",file.event.name))
            db.session.delete(file)
        for performance in element.performances.all():
            db.session.delete(performance)
            addHistoryEntry('Eliminado','Interpretación: {} de {}...'.format(performance.musical_piece.get_name(),performance.event.name[0:40]))
        for participant in element.participants.all():
            db.session.delete(participant)
            addHistoryEntry('Eliminado','Participante: {}'.format(participant.get_name()))
    if model == 'MusicalEnsemble':
        for member in element.members.all():
            db.session.delete(member)
            addHistoryEntry('Eliminado','Miembro de agrupción musical: {}'.format(member.get_name()))
        for participant in element.participants.all():
            db.session.delete(participant)
            addHistoryEntry('Eliminado','Participante: {}'.format(participant.get_name()))
    table_name=getStringForModel(element.__repr__().split('(')[0])
    addHistoryEntry('Eliminado','{}: {}'.format(table_name,element.get_name()[0:50]))
    db.session.delete(element)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response