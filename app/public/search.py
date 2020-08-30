import logging
from flask import request, session
from app.public.test_db import TEST, TEST2
from app.models import EventType, City, Gender, Country, PremiereType, InstrumentType, MusicalEnsembleType

logger = logging.getLogger('werkzeug')

# ------------------------------
# Cache para listas desplegables
# ------------------------------


class SelectCached:
    def __init__(self, obj=None):
        if obj:
            self.obj = obj
            self.name = type(obj()).__name__
            logger.debug('%s created' % self.name )

    def get(self):
        if '_cache_%s' % self.name not in session.keys() or session['_cache_%s' % self.name] == '':
            session['_cache_%s' % self.name] = [
                {'value': v.id, 'label': v.get_name()} for v in self.obj.query.all()]
            session.modified = True
            logger.debug('Data %s queried to DB' % self.name)
        else:
            logger.debug( 'Data %s returned from session cache' % self.name)
        return session['_cache_%s' % self.name]


# ------------------------------
# Resultados de Busqueda de Eventos
# ------------------------------
def event_list_PREVIO(keywords="", offset=0, limit=10):
    # return { 'rows': TEST , 'total': 100 }
    T = { "rows": TEST2['rows'][offset:offset+limit], 'total': len(TEST2['rows']) }
    return T

# Return a raw set of events paginated
def event_list(keywords="", offset=0, limit=10):
    T = TEST[:]
    return T

def get_event(id=id):
    found = False
    for t in TEST:
        if int(t['event_id']) == int(id):
            found = t
    if found:
        return found
    else:
        # return {}
        raise ValueError()


# ------------------------------
# Filtros de Busqueda
# ------------------------------
def validate_int(x):
    try:
        if str(x) == str(int(x)):
            return int(x)
    except:
        return None
    return None

def validate_int_list(X):
    if all([validate_int(x) for x in X]):
        return [ int(x) for x in X]
    else:
        return []

def validate_str(x):
    try:
        if x == str(x):
            return x
    except:
        return None
    return None

