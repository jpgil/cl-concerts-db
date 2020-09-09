# -*- coding: utf-8 -*-
from app.models import  Event
import logging
from app import cache
from config import Config 
import pickle, fasteners
from datetime import datetime, timedelta
from os import path, makedirs

logger=logging.getLogger('werkzeug')

def append_event(events_info,param,type_key,event_id):
    if not param in events_info:
        events_info[param]={}
    if not type_key in events_info[param]:
        events_info[param][type_key]=[event_id]
    else:
        events_info[param][type_key].append(event_id)

def refresh_cache_thread(app):
    with app.app_context():
        events_info=refresh_events_info_cache()
        cache.set('events_info',events_info)
        cache.set('last_update',datetime.now())

@fasteners.interprocess_locked(Config.CACHE_DEFAULT_DEST+"/cache.update.lock")        
def refresh_events_info_cache():
    timeout = timedelta(seconds = Config.CACHE_TIMEOUT)
    values_obtained_from_file=read_events_from_file()
    data_outdated=False
    if values_obtained_from_file:
        [events_info,last_update]=read_events_from_file()
        data_outdated=datetime.now() - last_update > timeout
        
    if  data_outdated or not values_obtained_from_file:
        events_info={}
        for event in Event.query.all():
            event_id=event.id # just to avoid some typing..
            append_event(events_info,"cycle",event.cycle_id,event_id)
            append_event(events_info,"event_type",event.event_type_id, event_id)
            for organization in event.organizations:
                append_event(events_info,"organized",organization.id, event_id)
            append_event(events_info,"location",event.location_id, event_id)
            append_event(events_info,"city",event.location.city_id, event_id)   
            for participant in event.participants.all():
                append_event(events_info,"participant_name",participant.person_id, event_id)   
                if participant.person:
                    append_event(events_info,"participant_gender",participant.person.gender_id, event_id)
                    for country in participant.person.nationalities:
                        append_event(events_info,"participant_country",country.id, event_id)
                if participant.activity_id:
                    append_event(events_info,"activity",participant.activity_id, event_id)
                if participant.musical_ensemble_id:
                    append_event(events_info,"musical_ensemble_name",participant.musical_ensemble_id, event_id)    
            for performance in event.performances.all():
                append_event(events_info,"musical_piece",performance.musical_piece_id, event_id)
                append_event(events_info,"premier_type",performance.premiere_type_id, event_id)
                for instrument in performance.musical_piece.instruments:
                    append_event(events_info,"instruments",instrument.id, event_id)
                for composer in performance.musical_piece.composers:
                    append_event(events_info,"compositor_name",composer.id, event_id)
                    append_event(events_info,"compositor_gender",composer.gender_id, event_id)
                    for country in composer.nationalities:
                        append_event(events_info,"compositor_country",country.id, event_id)
        save_events_to_file(events_info)

    return events_info


@fasteners.interprocess_locked(Config.CACHE_DEFAULT_DEST+"/cache.read.lock")
def read_events_from_file():
    try:
        f_events_info=open(Config.CACHE_DEFAULT_DEST+'/events_info.cache','rb')
        f_last_update=open(Config.CACHE_DEFAULT_DEST+'/last_update.cache','rb')        

        events_info=pickle.load(f_events_info)
        last_update=pickle.load(f_last_update)

        f_events_info.close()
        f_last_update.close()
    except: 
        return None
    return [events_info,last_update]


def save_events_to_file(events_info):
    if not path.exists(Config.CACHE_DEFAULT_DEST):
        makedirs(Config.CACHE_DEFAULT_DEST)
    f_events_info=open(Config.CACHE_DEFAULT_DEST+'/events_info.cache','wb')
    f_last_update=open(Config.CACHE_DEFAULT_DEST+'/last_update.cache','wb')  
    pickle.dump(events_info, f_events_info)  
    pickle.dump(datetime.now(), f_last_update)  
    f_events_info.close()
    f_last_update.close()
    
    
    
    
    

