import json
import os
import psycopg2 as dbapi2
import re
import flask

from flask import Flask
from flask import redirect,render_template, flash
from flask.helpers import url_for
from flask import Blueprint, redirect, render_template, url_for
from flask import current_app, request
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user, logout_user
from passlib.apps import custom_app_context as pwd_context


def create_app():
    app = Flask(__name__)
    return app
app =create_app()


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@app.route('/home/', methods=['GET', 'POST'])
def home_page():

        return render_template('home.html',titles=titles)

@app.route('/', methods=['GET', 'POST'])
def main_page():

        return render_template('main.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin_page():

        return render_template('signin.html')


@app.route('/sign_up/', methods=['GET', 'POST'])
def signup_page():

        return render_template('sign_up.html')

@app.route("/logout/")
def logout_page():
    logout_user()
    return redirect(url_for('main_page'))

@app.route('/settings/', methods=['GET', 'POST'])
def settings_page():
    return render_template("settings.html")

@app.route('/profile/')
def profile_page():
    return render_template("profile.html")

@app.route('/edit_profile/', methods=['GET', 'POST'])
def edit_profile_page():
    return render_template("edit_profile.html")

@app.route('/search/')
def search_page():
    return render_template("search.html")

@app.route('/category/')
def category_page():
    return render_template("category.html")

@app.route('/nearby/')
def nearby_page():
    return render_template("nearby.html")

@app.route('/initdb')
def initialize_database():

    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS RESTAURANT CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POSTCAST CASCADE"""
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS RST_DETAILS CASCADE """
        cursor.execute(query)

        query = """CREATE TABLE USERS (
                    NAME VARCHAR(80) NOT NULL,
                    USERNAME VARCHAR(20) PRIMARY KEY,
                    MAIL VARCHAR(80) NOT NULL UNIQUE,
                    PASSWORD VARCHAR(120) NOT NULL)"""
        cursor.execute(query)

        password = "admin"
        hashed = pwd_context.encrypt(password)
        query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('admin', 'admin123', 'admin@itu.edu.tr', %s)"""
        cursor.execute(query, [hashed])

        query = """CREATE TABLE POST (
                    POSTID SERIAL PRIMARY KEY,
                    USERNAME VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    COMMENT VARCHAR(500) NOT NULL,
                    RATE VARCHAR(20) DEFAULT 1)"""
        cursor.execute(query)

        query= """CREATE TABLE RESTAURANT (
                    ID SERIAL PRIMARY KEY,
                    NAME VARCHAR(20) NOT NULL,
                    USERNAME VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    UNIQUE(NAME) )"""
        cursor.execute(query)

        query = """INSERT INTO RESTAURANT ( NAME, USERNAME ) VALUES ('Burger king', 'admin123')"""
        cursor.execute(query)

        query = """INSERT INTO RESTAURANT ( NAME, USERNAME ) VALUES ('Mado', 'admin123')"""
        cursor.execute(query)

        query= """CREATE TABLE POSTCAST (
                    ID SERIAL PRIMARY KEY,
                    RSTID INTEGER REFERENCES RESTAURANT(ID) ON DELETE CASCADE,
                    POSTID INTEGER REFERENCES POST(POSTID) ON DELETE CASCADE,
                    UNIQUE(RSTID, POSTID) )"""
        cursor.execute(query)

        query= """CREATE TABLE RST_DETAILS (
                    ID SERIAL REFERENCES RESTAURANT(ID) ON DELETE CASCADE,
                    NAME VARCHAR(20) REFERENCES RESTAURANT(NAME) ON DELETE CASCADE,
                    LOCATION VARCHAR(20) NULL,
                    CATEGORY VARCHAR(20) NULL,
                    PRIMARY KEY(ID) )"""
        cursor.execute(query)

        query = """INSERT INTO RST_DETAILS ( NAME, LOCATION,CATEGORY ) VALUES ('Burger king', 'levent','fast food')"""
        cursor.execute(query)
        query = """INSERT INTO RST_DETAILS ( NAME, LOCATION,CATEGORY ) VALUES ('Mado', 'taksim','turkish food')"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.secret_key = 'secret key'
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)