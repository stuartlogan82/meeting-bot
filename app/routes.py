from flask import render_template, flash, redirect, url_for
from app import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Stuart'}
    return render_template('index.html', title='Home', user=user)
