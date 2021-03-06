from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from app import db
from app.users import bp
from app.users.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm, EditProfileForm, EditUserForm
from app.models import User
from app.users.email import send_password_reset_email




@bp.route('/view/users')
@login_required
def view_users():
    elementsname='users'
    title=_('Usuarios')
    page = request.args.get('page', 1, type=int)
    elements = User.query.order_by(User.last_name.asc()).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('users.view_'+elementsname, title=title,page=elements.next_num) \
        if elements.has_next else None
    prev_url = url_for('users.view_'+elementsname, title=title, page=elements.prev_num) \
        if elements.has_prev else None
    return render_template('users/'+elementsname+'.html', title=title,
                           elements=elements.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index',user=current_user.last_name))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('e-mail o contraseña incorrecta'),'error')
            return redirect(url_for('users.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('users.login')
        return redirect(next_page)
    return render_template('users/login.html', title=_('Entre aquí'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index',user=''))


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.profile.name != 'Administrador':
        flash(_('Debe ser un Administrador para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name = form.last_name.data, email=form.email.data, profile = form.perfil.data )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Usuario {} agregado'.format(form.first_name.data+" "+form.last_name.data)),'info')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title=_('Register'),
                           form=form)

@bp.route('/edituser', methods=['GET', 'POST'])
@login_required
def EditUser():
    if current_user.profile.name != 'Administrador':
        pass

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # flash(
        # _('Revise su correo por instrucciones sobre como recuperar su contraseña'), 'info')

        flash(
            url_for('users.reset_password',
                    token=user.get_reset_password_token(),
                    _external=True), 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'),user='')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Su contraseña ha sido reseteada'),'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_password.html', form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('users.edit_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data =  current_user.email
    return render_template('users/editprofile.html', title=_('Editar Perfil'),
                           form=form)

@bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.profile.name != 'Administrador':
        flash(_('Debe ser un Administrador para entrar a esta página'),'error')
        return redirect(url_for('users.login'))
    user=User.query.filter_by(id=user_id).first_or_404()
    form = EditUserForm(original_email=user.email)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.profile = form.perfil.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash(_('Tus cambios han sido guardados.'),'info')
        return redirect(url_for('users.view_users'))
    elif request.method == 'GET':
        form.perfil.data =  user.profile
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data =  user.email
    return render_template('users/editprofile.html', title=_('Editar Usuario'),
                           form=form)