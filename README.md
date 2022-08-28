# cl-concerts-db
Plataforma para almacenar y consultar una lista de conciertos de música docta en Chile

## Instalación
Se requiere Python 3.6 o superior

### Bajar repositorio
```
git clone https://github.com/jpgil/cl-concerts-db.git  
cd cl-concerts-db/
python3 -m venv venv  
```

### Configurar servidor local
```
# Instala requerimientos y chequeos iniciales
tools/00-setup-devel-environment.sh

# Sincronización de BD
tools/01-download-db-from-prod.sh 
```

## Acerca de
Proyecto a cargo de Daniela Fugellie. 
http://basedeconciertos.uahurtado.cl/public/page_about

### Equipo:
* @jpgil -- responsable
* @epikt -- developer original
* @kirlts -- traducciones
* @vlizanae -- welcome!

 Información relevante para desarrolladores y traductores en [README_DEVEL.md](README_DEVEL.md)
