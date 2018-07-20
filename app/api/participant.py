from app.api import bp
from flask import request
from app import db
from app.api.errors import bad_request
from app.models import Activity, Event, Person, Participant
from flask_babel import _
from flask import jsonify

@bp.route('/participant/add',methods=['POST'])
def add_participant():
    print('request: {}'.format(request.form))
    if not request.form['event_id'] or not request.form['person_id'] or not request.form['activity_id']:
        return bad_request(_('debe incluir event_id, person_id y activity_id'))
    activity=Activity.query.filter_by(id=request.form['activity_id']).first()
    if not activity:
        return bad_request(_('actividad no encontrada'))
    person=Person.query.filter_by(id=request.form['person_id']).first()
    if not person:   
        return bad_request(_('persona no encontrada'))
    event=Event.query.filter_by(id=request.form['event_id']).first()
    if not event:
        return bad_request(_('evento no encontrado'))   
    participants=event.participants.all()
    for participant in participants:
        # if the participant already exists, we just return nothing
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
        return bad_request(_('debe incluir participant_id'))    
    participant=Participant.query.filter_by(id=request.form['participant_id']).first()
    db.session.delete(participant)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
#    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response    
