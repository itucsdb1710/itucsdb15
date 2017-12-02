from flask import Blueprint, render_template
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user
from flask import current_app, request
from jinja2 import TemplateNotFound
import psycopg2 as dbapi2
import flask

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for

site = Blueprint('site', __name__,template_folder='templates', static_folder='static')

@site.route('/mainpage/', methods=['GET', 'POST'])
@login_required
def main_page():

    return render_template('mainpage.html')


