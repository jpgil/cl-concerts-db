# -*- coding: utf-8 -*-


from app.models import  Event, Instrument, MusicalEnsemble
#import logging
from datetime import datetime
from fuzzywuzzy import process 
from config import Config 
from sqlalchemy import and_
import traceback
from app import cache
from werkzeug.local import LocalProxy
from flask import current_app
logger = LocalProxy(lambda: current_app.logger)

# we'll use the intersection method to filtering out events
def intersection(lst1, lst2): 
    return list(set(lst1).intersection(lst2))

def fuzzy_search(look_for,search_into):
    founds=process.extractBests(look_for,search_into,\
                               score_cutoff=Config.SEARCH_SCORE_CUTOFF,limit=Config.SEARCH_LIMIT)
    founds_dict={}
    for found in founds:
        founds_dict[found[2]]=found[0]
    return founds_dict

def add_to_dict(dictionary,key,list_value):
    """This methods adds a value in a list under dictionary[key]
    if the key doesn't exist, it creates the list and then append the value
    to it"""
    if key not in dictionary:
        dictionary[key]=[]
    dictionary[key].append(list_value)

# basically, the same method get_name from Person model
def get_name(last_name,first_name):
    if last_name and first_name:
        return '{}, {}'.format(last_name,first_name) 
    else:
        return last_name if last_name else first_name
        
