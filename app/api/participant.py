from app.api import bp
from flask import request
from app import db
from app.api.errors import bad_request
from app.models import Activity, Event, Person, Participant, MusicalPiece, PremiereType, Performance
from flask_babel import _
from flask import jsonify

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
    db.session.delete(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
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
    db.session.delete(performance)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
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
    performance.participants.remove(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response