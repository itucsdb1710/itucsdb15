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
    if request.method == 'POST':

        if request.form['action'] == 'add':
            newRst = request.form['newRst']
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO RESTAURANT(NAME, USERNAME) VALUES(%s, %s)"""
                cursor.execute(query,(newRst, username))
                connection.commit()
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO RST_DETAILS (NAME,LOCATION,CATEGORY)
                VALUES ('%s', '%s', '%s') """ %(newRst,'not provided yet.','not provided yet.')
                cursor.execute(query)
                connection.commit()


            return redirect(url_for('site.main_page'))
    if request.method == 'GET':
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()
        query = """SELECT * FROM RESTAURANT"""
        cursor.execute(query)
        names=cursor.fetchall()
        query = """SELECT * FROM USERS"""
        cursor.execute(query)
        users=cursor.fetchall()
        connection.commit()
        return render_template('mainpage.html',names=names,users=users,user=current_user)