def search_events(keywords,filters,offset,limit):
    params=filters
    events_info=cache.get('events')    
    if not events_info:
        logger.error("events_info is empty")
        logger.error(cache.get('events') )

    # get date related stuf
    [start_year,start_month, start_day]=params['start_date'].split('-')
    [end_year,end_month, end_day]=params['end_date'].split('-')
    start_date=datetime.strptime(params['start_date'], '%Y-%m-%d')
    end_date=datetime.strptime(params['end_date'], '%Y-%m-%d')

    # first filter: by year
    events_query=Event.query.filter(and_(Event.year >= start_year,Event.year <= end_year ))
    # filter by name
    if params['name']:
        events_query=events_query.filter(Event.name.ilike('%'+params['name']+'%')) 


    # if we're looking for an instrument type, we actually can just look for the all instruments
    # of that type 
    if params['instrument_type'] :
        instrument_query=Instrument.query.filter(Instrument.instrument_type_id.in_(params['instrument_type']))
        instruments_ids=[instrument.id for instrument in instrument_query.all()]
        params['instruments'].extend(instruments_ids)

    # if we're looking for an enssemble type, we actually can just look for the all ensemblles
    # of that type         
    if params['musical_ensemble_type'] :
        musical_ensemble_query=MusicalEnsemble.query.filter(MusicalEnsemble.musical_ensemble_type_id.in_(params['musical_ensemble_type']))
        musical_ensemble_ids=[musical_ensemble.id for musical_ensemble in musical_ensemble_query.all()]
        print("Musical ensemble ids={}".format(musical_ensemble_ids))
        params['musical_ensemble_name'].extend(musical_ensemble_ids)    
    
    # we'll have a different behavior depending on if keywords were provided or not
    # the easiest case: no keywords were provided, in this case, we just iterate
    # through the full list of events
    
    events_found_causes={}    
    #if not, we'll create the list of events, but just the events found
    # with it's causes
    events_ids=[event.id for event in events_query.all()]

    if keywords:
        events_names=cache.get('events_names')
        people=cache.get('people')
        instruments=cache.get('instruments')
        musical_pieces=cache.get('musical_pieces')
        musical_ensembles=cache.get('musical_ensembles')
        #last_update=cache.get('last_update')
        
        event_names_found=fuzzy_search(keywords,events_names)
        logger.debug('event_names_found:{}'.format(event_names_found))
        # for the case of people, the search works better if we search
        # separately in first and last name, however, the algorithm
        # doesn't behave to well when working in initials, since we get
        # false positives (for example, 'Carla' is found in 'C.')
        # so we'll remove the firt/last names shorter than 4 letter
        people_first_name={}
        people_last_name={}
        for person_id in people:
            if people[person_id][0].__len__() >= 4: # firt name
                people_first_name[person_id]=people[person_id][0]
            if people[person_id][0].__len__() >= 4: # last name
                people_last_name[person_id]=people[person_id][1]

        people_first_name_found=fuzzy_search(keywords,people_first_name)
        logger.debug('people_first_name_found:{}'.format(people_first_name_found))
        people_last_name_found=fuzzy_search(keywords,people_last_name)
        logger.debug('people_last_name_found:{}'.format(people_last_name_found))        
        instruments_found=fuzzy_search(keywords,instruments)
        logger.debug('instruments_found:{}'.format(instruments_found))
        musical_pieces_found=fuzzy_search(keywords,musical_pieces)
        logger.debug('musical_pieces_found:{}'.format(musical_pieces_found))
        musical_ensembles_found=fuzzy_search(keywords,musical_ensembles)
        logger.debug('musical_ensembles_found:{}'.format(musical_ensembles_found))
         # merge both lists and dedup
        people_found_ids=list(set([*people_first_name_found])-set([*people_last_name_found]))+[*people_last_name_found]
        people_found={}
        for person_id in people_found_ids:
            people_found[person_id]=get_name(people[person_id][1],people[person_id][0])
        # we'll iterate throug allt he events
        for param_key in ['participant_name' , 'compositor_name', 'instruments' ,\
                          'musical_piece', 'musical_ensemble_name' ]:
            if param_key == 'participant_name':
                founds_collection=people_found
                found_string='Participante'
            if param_key == 'compositor_name':
                founds_collection=people_found
                found_string='Compositor'
            if param_key == 'instruments':
                founds_collection=instruments_found
                found_string='Instrumento'
            if param_key == 'musical_piece':
                founds_collection=musical_pieces_found
                found_string='Obra Musical'
            if param_key == 'musical_ensembles':
                founds_collection=musical_ensembles_found
                found_string='Agrupación Musical'
            for param_value in founds_collection.keys():      
                try:
                    event_ids=events_info[param_key][param_value] if param_value in events_info[param_key] else []
                    logger.debug("event_ids {}".format(event_ids))
                    for event_id in event_ids:
                            add_to_dict(events_found_causes, \
                                       event_id,\
                                    "{}: {}".format(found_string, founds_collection[param_value]))
                except Exception as e:
                    logger.error(param_value)
                    logger.error(founds_collection)
                    logger.error(events_info)
                    track = traceback.format_exc()
                    logger.error(track)
        for event_name_key in event_names_found.keys():
            add_to_dict(events_found_causes,event_name_key,"Nombre de evento: {}".format(event_names_found[event_name_key]))

        # at this point, events_found_causes contains all the events that matchs with
        # with the keyword search. For the next steps, the filters will narrow down
        # even more the search
        events_ids=intersection([*events_found_causes], events_ids)
  
    # and finally, we remove all the elements which are out of the complete date
    params.pop('musical_ensemble_type')
    params.pop('instrument_type')
    params.pop('name')
    params.pop('start_date')
    params.pop('end_date')
    

    # and finally, we start happyly intersecting
    for param_key in params:
        if params[param_key]:
            events_for_param=[]
            for param_value in params[param_key]:
                if param_value in events_info[param_key].keys():
                    events_for_param.extend(events_info[param_key][param_value] )  
            events_ids=intersection(events_ids, events_for_param)
            
    event_ids_to_return=[]
    for event in Event.query.filter(Event.id.in_(events_ids)):# query.all():
        # since we're iterating through events, getting their id and removing all 
        # events out of date
        [event_min_date,event_max_date]=event.get_dates()
        if event_min_date <= end_date and event_max_date >= start_date:
            event_ids_to_return.append(event.id)       


    response={}
        
    total=event_ids_to_return.__len__()
    response["total"]=total

    if offset >= total:
        response["rows"]=[]
    elif offset+limit >= total:
        response["rows"]=event_ids_to_return[offset:]
    else:
        response["rows"]=event_ids_to_return[offset:offset+limit]
        
    if keywords:
        events_found_causes={k: events_found_causes.get(k) for k in response["rows"]}
        response["events_found_causes"]=events_found_causes
    else:
        response["events_found_causes"]={}
        
    logger.debug("events_found_causes: {}".format(events_found_causes))
    return response
    

def test_search_events(offset,limit):
    filters = {
    "start_date": "1950-04-20", "end_date": "1995-01-20",
    "name": "Moz",
    "cycle": [4,16],"event_type": [],"organized": [],"city": [ ],"location": [],
    "participant_name": [],"participant_gender": [1],"participant_country": [],"activity": [],
    "instruments": [],"compositor_name": [],"compositor_gender": [],"compositor_country": [],
    "premier_type": [],"musical_piece": [],"instrument_type": [],"musical_ensemble_name": [],
    "musical_ensemble_type": []
    }

    keywords=""
    resp=search_events(keywords,filters,offset,limit)
    events=Event.query.filter(Event.id.in_(resp["rows"])).all()
    for event in events:
        logger.debug(event)
 


    
                    
    
                    
                    
            
    
                             
