from app.api import bp
from flask import request, current_app, jsonify, flash
from app import db
from app.api.errors import bad_request, server_error
from app.models import Activity, Event, Person, Participant, MusicalPiece, PremiereType, Performance, MediaLink
from flask_babel import _
from app import files_collection
from app.main.routes import addHistoryEntry
import os


@bp.route('/participant/add',methods=['POST'])
def add_participant():
    if not request.form['event_id'] or not request.form['person_id'] or not request.form['activity_id']:
        return bad_request(_('debe incluir evento, persona y actividad'))
    activity=Activity.query.filter_by(id=request.form['activity_id']).first()
    if not activity:
        return bad_request(_('actividad no encontrada'))
    person=Person.query.filter_by(id=request.form['person_id']).first()
    if not person:   
        return bad_request(_('persona no encontrada'))
    event=Event.query.filter_by(id=request.form['event_id']).first()
    if not event:
        return bad_request(_('evento no encontrado'))   
    participants=event.participants.order_by(Participant.person_id).all()
    for participant in participants:
        # if the participant already exists, we return an error
        if ( participant.person_id == int(request.form['person_id']) and participant.activity_id == int(request.form['activity_id'])):
            return bad_request(_('Participante ya agregado'))
    event.participants.append(Participant(person=person,activity=activity))
    addHistoryEntry('Agregado','Participante: {}({}) a {}...'.format(person.get_full_name(),activity.name,event.name[0:40]))
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/participant/delete', methods=['POST'])
def remove_participant():
    if not request.form['participant_id']:
        return bad_request(_('debe incluir participante'))    
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    addHistoryEntry('Eliminado','Participante: {}({}) a {}...'.format(participant.person.get_full_name(),
                                                            participant.activity.name,
                                                            participant.event.name[0:40]))
    db.session.delete(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response    


@bp.route('/performance/add',methods=['POST'])
def add_performance():
    if not request.form['event_id'] or not request.form['musical_piece_id'] or not request.form['musical_piece_id']:
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
    addHistoryEntry('Agregado','Interpretación: {}({}) a {}...'.format(musical_piece.name,musical_piece.composer.get_full_name(),event.name[0:40]))
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/performance/delete', methods=['POST'])
def remove_performance():
    if not request.form['performance_id']:
        return bad_request(_('debe incluir interpretación'))    
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    addHistoryEntry('Eliminado','Interpretación: {}({}) a {}...'.format(performance.musical_piece.name,performance.musical_piece.composer.get_full_name(),performance.event.name[0:40]))
    db.session.delete(performance)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response    

@bp.route('/performancedetail/add', methods=['POST'])
def add_performance_detail():
    if not request.form['performance_id']:
        return bad_request(_('debe incluir interpretación'))    
    if not request.form['participant_id']:
        return bad_request(_('debe participante'))
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    if participant in performance.participants:
        return bad_request(_('participante ya agregado'))
    addHistoryEntry('Agregado','Detalle de Interpretación: {}({}) agregado a {} en {}'.format(participant.person.get_full_name(),
                                                                                              participant.activity.name,
                                                                                              performance.musical_piece.name,
                                                                                              performance.event.name[0:40]))
    performance.participants.append(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response
    
    

@bp.route('/performancedetail/delete', methods=['POST'])
def delete_performance_detail():
    if not request.form['performance_id']:
        return bad_request(_('debe incluir interpretación'))    
    if not request.form['participant_id']:
        return bad_request(_('debe incluir participante'))    
    print('performance_id:  {}, participant_id:  {}'.format(request.form['performance_id'],request.form['participant_id']))
    performance=Performance.query.filter_by(id=request.form['performance_id']).first()
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    if participant not in performance.participants:
        return bad_request(_('participante no está agregado a esta presentación'))
    addHistoryEntry('Eliminado','Detalle de Interpretación: {}({}) agregado a {} en {}'.format(participant.person.get_full_name(),
                                                                                              participant.activity.name,
                                                                                              performance.musical_piece.name,
                                                                                              performance.event.name[0:40]))
    performance.participants.remove(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/uploadajax', methods=['POST'])
def upldfile():
    files = request.files['file']
    if not files:
        return bad_request(_('debe incluir al menos un archivo'))    
    if not request.form['event_id']:
        return bad_request(_('debe incluir el id del evento'))
    if not request.form['description']:
        return bad_request(_('debe incluir una descripcion'))   
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
def deleteFile():
    if not request.form['medialink_id']:
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
  

