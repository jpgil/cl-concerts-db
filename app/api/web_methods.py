# -*- coding: utf-8 -*-


from app.models import  Event, Instrument, MusicalEnsemble
import logging
from datetime import datetime

from sqlalchemy import and_

from app import cache
logger=logging.getLogger('werkzeug')

# we'll use the intersection method to filtering out events
def intersection(lst1, lst2): 
<<<<<<< HEAD
    # # Use of hybrid method 
    # temp = set(lst2) 
    # lst3 = [value for value in lst1 if value in temp] 
    # return list(set(lst3))
    return list( set(lst1).intersection(set(lst2)) ) 
=======
    return list(set(lst1).intersection(lst2))

>>>>>>> 7468d2262ab2f3b2f45ea7209d67dfdad6386658

def search_events(keywords,filters,offset,limit):
    params=filters
    events_info=cache.get('events_info')
    # get date related stuf
    [start_year,start_month, start_day]=params['start_date'].split('-')
    [end_year,end_month, end_day]=params['end_date'].split('-')
    start_date=datetime.strptime(params['start_date'], '%Y-%m-%d')
    end_date=datetime.strptime(params['end_date'], '%Y-%m-%d')

    # first filter: by year
    events_query=Event.query.filter(and_(Event.year >= start_year,Event.year <= end_year ))
    
    #if we're lookin for name, add it to the filter
    if params['name']:
        events_query=events_query.filter(Event.name.ilike('%{}%'.format(params['name'])))
    
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
        params['musical_ensemble_name'].extend(musical_ensemble_ids)    
    
    # now we'll iterate throug the params, performing the intersections between all
    # params which meet the condition, the params which are managed in a different way
    params.pop('musical_ensemble_type')
    params.pop('instrument_type')
    params.pop('name')
    params.pop('start_date')
    params.pop('end_date')
    
    events_ids=[event.id for event in events_query.all()]
    # and finally, we start happyly intersecting
    for param_key in params:
        if params[param_key]:
            events_for_param=[]
            for param_value in params[param_key]:
                if param_value in events_info[param_key].keys():
                    events_for_param.extend(events_info[param_key][param_value] )  
            events_ids=intersection(events_ids, events_for_param)
 
    
    # and finally, we remove all the elements which are out of the complete date
    
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
        print(event)
 


    
                    
    
                    
                    
            
    
                             