class SideBarFilters:
    """
    Clase conveniente para el prellenado del formulario de filtros de busqueda
    """
    def __init__(self):
        self.filters = {
            'evento': [
                { 'name': 'name', 'type': 'text', 'placeholder': 'Nombre o Información', 'url': 'events' },
                { 'name': 'cycle', 'type': 'select2', 'placeholder': 'Ciclo', 'url': 'cycles' },
                { 'name': 'event_type', 'type': 'select2', 'placeholder': 'Tipo de Evento', 'url': 'eventtypes',
                    'values': SelectCached(EventType).get()
                }
            ],
            'lugar': [
                { 'name': 'organized', 'type': 'select2', 'placeholder': 'Organizador(es)', 'url': 'organizations' },
                { 'name': 'city', 'type': 'select2', 'placeholder': 'Ciudad', 'url': 'cities',
                    'values': SelectCached(City).get()
                },
                { 'name': 'location', 'type': 'select2', 'placeholder': 'Locación', 'url': 'locations' }
            ],
            'participantes': [
                {'name': 'participant_name', 'type': 'select2',
                    'placeholder': 'Nombre de participante', 'url': 'people'},
                {'name': 'participant_gender', 'type': 'select', 'placeholder': 'Género',
                    'values': SelectCached(Gender).get()
                },
                {'name': 'participant_country', 'type': 'select2', 'placeholder': 'País', 'url': 'countries' },
                {'name': 'activity', 'type': 'select2',
                    'placeholder': 'Actividad', 'url': 'activities'},
            ],
            'compositores': [
                {'name': 'compositor_name', 'type': 'select2',
                    'placeholder': 'Compositor', 'url': 'composer'},
                {'name': 'compositor_gender', 'type': 'select', 'placeholder': 'Género',
                    'values': SelectCached(Gender).get()
                },
                {'name': 'compositor_country', 'type': 'select2', 'placeholder': 'País', 'url': 'countries' }
            ],
            'repertorio': [
                {'name': 'premier_type', 'type': 'select2', 'placeholder': 'Estreno', 'url': 'premieretypes',
                    'values': SelectCached(PremiereType).get()
                },
                {'name': 'musical_piece', 'type': 'select2', 'placeholder': 'Obra', 'url': 'musicalpiecesclean'},
                {'name': 'instruments', 'type': 'select2',
                    'placeholder': 'Instrumentos', 'url': 'instruments'},
                {'name': 'instrument_type', 'type': 'select2', 'placeholder': 'Tipo de Instrumentos', 'url': 'instrumenttypes',
                    'values': SelectCached(InstrumentType).get()
                }
            ],
            'agrupaciones': [
                {'name': 'musical_ensemble_name', 'type': 'select2',
                    'placeholder': 'Nombre de agrupación', 'url': 'musicalensembles'},
                {'name': 'musical_ensemble_type', 'type': 'select2', 'placeholder': 'Tipo de agrupación', 'url': 'musicalensembletypes',
                    'values': SelectCached(MusicalEnsembleType).get()
                }
            ]
        }
        self.evento
        self.lugar
        self.participantes
        self.compositores
        self.repertorio
        self.agrupaciones
        self.keywords
        self.fecha
    
    @property
    def all_filters(self):
        all_f = []
        for key in self.filters:
            all_f += self.filters[key]

        all_f.append({'name': 'keywords', 'type': 'text',
                      'placeholder': 'keywords'} )
        all_f.append({'name': 'start_date', 'type': 'date',
                      'placeholder': '[Desde]', 'default': '1/1/1945'} )
        all_f.append({'name': 'end_date', 'type': 'date',
                      'placeholder': '[Hasta]', 'default': '31/12/1995'})
        return all_f

    @property
    def query(self):
        # query = app.main.search(  # Johnny elige el nombre!!
        #     keywords=keywords,
        #     filters=filter,
        #     offset=offset,
        #     limit=limit)
        # # Ejemplo real de filter
        # keywords = "simple string"
        # filter = {
        #     "start_date": "YYYY-MM-DD", "end_date": "",
        #     "name": "Texts here",
        #     "cycle": [], "event_type": [], "organized": [], "city": [], "location": [],
        #     "participant_name": [], "participant_gender": [], "participant_country": [], "activity": [],
        #     "instruments": [], "compositor_name": [], "compositor_gender": [], "compositor_country": [],
        #     "premier_type": [], "musical_piece": [], "instrument_type": [], "musical_ensemble_name": [],
        #     "musical_ensemble_type": []
        # }
        query={ 'filters': {} }
        for f in self.all_filters:
            if f['name'] not in ['keywords']:
                val = self.prefill(f['name'])
                if f['name'] not in ['name', 'start_date', 'end_date']:
                    if val == '':
                        val = []
                    elif type(val) != list:
                        val = [val]
                query['filters'][f['name']] = val
        query['keywords'] = self.prefill('keywords')

        # Fix date format

        #TODO: validate in validators, not here.
        def format_date(d):
            try:
                f = d.split('/')
                d, m, y = int(f[0]), int(f[1]), int(f[2])
                return '%04d-%02d-%02d' % (y, m, d)
                return '%s-%s-%s' % (y, m, d)
            except:
                return '1900-1-1'
        query['filters']['start_date'] = format_date(
            query['filters']['start_date'])
        query['filters']['end_date'] = format_date(
            query['filters']['end_date'])

        return query

    # Rewerite session from request values
    def updateFromRequest(self):

        validate = {'select': validate_int, 'select2': validate_int_list,
                    'text': validate_str, 'date': validate_str}

        for f in self.all_filters:

            if 'default' in f.keys():
                default = f['default']
            else:
                default = ''

            # Multivalues must be extracted with request.args.getlist() = [1,2,...,N]
            if f['type'] == 'select2':
                getfunc = request.args.getlist
            else:
                getfunc = request.args.get

            if f['name'] in request.args and getfunc(f['name']):
                logger.debug('%s will be included to value %s' %
                            (f['name'], getfunc(f['name'])))

                session['filt_%s' % f['name']] = validate[f['type']](
                    getfunc(f['name'])) or default
            else:
                logger.debug('%s to be cleared' % f['name'])
                session['filt_%s' % f['name']] = default

            session.modified = True


    # for each field in filters bring values from flask session
    def prefill(self, name, default=''):
        if 'filt_%s' % name not in session.keys():
            session['filt_%s' % name] = default
            session.modified = True
        return session['filt_%s' % name]


    def format_fields(self, fields):
        show = False
        for f in fields:
            if 'default' in f.keys():
                default = f['default']
            else:
                default = ""
            f['value'] = self.prefill(f['name'], default=default)
            show = show or f['value'] != default
        return dict(fields=fields, show=show)

    @property
    def fecha(self):
        default = {
            'start_date': '1/1/1945',
            'end_date': '31/12/1995'
        }
        response = {
            'start_date': self.prefill('start_date', default=default['start_date']),
            'end_date': self.prefill('end_date', default=default['end_date']),
        }
        response['show'] = response['start_date'] != default['start_date'] or response['end_date'] != default['end_date']
        return response

    @property
    def keywords(self):
        return self.prefill('keywords', 'text')

    @property 
    def evento(self):
        return self.format_fields(self.filters['evento'])

        
    @property
    def lugar(self):
        return self.format_fields(self.filters['lugar'])


    @property
    def participantes(self):
        return self.format_fields(self.filters['participantes'])

    @property
    def compositores(self):
        return self.format_fields(self.filters['compositores'])

    @property
    def repertorio(self):
        return self.format_fields(self.filters['repertorio'])
        
    @property
    def agrupaciones(self):
        return self.format_fields(self.filters['agrupaciones'])





