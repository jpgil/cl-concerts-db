# -*- coding: utf-8 -*-

from app.models import  Event, Organization, Participant, Country, Performance,\
    Instrument
import logging
from datetime import datetime
from sqlalchemy_filters import apply_filters

logger=logging.getLogger('werkzeug')

# we'll use the intersection method to filtering out events
def intersection(lst1, lst2): 
    # Use of hybrid method 
    temp = set(lst2) 
    lst3 = [value for value in lst1 if value in temp] 
    return list(set(lst3))  

def search_events(keywords,filters,offset,limit):
    params=filters
    # filter_spec will manage the 'or' case
    query=Event.query
    if params['name']:
#   I think it's a better idea to look the full text under name, so there is no
#    need to iterate
#        for name in params['name']:
#            filter_spec['or'].append({'field': 'name', 'op': 'ilike', 'value': "%{}%".format(name)})
        query=query.filter(Event.name.ilike('%{}%'.format(params['name'])))

    # each time a filter is applied, the resulting query will be filtered again
    # in this way, we're managing the 'and' between fields in the advanced filters

    # this parameters are 1 to 1, easy to restrict (n to 1 in this case since 
    # each particular 'field' can have multiples selections (in each dropdown menu)
    simple_params=[ "cycle","event_type","location"]
    for param in simple_params:
        filter_spec={ 'or' : []}
        # we'll do this for each param
        for param_occurrence in params[param]:
            # we'll do this for all selected item of this param
            filter_spec['or'].append({'field': param+'_id', 'op': 'eq', 'value': param_occurrence })
        if filter_spec['or']:
            query=apply_filters(query,filter_spec)
    [start_year,start_month, start_day]=params['start_date'].split('-')
    [end_year,end_month, end_day]=params['end_date'].split('-')
    # since filtering for month and day without having a date field in the event
    # (for example, start date 1900-11-10 should allow 1901-01-10 sincejson.loads(json_params)
    # 1901 > 1900 but 01 < 11!, but for years this is ok. We'll do the filtering later
    # for months and days
    filter_spec={ 'and' : []}
    filter_spec['and'].append({'field': 'year', 'op': 'ge', 'value': int(start_year)})
    filter_spec['and'].append({'field': 'year', 'op': 'le', 'value': int(end_year)})
    query=apply_filters(query,filter_spec)
    
    # now the query will filter all the events not matching with the above queries
    # and save their ids in a list and we'll finish the date filter
    start_date=datetime.strptime(params['start_date'], '%Y-%m-%d')
    end_date=datetime.strptime(params['end_date'], '%Y-%m-%d')
    events_ids=[]
            
    for event in query.all():
        # since we're iterating through events/ let's use this oportunity for checking if 
        # the city is what we're looking for
        if params['city']:
            if event.location.city_id not in params['city']:
                continue
        [event_min_date,event_max_date]=event.get_dates()
        if event_min_date <= end_date and event_max_date >= start_date:
            events_ids.append(event.id)
    # yeii! we have now all the simple filters applied. Nostart_datew let's go
    # to the mulplies ones. We will inverse the approach here; we'll apply the
    # filters to the child. Each case is different, so we'll manage them case by case
    
    # first: organizations
    # piece of cake, we get the list of all organizations which are added to the filter

    if params["organized"]:
        orgs=Organization.query.filter(Organization.id.in_(params["organized"])).all()
        # now we iterate through all of them and generate the list of event ids which
        # are referenced by this organizations
        temp_events_id=[]
        for org in orgs:
            for event in org.events:
                temp_events_id.append(event.id)
        events_ids=intersection(events_ids,temp_events_id)      
    

