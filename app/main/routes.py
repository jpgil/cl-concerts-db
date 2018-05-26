from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from guess_language import guess_language
from app import db
#from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.main.forms import EditSimpleElementForm
from app.models import User, Profile, History, Event, Country, City, InstrumentType
#from app.translate import translate
from app.main import bp


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
    next_url = url_for('main.view_'+elementsname, page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('main.view_'+elementsname, page=elements.prev_num) \
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
    return view_elements(InstrumentType,'instrumenttypes',_('Tipos de Instrumentos'))

#@bp.route('/list/countries')
#def getCountryList():
#    page = request.args.get('page', 1, type=int)
#    q=request.args.get('q', '', type=str)
#    countries=db.session.query(Country).filter(Country.name.ilike(q+'%')).order_by(Country.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
#    data={ "results": [], "pagination": { "more": countries.has_next} }
#    for country in countries.items:
#        data["results"].append( { 'id' : country.id , 'text': country.name} )
#    return jsonify(data)

def getItemList(dbmodel,q,page):    
    itemslist=db.session.query(dbmodel).filter(dbmodel.name.ilike(q+'%')).order_by(dbmodel.name.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    data={ "results": [], "pagination": { "more": itemslist.has_next} }
    for item in itemslist.items:
        data["results"].append( { 'id' : item.id , 'text': item.name} )
    return jsonify(data)

@bp.route('/list/countries')
def getCountryList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(Country,q,page)

@bp.route('/list/cities')
def getCityList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(City,q,page)

@bp.route('/list/instrumenttype')
def getInstrumentTypeList():
    page = request.args.get('page', 1, type=int)
    q=request.args.get('q', '', type=str)
    return getItemList(InstrumentType,q,page)

@bp.route('/show/countries')
def testCountries():
    return render_template('main/testdropdown.html')



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
    elif request.method == 'GET':
        form.name.data = original_name
    return render_template('main/edit_simple_element.html',title=title,form=form)


@bp.route('/edit/country/<country>',methods = ['GET','POST'])
@login_required
def EditCountry(country):
    return EditSimpleElement(Country,_('País'),country)
 
@bp.route('/edit/city/<city>',methods = ['GET','POST'])
@login_required
def EditCity(city):
    return EditSimpleElement(City,_('Ciudad'),city)

@bp.route('/edit/instrumenttype/<instrumenttype>',methods = ['GET','POST'])
@login_required
def EditInstrumentType(instrumenttype):
    return EditSimpleElement(InstrumentType,_('Tipo de Instrumento'),instrumenttype) 



      
#            db.session.add(dbmodel(name=form.name.data))    
#    
#@bp.route('/new/country', methods = ['GET','POST'])
#@login_required
#def NewCountry():
#    return_value = EditElement(dbmodel=Country,title='País',original_name=None,is_new=True)
#    flash(_('Tus cambios han sido guardados.'))
#    return render_template(url_for('main.countries'))




@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
  return redirect(url_for('users.edit_profile'))
#    form = PostForm()
#    if form.validate_on_submit():
#        language = guess_language(form.post.data)
#        if language == 'UNKNOWN' or len(language) > 5:
#            language = ''
#        post = Post(body=form.post.data, author=current_user,
#                    language=language)
#        db.session.add(post)
#        db.session.commit()
#        flash(_('Your post is now live!'))
#        return redirect(url_for('main.index'))
#    page = request.args.get('page', 1, type=int)
#    posts = current_user.followed_posts().paginate(
#        page, current_app.config['POSTS_PER_PAGE'], False)
#    next_url = url_for('main.explore', page=posts.next_num) \
#        if posts.has_next else None
#    prev_url = url_for('main.explore', page=posts.prev_num) \
#        if posts.has_prev else None
#    return render_template('index.html', title=_('Home'), form=form,
#                           posts=posts.items, next_url=next_url,
#                           prev_url=prev_url)

#@bp.route('/view/country/<country>', methods=['GET'])
#@login_required
#def view_country(country_name):
#    country = Country.query.filter_by(name=country_name).first_or_404()
#    



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
