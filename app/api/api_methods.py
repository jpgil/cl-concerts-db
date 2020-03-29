from app.api import bp
from flask import request, current_app, jsonify
from app import db
from app.api.errors import bad_request, server_error
from app.models import *
from flask_babel import _
from app import files_collection
from app.main.routes import addHistoryEntry,getStringForModel
from sqlalchemy import and_, inspect
import sqlalchemy
from flask_login import current_user, login_required
import os

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
        return bad_request(_('debe participante'))
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
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
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
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
        addHistoryEntry('Eliminado','Miembro: {} de {}...'.format(musical_ensemble_member.get_name(),musical_ensemble_member.musical_ensemble.name[0:40]))
        db.session.delete(musical_ensemble_member)
        db.session.commit()
        response = jsonify({})
        response.status_code = 200
#       response.headers['Location'] = url_for('api.get_user', id=user.id)
        return response
    else:
        return bad_request(_('miembro no encontrado'))    


def get_table_and_relationships(model): 
    # this conver the model name in the model class 
    table=eval(model) 
    # get the list of all the attributes of the table  
    keys=inspect(table).attrs.keys() 
    # we'll store the name of the attributs who correspond to relationship
    # with other tables in relation_keys
    relation_keys=[] 
    for key in keys: 
        attr=getattr(table,key) 
        if type(attr.property) == sqlalchemy.orm.relationships.RelationshipProperty: 
            relation_keys.append(key) 
    return (table,relation_keys)

    
@bp.route('/delete/<string:model>/<int:id>', methods = ['GET','POST'])
@login_required
def delete_element(model,id):
    (table,relationship_keys)=get_table_and_relationships(model)
    element=table.query.filter(table.id==id).first_or_404()
    linked_objects_dict={}
    for relation in relationship_keys:
        # now we iterate for each relation, looking for linked objects
        for linked_object in getattr(element,relation):
            ln_obj_table_name=linked_object.__repr__().split('(')[0]
            ln_obj_info=linked_object.get_name()
            if ln_obj_table_name not in linked_objects_dict:
                linked_objects_dict[ln_obj_table_name]=[ln_obj_info]
            else:
                linked_objects_dict[ln_obj_table_name].append(ln_obj_info)
    for linked_objects in linked_objects_dict:
        print('No se puede borrar, este item está relacionado')
        print('con los siguientes elementos de la tabla {}'.format(getStringForModel(linked_objects)))
        for obj in linked_objects_dict[linked_objects]:
            print('\t{}'.format(obj))
            

    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        return bad_request(_('Su perfil debe ser de Administrador o Editor para realizar esta tarea'))
    
    print("Deleted {}:{}".format(model,id))
    response = jsonify({})
    response.status_code = 200
#   response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
    