####################  FILTERING BY PARTICIPANTS ########################
    
    # we'll filter thought participants only if any of its parameter is given
    if params["participant_name"] or params["activity"] or  params["participant_country"] or\
       params["participant_gender"] or params["musical_ensemble_name"]\
       or params["musical_ensemble_type"]:
        # next! participants: we'll filter them out using name, gender, activity and nationalities
        #first list of participants. 
        participants_query=Participant.query.filter(Participant.event_id.in_(events_ids))
        if params["participant_name"]:
            participants_query=participants_query.filter(Participant.person_id.in_(params["participant_name"]))
        if params["activity"]:
            participants_query=participants_query.filter(Participant.activity_id.in_(params["activity"]))
        # MusicalEnsembles could be filtered out by their type
        if params["musical_ensemble_name"]:            
            participants_query=participants_query.filter(Participant.musical_ensemble_id.in_(params["musical_ensemble_name"]))

        # the following code is not for faint hearts. It's so ugly that I not even
        # dare to use it in a Yo Mamma joke. This is done for managing cases where
        # we go to a third layer of information 
        temp_events_id=[]
        # first, we get the list of countries, if it was provided
        country_list=[]
        if params["participant_country"]:
            country_list=Country.query.filter(Country.id.in_(params["participant_country"])).all()
        for participant in participants_query.all():
            # not complying with any of the condition will get the participant
            # out of the final listjson.loads(json_params)
            if not participant.person:
                continue
            if params["participant_gender"]:
                if participant.person.gender_id not in params["participant_gender"]:
                    continue
            if params["participant_country"]:
                if not participant.person:
                    continue
                if not intersection(country_list,participant.person.nationalities):
                    continue
            if params["musical_ensemble_type"]: 
                if not participant.musical_ensemble:
                    continue
                if participant.musical_ensemble.musical_ensemble_type_id not in params["musical_ensemble_type"]:
                    continue
            # the participant passed all the filters! so we just add its event the list
            temp_events_id.append(participant.event_id)
        # the final list will be temp_events_id, I'm just intersecting it for
        # clean up duplicates and paranoia
        events_ids=intersection(events_ids,temp_events_id)
        
# compositor_gender": [],"compositor_country": [],
#    "premier_type": [],"musical_piece": [],"instrument_type": [],"musical_ensemble_name": [],
#    "": []   
        
####################  FILTERING BY PERFORMANCES ########################        

    if params["premier_type"] or  params["musical_piece"] or params["compositor_country"] or\
            params["instruments"] or  params["instrument_type"] or params["compositor_gender"] or\
            params["compositor_name"]:
        #initial list of performances. 
        temp_events_id=[]
        performance_query=Performance.query.filter(Performance.event_id.in_(events_ids))
        if params["premier_type"]:
            performance_query=performance_query.filter(Performance.premiere_type_id.in_(params["premier_type"]))
        if params["musical_piece"]:
             performance_query=performance_query.filter(Performance.musical_piece_id.in_(params["musical_piece"]))
        performances=performance_query.all()

##     FILTERING COMPOSERS
        country_list=None
        if params["compositor_country"]:
            country_list=Country.query.filter(Country.id.in_(params["compositor_country"])).all()
        for performance in performances:
            check_composers=False
            check_instruments=False
            composer_found=False
            instrument_found=False
            if  params["compositor_country"] or params["compositor_name"] or params["compositor_gender"]:
                check_composers=True
                for composer in performance.musical_piece.composers:
                    if params["compositor_country"]:
                        if not intersection(composer.nationalities, country_list):
                            continue
                    if params["compositor_name"]:
                        if composer.id not in params["compositor_name"]:
                            continue
                    if params["compositor_gender"]:
                         if composer.gender_id not in params["compositor_gender"]:
                             continue
                    composer_found=True
            if (params["instrument_type"] or params["instruments"]):
                check_instruments=True
                instrument_query=Instrument.query
                if params["instruments"]:
                    instrument_query=instrument_query.filter(Instrument.id.in_(params["instruments"]))  
                if params["instrument_type"]:
                    instrument_query=instrument_query.filter(Instrument.instrument_type_id.in_(params["instrument_type"])) 
                instrument_list=instrument_query.all()
                if intersection(instrument_list, performance.musical_piece.instruments):
                    instrument_found=True
            if check_composers and not composer_found:
                continue
            if check_instruments and not instrument_found:
                continue
            temp_events_id.append(performance.event_id)
            
        # sorted by id, but this could be easily changed
        events_ids=sorted(intersection(events_ids,temp_events_id))
    response={}
    total=events_ids.__len__()
    response["total"]=total

    if offset >= total:
        response["rows"]=[]
    elif offset+limit >= total:
        response["rows"]=events_ids[offset:]
    else:
        response["rows"]=events_ids[offset:offset+limit]
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
                        
                     
