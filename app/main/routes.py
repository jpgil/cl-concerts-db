from datetime import datetime
import json
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from guess_language import guess_language
from app import db
#from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.main.forms import EditSimpleElementForm, EditInstrumentForm, EditPersonForm
from app.models import User, Profile, History, Event, Country, City, \
    InstrumentType, Instrument, Person, PremiereType
#from app.translate import translate
from app.main import bp


def list2csv(some_list):
    return ','.join(map(str, some_list)) 

@bp.route('/favicon.ico')
def hello():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@bp.before_app_request
def before_request():
    pass
#    if current_user.is_authenticated:
#        current_user.last_seen = datetime.utcnow()
#        db.session.commit()
#        g.search_form = SearchForm()
#    g.locale = str(get_locale())
    
def view_elements(dbmodel,elementsname,title):
    page = request.args.get('page', 1, type=int)
    elements = dbmodel.query.order_by(dbmodel.name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('main/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)
    
@bp.route('/view/countries')
@login_required
def view_countries():
    return view_elements(Country,'countries',_('Países'))


@bp.route('/view/cities')
@login_required
def view_cities():
    return view_elements(City,'cities',_('Ciudades'))

@bp.route('/view/instrumenttypes')
@login_required
def view_instrumenttypes():
    return view_elements(InstrumentType,'instrumenttypes',_('Tipos de Instrumento'))

@bp.route('/view/premieretypes')
@login_required
def view_premieretypes():
    return view_elements(PremiereType,'premieretypes',_('Tipos de Premier'))

@bp.route('/view/instruments')
@login_required
def view_instruments():
    return view_elements(Instrument,'instruments',_('Instrumentos'))

@bp.route('/view/persons')
@login_required
def view_persons():
    elementsname='persons'
    title=_('Personas')
    page = request.args.get('page', 1, type=int)
    elements = Person.query.order_by(Person.last_name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('main/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)


def getItemList(dbmodel,q,page):    
    itemslist=db.session.query(dbmodel).filter(dbmodel.name.ilike(q+'%')).order_by(dbmodel.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        data["results"].append( { 'id' : item.id , 'text': item.name} )
    return jsonify(data)

def getItem(dbmodel,id):
    item=dbmodel.query.filter_by(id=id).first_or_404()
    data={ 'id' : item.id , 'text': item.name }
    return jsonify(data)

@bp.route('/list/countries')
def getCountryList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Country,q,page)

@bp.route('/list/countries/<id>')
def getCountryItem(id):
    return getItem(Country,id)


@bp.route('/list/cities')
def getCityList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(City,q,page)

@bp.route('/list/cities/<id>')
def getCityItem(id):
    return getItem(City,id)


@bp.route('/list/instrumenttypes')
def getInstrumentTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(InstrumentType,q,page)

@bp.route('/list/instrumenttypes/<id>')
def getInstrumentTypeItem(id):
    return getItem(InstrumentType,id)

@bp.route('/list/instrument')
def getInstrumentList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Instrument,q,page)

@bp.route('/list/instrument/<id>')
def getInstrumentItem(id):
    return getItem(Instrument,id)


@bp.route('/show/countries')
def testCountries():
    return render_template('main/testdropdown.html')

@bp.route('/list/premieretypes')
def getPremiereTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(PremiereType,q,page)

@bp.route('/list/premieretypes/<id>')
def getPremiereTypeItem(id):
    return getItem(PremiereType,id)


def EditSimpleElement(dbmodel,title,original_name):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    db_element = dbmodel.query.filter_by(name=original_name).first_or_404()
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name=original_name)
    if form.validate_on_submit():
        db_element.name = form.name.data
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'))
        return redirect(url_for('main.edit_elements'))
    elif request.method == 'GET':
        form.name.data = original_name
    return render_template('main/edit_simple_element.html',title=title,form=form)


@bp.route('/edit/country/<country>',methods = ['GET','POST'])
@login_required
def EditCountry(country):
    return EditSimpleElement(Country,_('Editar País'),country)
 
@bp.route('/edit/city/<city>',methods = ['GET','POST'])
@login_required
def EditCity(city):
    return EditSimpleElement(City,_('Editar Ciudad'),city)

@bp.route('/edit/instrumenttype/<instrumenttype>',methods = ['GET','POST'])
@login_required
def EditInstrumentType(instrumenttype):
    return EditSimpleElement(InstrumentType,_('Editat Tipo de Instrumento'),instrumenttype) 

@bp.route('/edit/premieretype/<premieretype>',methods = ['GET','POST'])
@login_required
def EditPremiereType(premieretype):
    return EditSimpleElement(PremiereType,_('Editat Tipo de Instrumento'),premieretype) 

def NewSimpleElement(dbmodel,title):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    form = EditSimpleElementForm(dbmodel=dbmodel,original_name='')   
    if form.validate_on_submit():
        if  dbmodel.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'))
        else:
            db.session.add(dbmodel(name=form.name.data))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.')) 
        return redirect('/editelements')
    return render_template('main/edit_simple_element.html',title=title,form=form)
 
@bp.route('/new/country', methods = ['GET','POST'])
@login_required
def NewCountry():
    return NewSimpleElement(Country,_('Agregar País'))

@bp.route('/new/city', methods = ['GET','POST'])
@login_required
def NewCity():
    return NewSimpleElement(City,_('Agregar Ciudad'))

@bp.route('/new/instrumenttype', methods = ['GET','POST'])
@login_required
def NewInstrumentType():
    return NewSimpleElement(InstrumentType,_('Agregar Tipo de Instrumento'))
    
@bp.route('/new/premieretype', methods = ['GET','POST'])
@login_required
def NewPremiereType():
    return NewSimpleElement(PremiereType,_('Agregar Tipo de Premiere'))

@bp.route('/editelements')
@login_required
def edit_elements():
    return render_template('main/edit_elements.html')    

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
  return redirect(url_for('users.edit_profile'))


@bp.route('/new/instrument', methods = ['GET','POST'])
@login_required
def NewInstrument():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    form = EditInstrumentForm(dbmodel=Instrument,original_name='')   
    if form.validate_on_submit():
        if  Instrument.query.filter_by(name=form.name.data).all().__len__() > 0:
            flash(_('Este nombre ya ha sido registrado'))
            return render_template('main/editinstrument.html',form=form,selectedElements=None)
        else:
            instrument_type = InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first_or_404()
            db.session.add(Instrument(name=form.name.data,instrument_type=instrument_type))
            db.session.commit()
            flash(_('Tus cambios han sido guardados.'))
        return redirect('/editelements')
    return render_template('main/editinstrument.html',form=form,selectedElements=None)

@bp.route('/edit/instrument/<instrument>', methods = ['GET','POST'])
@login_required
def EditInstrument(instrument):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    instrument = Instrument.query.filter_by(name=instrument).first_or_404()
    selectedElements=[]
    selectedElements.append(instrument.instrument_type.id)
    form = EditInstrumentForm(original_name=instrument.name)
    if form.validate_on_submit():
         instrument.name = form.name.data
         instrument_type = InstrumentType.query.filter_by(id=int(form.instrument_type.data[0])).first_or_404()
         instrument.instrument_type = instrument_type
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'))
         return redirect('/editelements')
    elif request.method == 'GET':
        form.name.data = instrument.name            
    return render_template('main/editinstrument.html',form=form,selectedElements=list2csv(selectedElements))    

@bp.route('/new/person', methods = ['GET','POST'])
@login_required
def NewPerson():
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    form = EditPersonForm(original_person=None)   
    if form.validate_on_submit():
        person = Person(first_name=form.first_name.data,last_name=form.last_name.data)
        person.birth_date = form.birth_date.data
        person.death_date = form.death_date.data
        person.biography= form.biography.data
        for country_id in form.nationalities.data:
            person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
        db.session.add(person)
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'))
        return redirect('/editelements')
    return render_template('main/editperson.html',form=form,title=_('Persona'),selectedElements=None)

@bp.route('/edit/person/<person_id>', methods = ['GET','POST'])
@login_required
def EditPerson(person_id):
    if (current_user.profile.name != 'Administrador' and  current_user.profile.name != 'Editor'):
        flash(_('Debe ser Administrador/Editor para entrar a esta página'))
        return render_template(url_for('users.login'))
    person = Person.query.filter_by(id=person_id).first_or_404()
    form = EditPersonForm(person)
    selectedElements=[]
    for nationality in person.nationalities:
        selectedElements.append(nationality.id)
    if form.validate_on_submit():
         person.first_name = form.first_name.data
         person.last_name = form.last_name.data
         person.birth_date = form.birth_date.data
         person.death_date = form.death_date.data
         person.biography= form.biography.data
         person.nationalities.clear()
         for country_id in form.nationalities.data:
             person.nationalities.append(Country.query.filter_by(id=country_id).first_or_404())
         db.session.commit()
         flash(_('Tus cambios han sido guardados.'))
         return redirect('/editelements')
    elif request.method == 'GET':
         form.first_name.data = person.first_name
         form.last_name.data = person.last_name
         form.birth_date.data = person.birth_date
         form.death_date.data = person.death_date
         form.biography.data = person.biography
    return render_template('main/editperson.html',form=form,title=_('Persona'),selectedElements=list2csv(selectedElements))    



#
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.date.desc.desc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('main.explore', page=events.prev_num) \
        if events.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=events.items, next_url=next_url,
                           prev_url=prev_url)

#
#@bp.route('/user/<username>')
#@login_required
#def user(username):
#    user = User.query.filter_by(username=username).first_or_404()
#    page = request.args.get('page', 1, type=int)
#    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
#        page, current_app.config['POSTS_PER_PAGE'], False)
#    next_url = url_for('main.user', username=user.username,
#                       page=posts.next_num) if posts.has_next else None
#    prev_url = url_for('main.user', username=user.username,
#                       page=posts.prev_num) if posts.has_prev else None
#    return render_template('user.html', user=user, posts=posts.items,
#                           next_url=next_url, prev_url=prev_url)
#
#
#@bp.route('/edit_profile', methods=['GET', 'POST'])
#@login_required
#def edit_profile():
#    form = EditProfileForm(current_user.username)
#    if form.validate_on_submit():
#        current_user.username = form.username.data
#        current_user.about_me = form.about_me.data
#        db.session.commit()
#        flash(_('Your changes have been saved.'))
#        return redirect(url_for('main.edit_profile'))
#    elif request.method == 'GET':
#        form.username.data = current_user.username
#        form.about_me.data = current_user.about_me
#    return render_template('edit_profile.html', title=_('Edit Profile'),
#                           form=form)
#
#
#@bp.route('/follow/<username>')
#@login_required
#def follow(username):
#    user = User.query.filter_by(username=username).first()
#    if user is None:
#        flash(_('User %(username)s not found.', username=username))
#        return redirect(url_for('main.index'))
#    if user == current_user:
#        flash(_('You cannot follow yourself!'))
#        return redirect(url_for('main.user', username=username))
#    current_user.follow(user)
#    db.session.commit()
#    flash(_('You are following %(username)s!', username=username))
#    return redirect(url_for('main.user', username=username))
#
#
#@bp.route('/unfollow/<username>')
#@login_required
#def unfollow(username):
#    user = User.query.filter_by(username=username).first()
#    if user is None:
#        flash(_('User %(username)s not found.', username=username))
#        return redirect(url_for('main.index'))
#    if user == current_user:
#        flash(_('You cannot unfollow yourself!'))
#        return redirect(url_for('main.user', username=username))
#    current_user.unfollow(user)
#    db.session.commit()
#    flash(_('You are not following %(username)s.', username=username))
#    return redirect(url_for('main.user', username=username))
#
#
#@bp.route('/translate', methods=['POST'])
#@login_required
#def translate_text():
#    return jsonify({'text': translate(request.form['text'],
#                                      request.form['source_language'],
#                                      request.form['dest_language'])})
#
#
#@bp.route('/search')
#@login_required
#def search():
#    if not g.search_form.validate():
#        return redirect(url_for('main.explore'))
#    page = request.args.get('page', 1, type=int)
#    posts, total = Post.search(g.search_form.q.data, page,
#                               current_app.config['POSTS_PER_PAGE'])
#    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
#        if total > page * current_app.config['POSTS_PER_PAGE'] else None
#    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
#        if page > 1 else None
#    return render_template('search.html', title=_('Search'), posts=posts,
#                           next_url=next_url, prev_url=prev_url)
