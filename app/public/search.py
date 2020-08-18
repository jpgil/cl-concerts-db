import logging
from app.public.test_db import TEST, TEST2
from app.models import EventType, City, Gender, Country, PremiereType, InstrumentType, MusicalEnsembleType

logger = logging.getLogger('werkzeug')

# ------------------------------
# Cache para listas desplegables
# ------------------------------

class ItemCache:
    def get(self):
        # data = [ dict( value=v.id, label=v.get_name() ) for v in self.obj.all() ]
        data = [{'value':v.id, 'label':v.get_name()} for v in self.obj.query.all()]
        logger.info( 'Data is %s' % data)
        return data

class SelectEventyType(ItemCache):
    obj = EventType

class SelectCiudad(ItemCache):
    obj = City

class SelectGenero(ItemCache):
    obj = Gender

class SelectPais(ItemCache):
    obj = Country

class SelectPremierTypes(ItemCache):
    obj = PremiereType

class SelectInstrumentTypes(ItemCache):
    obj = InstrumentType

class SelectMusicalEnsembleType(ItemCache):
    obj = MusicalEnsembleType


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

class SideBarFilters:
    """
    Clase conveniente para el prellenado del formulario de filtros de busqueda
    """
    def format_fields(self, fields):
        # Prefill values
        for f in fields:
            f['value'] = ""

        return dict(fields=fields, show=any([v['value'] for v in fields]))

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
                'values': SelectEventyType().get()
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
                'values': SelectCiudad().get()
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
                'values': SelectGenero().get()
            },
            {
                'name': 'participante_pais', 'type': 'select', 'placeholder': 'País',
                'values': SelectPais().get()
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
                'values': SelectGenero().get()
            },
            {
                'name': 'compositor_pais', 'type': 'select', 'placeholder': 'País',
                'values': SelectPais().get()
            }
        ]
        return self.format_fields(fields)

    @property
    def repertorio(self):
        fields = [
            {
                'name': 'repertorio_estreno', 'type': 'select', 'placeholder': 'Estreno',
                'values': SelectPremierTypes().get()
            },
            {
                'name': 'repertorio_obra', 'type': 'text', 'placeholder': 'Obra'
            },
            {
                'name': 'repertorio_instrumentos', 'type': 'select', 'placeholder': 'Tipo de Instrumentos',
                'values': SelectInstrumentTypes().get()
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
                'values': SelectMusicalEnsembleType().get()
            } 
        ]
        return self.format_fields(fields)





