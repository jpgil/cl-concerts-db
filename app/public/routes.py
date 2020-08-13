from app.public import bp
from flask import Flask, render_template, url_for, request, redirect, abort
from jinja2 import TemplateNotFound


# Make some objects available to templates.
@bp.context_processor
def inject_userquery():
    return dict(userquery=request.args.get('keywords', default=''))

# Defaults to Start Page
@bp.route('/')
def index():
    return redirect(url_for('.inicio'))

# Start Page
@bp.route('/inicio')
def inicio():
    return render_template('public/inicio.html')

# Search Result
@bp.route('/search')
def search():
    return render_template('public/search.html')

# Event Detail

# Plain pages
@bp.route('/<page>')
def show(page):
    try:
        return render_template('public/%s.html' % page)
    except TemplateNotFound:
        abort(404)
