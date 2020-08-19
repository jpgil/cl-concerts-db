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
            logger.info('Data %s queried to DB' % self.name)
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
        # # Prefill all things
        # self.evento
        # self.lugar
        # self.participantes
        # self.compositores
        # self.repertorio
        # self.agrupaciones
        # self.keywords
        pass

    def prefill(self, name, istype, default=''):
        if not istype:
            validate = validate_str
        elif istype == 'select':
            validate = validate_int
        elif istype == 'text':
            validate = validate_str
        elif istype == 'date':
            validate = validate_str
        else:
            validate = validate_int

        # Update from request
        if name in request.args:
            session['filt_%s' % name] = validate(
                request.args.get(name)) or default
            session.modified = True
        # Persistance: Fill from stored session
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
        # return dict(fields=fields, show=any([v['value'] for v in fields]))

    @property
    def fecha(self):
        default = {'desde': '1/1/1945', 'hasta': '31/12/1995'}
        response = {
            'desde': self.prefill('fecha_desde', 'date', default=default['desde']),
            'hasta': self.prefill('fecha_hasta', 'date', default=default['hasta']),
        }
        response['show'] = response['desde'] != default['desde'] or response['hasta'] != default['hasta']
        return response

    @property
    def keywords(self):
        return self.prefill('keywords', 'text')

    @property 
    def evento(self):
        fields = [
            {
                'name': 'event_name', 'type': 'text', 'placeholder': 'Nombre o Información'
            },
            {
                'name': 'event_cycle', 'type': 'text', 'placeholder': 'Ciclo'
            },
            {
                'name': 'event_type', 'type': 'select', 'placeholder': 'Tipo de Evento',
                'values': SelectCached(EventType).get()
            }
        ]
        return self.format_fields(fields)

        
    @property
    def lugar(self):
        fields = [
            {
                'name': 'lugar_organizador', 'type': 'text', 'placeholder': 'Organizador(es)'
            },
            {
                'name': 'lugar_ciudad', 'type': 'select', 'placeholder': 'Ciudad',
                'values': SelectCached(City).get()
            },
            {
                'name': 'lugar_locacion', 'type': 'text', 'placeholder': 'Locación'
            }
        ]
        return self.format_fields(fields)


    @property
    def participantes(self):
        fields = [
            {
                'name': 'participante_nombre', 'type': 'text', 'placeholder': 'Nombre de participante'
            },
            {
                'name': 'participante_genero', 'type': 'select', 'placeholder': 'Género',
                'values': SelectCached(Gender).get()
            },
            {
                'name': 'participante_pais', 'type': 'select', 'placeholder': 'País',
                'values': SelectCached(Country).get()
            },
            {
                'name': 'participante_actividad', 'type': 'text', 'placeholder': 'Actividad'
            },
            {
                'name': 'participante_instrumentos', 'type': 'text', 'placeholder': 'Instrumentos'
            }
        ]
        return self.format_fields(fields)

    @property
    def compositores(self):
        fields = [
            {
                'name': 'compositor_nombre', 'type': 'text', 'placeholder': 'Nombre de participante'
            },
            {
                'name': 'compositor_genero', 'type': 'select', 'placeholder': 'Género',
                'values': SelectCached(Gender).get()
            },
            {
                'name': 'compositor_pais', 'type': 'select', 'placeholder': 'País',
                'values': SelectCached(Country).get()
            }
        ]
        return self.format_fields(fields)

    @property
    def repertorio(self):
        fields = [
            {
                'name': 'repertorio_estreno', 'type': 'select', 'placeholder': 'Estreno',
                'values': SelectCached(PremiereType).get()
            },
            {
                'name': 'repertorio_obra', 'type': 'text', 'placeholder': 'Obra'
            },
            {
                'name': 'repertorio_instrumentos', 'type': 'select', 'placeholder': 'Tipo de Instrumentos',
                'values': SelectCached(InstrumentType).get()
            }            
        ]
        return self.format_fields(fields)
        
    @property
    def agrupaciones(self):
        fields = [
            {
                'name': 'agrupacion_nombre', 'type': 'text', 'placeholder': 'Nombre de agrupación'
            },
            {
                'name': 'agrupacion_tipo', 'type': 'select', 'placeholder': 'Tipo de agrupación',
                'values': SelectCached(MusicalEnsembleType).get()
            } 
        ]
        return self.format_fields(fields)





