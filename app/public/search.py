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
        if '_cache_%s'%self.name not in session.keys():
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
        return X
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
                { 'name': 'event_name', 'type': 'text', 'placeholder': 'Nombre o Información', 'url': 'events' },
                { 'name': 'event_cycle', 'type': 'select2', 'placeholder': 'Ciclo', 'url': 'cycles' },
                { 'name': 'event_type', 'type': 'select', 'placeholder': 'Tipo de Evento', 'url': 'eventtypes',
                    'values': SelectCached(EventType).get()
                }
            ],
            'lugar': [
                { 'name': 'lugar_organizador', 'type': 'select2', 'placeholder': 'Organizador(es)', 'url': 'organizations' },
                { 'name': 'lugar_ciudad', 'type': 'select', 'placeholder': 'Ciudad', 'url': 'cities',
                    'values': SelectCached(City).get()
                },
                { 'name': 'lugar_locacion', 'type': 'select2', 'placeholder': 'Locación', 'url': 'locations' }
            ],
            'participantes': [
                { 'name': 'participante_nombre', 'type': 'select2', 'placeholder': 'Nombre de participante', 'url': 'people' },
                { 'name': 'participante_genero', 'type': 'select', 'placeholder': 'Género',
                    'values': SelectCached(Gender).get()
                },
                { 'name': 'participante_pais', 'type': 'select', 'placeholder': 'País',
                    'values': SelectCached(Country).get()
                },
                { 'name': 'participante_actividad', 'type': 'select2', 'placeholder': 'Actividad', 'url': 'activities' },
            ],
            'compositores': [
                { 'name': 'compositor_nombre', 'type': 'select2', 'placeholder': 'Nombre_de_participante', 'url': 'people' },
                { 'name': 'compositor_genero', 'type': 'select', 'placeholder': 'Género',
                    'values': SelectCached(Gender).get()
                },
                { 'name': 'compositor_pais', 'type': 'select', 'placeholder': 'País',
                    'values': SelectCached(Country).get()
                }
            ],
            'repertorio': [
                { 'name': 'repertorio_estreno', 'type': 'select', 'placeholder': 'Estreno',
                    'values': SelectCached(PremiereType).get()
                },
                { 'name': 'repertorio_obra', 'type': 'text', 'placeholder': 'Obra', 'url': 'performances' },
                { 'name': 'repertorio_instrumentos', 'type': 'select2', 'placeholder': 'Instrumentos', 'url': 'instruments'},
                { 'name': 'repertorio_tipo_instrumentos', 'type': 'select', 'placeholder': 'Tipo de Instrumentos',
                    'values': SelectCached(InstrumentType).get()
                }
            ],
            'agrupaciones': [
                { 'name': 'agrupacion_nombre', 'type': 'select2', 'placeholder': 'Nombre de agrupación', 'url': 'musicalensembles' },
                { 'name': 'agrupacion_tipo', 'type': 'select', 'placeholder': 'Tipo de agrupación',
                    'values': SelectCached(MusicalEnsembleType).get()
                }
            ]
        }
    
    @property
    def all_filters(self):
        all_f = []
        for key in self.filters:
            all_f += self.filters[key]

        all_f.append({'name': 'keywords', 'type': 'text',
                      'placeholder': 'keywords'} )
        all_f.append({'name': 'fecha_desde', 'type': 'date',
                      'placeholder': '[Desde]', 'default': '1/1/1945'} )
        all_f.append({'name': 'fecha_hasta', 'type': 'date',
                      'placeholder': '[Hasta]', 'default': '31/12/1995'})
        return all_f


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
                logger.info('%s will be included to value %s' %
                            (f['name'], getfunc(f['name'])))

                session['filt_%s' % f['name']] = validate[f['type']](
                    getfunc(f['name'])) or default
            else:
                logger.info('%s to be cleared' % f['name'])
                session['filt_%s' % f['name']] = default

            session.modified = True


    # for each field in filters bring values from flask session
    def prefill(self, name, istype, default=''):
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
            f['value'] = self.prefill(f['name'], f['type'], default=default)
            show = show or f['value'] != default
        return dict(fields=fields, show=show)

    @property
    def fecha(self):
        default = {
            'fecha_desde': '1/1/1945',
            'fecha_hasta': '31/12/1995'
        }
        response = {
            'desde': self.prefill('fecha_desde', 'date', default=default['fecha_desde']),
            'hasta': self.prefill('fecha_hasta', 'date', default=default['fecha_hasta']),
        }
        response['show'] = response['desde'] != default['fecha_desde'] or response['hasta'] != default['fecha_hasta']
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





