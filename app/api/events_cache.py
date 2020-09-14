# -*- coding: utf-8 -*-
from app.models import  Event, Person, Instrument, MusicalEnsemble, MusicalPiece
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
        refresh_cache()

    

@fasteners.interprocess_locked(Config.CACHE_DEFAULT_DEST+"/cache.refresh_cache.lock")        
def refresh_cache():
    timeout = timedelta(seconds = Config.CACHE_TIMEOUT)
    
    # first case: the cached data is still valid. We do nothing in this case
    current_time=datetime.now()
    if current_time - cache.get('last_update') <= timeout:
        print('data is up to date')
        return
    
    # second case: the data in disk is newer that the cached data
    # this happens if a different thread updated the cache is disk
    # If that's the case, we'll use the values read from disk to update the data
    # but we need to make sure all data can be read from disk
        
    # read from disk
    events_from_file=read_from_file('events')
    people_from_file=read_from_file('people')
    instruments_from_file=read_from_file('instruments')
    musical_pieces_from_file=read_from_file('musical_pieces')
    musical_ensembles_from_file=read_from_file('musical_ensembles')
    last_update_from_file=read_from_file('last_update')
    # this will be true if all the data is available from fisk
    all_read_from_file=last_update_from_file and events_from_file and people_from_file and instruments_from_file and musical_pieces_from_file and musical_ensembles_from_file and last_update_from_file 
    # we also need to make sure the data in the disk cache is not out dated
    disk_data_up_to_date = current_time - last_update_from_file <= timeout
    # we can use the data from the disk to set the cache online if:
    # the data from disk could be all read and it's up to date
    if disk_data_up_to_date or all_read_from_file:
        # in that case, we set the cache from disk
        print("using cache from disk")
        cache.set('people',people_from_file)
        cache.set('instruments',instruments_from_file)
        cache.set('musical_pieces',musical_pieces_from_file)
        cache.set=save_to_file('musical_ensembles',musical_ensembles_from_file)
        cache.set('last_update',last_update_from_file)
        return
    else:
        print("data outdated or cache not found. refreshing....")
        events={}
        for event in Event.query.all():
            event_id=event.id # just to avoid some typing..
            append_event(events,"cycle",event.cycle_id,event_id)
            append_event(events,"event_type",event.event_type_id, event_id)
            for organization in event.organizations:
                append_event(events,"organized",organization.id, event_id)
            append_event(events,"location",event.location_id, event_id)
            append_event(events,"city",event.location.city_id, event_id)   
            for participant in event.participants.all():
                append_event(events,"participant_name",participant.person_id, event_id)   
                if participant.person:
                    append_event(events,"participant_gender",participant.person.gender_id, event_id)
                    for country in participant.person.nationalities:
                        append_event(events,"participant_country",country.id, event_id)
                if participant.activity_id:
                    append_event(events,"activity",participant.activity_id, event_id)
                if participant.musical_ensemble_id:
                    append_event(events,"musical_ensemble_name",participant.musical_ensemble_id, event_id)    
            for performance in event.performances.all():
                append_event(events,"musical_piece",performance.musical_piece_id, event_id)
                append_event(events,"premier_type",performance.premiere_type_id, event_id)
                for instrument in performance.musical_piece.instruments:
                    append_event(events,"instruments",instrument.id, event_id)
                for composer in performance.musical_piece.composers:
                    append_event(events,"compositor_name",composer.id, event_id)
                    append_event(events,"compositor_gender",composer.gender_id, event_id)
                    for country in composer.nationalities:
                        append_event(events,"compositor_country",country.id, event_id)
        
        # saving events to file and cache
        save_to_file('events',events)
        # saving people names to file and cache
        people={}
        for person in Person.query.all():
            people[person.id]=person.get_name()
        save_to_file('people',people)
        cache.set('people',people)
        # saving instruments names to file and cache
        instruments={}
        for instrument in Instrument.query.all():
            instruments[instrument.id]=instrument.name
        save_to_file('instruments',instruments)
        cache.set('instruments',instruments)
        # saving musical_pieces names to file and cache
        musical_pieces={}
        for musical_piece in MusicalPiece.query.all():
            musical_pieces[musical_piece.id]=musical_piece.name      
        save_to_file('musical_pieces',musical_pieces)   
        cache.set('musical_pieces',musical_pieces)      
        # saving musical_ensembles names to file and cache
        musical_ensembles={}
        for musical_ensemble in MusicalEnsemble.query.all():
            musical_ensembles[id]=musical_ensemble.name
        save_to_file('musical_ensembles',musical_ensembles)
        cache.set('musical_ensembles',musical_ensembles)
        # saving current time to file and cache
        current_time=datetime.now() 
        save_to_file('last_update',current_time)
        cache.set('last_update',current_time)


@fasteners.interprocess_locked(Config.CACHE_DEFAULT_DEST+"/cache.read.lock")
def read_from_file(name):
    try:
        f_data=open("{}/{}.cache".format(Config.CACHE_DEFAULT_DEST,name),'rb')
        data=pickle.load(f_data)
    except:
        return None
    return data

def save_to_file(name,data):
    if not path.exists(Config.CACHE_DEFAULT_DEST):
        makedirs(Config.CACHE_DEFAULT_DEST)
    f_data=open("{}/{}.cache".format(Config.CACHE_DEFAULT_DEST,name),'wb')
    pickle.dump(data, f_data)  
    f_data.close()

    
    
    
    
    

