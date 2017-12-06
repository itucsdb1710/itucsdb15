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

from user import User
from main import *
from restaurant import *

lm = LoginManager()

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@lm.user_loader
def load_user(userName):
    return get_user(userName)

def get_user(user_id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM USERS WHERE USERNAME = %s"""
        cursor.execute(query, [user_id])
        x = cursor.fetchall()
        password = x[0][3]
        user = User(x[0][0], x[0][1], x[0][2], x[0][3]) if password else None
    return user

def create_app():
    app = Flask(__name__)
    app.register_blueprint(site)
    return app
app =create_app()
lm.init_app(app)
lm.login_view = 'signin_page'

@app.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT USERNAME FROM USERS WHERE MAIL = %s"""
            cursor.execute(query, [email])
            data = cursor.fetchall()
            connection.commit()

        user = get_user(data[0][0])
        if user is not None:
            if pwd_context.verify(password, user.password):
                login_user(user)
                next_page = request.args.get('next', url_for('site.main_page'))
                return redirect(next_page)
        next = request.args.get('next')
        return redirect(next or url_for('site.main_page'))
    else:
        return render_template('signin.html')

@app.route('/sign_up/', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        nameSurname=request.form['inputNameSurname']
        username=request.form['inputUsername']
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD)
            VALUES ('%s', '%s', '%s', '%s')""" %(nameSurname,username,email,hashed)
            cursor.execute(query)
            user = User(nameSurname, username,email,hashed)

            connection.commit()
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """INSERT INTO INFO (USERNAME, SURNAME, AGE, COUNTRY,CITY,GENDER)
             VALUES ('%s','%s', '%s', '%s', '%s', '%s')""" %(username,'........','........','........','........','........')
            cursor.execute(query)
            connection.commit()

            login_user(user)
        return redirect(url_for('site.main_page'))

    else:
        return render_template('signup.html')
    return render_template('signup.html')

@app.route("/logout/")
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT USERNAME FROM USERS WHERE MAIL = %s"""
            cursor.execute(query, [email])
            data = cursor.fetchall()
            connection.commit()

        user = get_user(data[0][0])
        if user is not None:
            if pwd_context.verify(password, user.password):
                login_user(user)
                next_page = request.args.get('next', url_for('site.main_page'))
                return redirect(next_page)
    else:
        return render_template('homepage.html')



@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if request.method == 'POST':
        if request.form['action'] == 'deleteUser':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM USERS WHERE ( USERNAME=%s )"""
                cursor.execute(query, ([current_user.userName]))

                connection.commit()
            logout_user()
            return redirect(url_for('home_page'))
        elif request.form['action'] == 'updateUser':

            email=request.form['inputEmail']
            password=request.form['inputPassword']
            hashed = pwd_context.encrypt(password)

            execute=[]

            query="""UPDATE USERS SET """


            if len(email)!=0:
                current_user.email=email
                execute+=[str(email)]
                query+="""MAIL=%s"""

            if len(password)!=0:
                current_user.password=hashed
                execute+=[str(hashed)]
                if  len(email)!=0:
                    query+=""", """
                query+="""PASSWORD=%s"""
            if  len(email)==0 and len(password)==0:
                return render_template('settings.html')
            username=current_user.userName

            query+=""" WHERE (USERNAME=%s)"""

            execute+=[username]

            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                cursor.execute(query, execute)

                connection.commit()
            return render_template('settings.html')
    else:
        return render_template('settings.html')


@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
        query = """SELECT * FROM USERS"""
        cursor.execute(query)
        info=cursor.fetchall()
        connection.commit()
        query = """SELECT * FROM INFO"""
        cursor.execute(query)
        details=cursor.fetchall()

        connection.commit()
        return render_template('profile.html',info=info,user=current_user,details=details)


@app.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile_page():
    if request.method == 'POST':
        if request.form['action'] == 'save':
            name=request.form['Name']

            if len(name)!=0:
                execute=[]
                query="""UPDATE USERS SET """
                current_user.name=name
                execute+=[str(name)]
                query+="""NAME=%s"""
            elif len(name)==0:
                execute=[]
                query="""UPDATE USERS SET """
                execute+=[str(current_user.name)]
                query+="""NAME=%s"""

            query+=""" WHERE (USERNAME=%s)"""
            username=current_user.userName
            execute+=[username]

            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                cursor.execute(query, execute)
                connection.commit()

            surname=request.form['Surname']
            age=request.form['Age']
            country=request.form['Country']
            city=request.form['City']
            gender=request.form['Gender']

            if len(surname)!=0 or len(age)!=0 or len(country)!=0 or len(city)!=0 or len(gender)!=0:
                execute=[]
                query="""UPDATE INFO SET """
                if len(surname)!=0:
                    execute+=[str(surname)]
                    query+="""SURNAME=%s"""
                if len(age)!=0:
                    execute+=[str(age)]
                    if len(surname)!=0:
                        query+=""", """
                    query+="""AGE=%s"""
                if len(country)!=0:
                    execute+=[str(country)]
                    if len(surname)!=0 or len(age)!=0:
                        query+=""", """
                    query+="""COUNTRY=%s"""
                if len(city)!=0:
                    execute+=[str(city)]
                    if len(surname)!=0 or len(age)!=0 or len(country)!=0:
                        query+=""", """
                    query+="""CITY=%s"""
                if len(gender)!=0:
                    execute+=[str(gender)]
                    if len(surname)!=0 or len(age)!=0 or len(country)!=0 or len(city)!=0:
                        query+=""", """
                    query+="""GENDER=%s"""

                query+=""" WHERE (USERNAME=%s)"""
                username=current_user.userName
                execute+=[username]

                with dbapi2.connect(app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    cursor.execute(query, execute)
                    connection.commit()


            return render_template('edit_profile.html')
    else:
        return render_template('edit_profile.html')


@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search_page():

    if request.method =='POST':
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'search':
                 branch_name = request.form['search-branch-name']
                 query = """SELECT * FROM RESTAURANT WHERE (NAME = %s) """
                 cursor.execute(query,[branch_name])
                 name = cursor.fetchall()
                 connection.commit()
                 return render_template('search.html', results=name)

    else:
        return render_template('search.html')


@app.route('/category/')
@login_required
def category_page():
    return render_template("category.html")

@app.route('/nearby/')
@login_required
def nearby_page():
    return render_template("nearby.html")

@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS INFO CASCADE """
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS RESTAURANT CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POSTCAST CASCADE"""
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS RST_DETAILS CASCADE """
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS MYFAVORITE CASCADE"""
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

        query = """CREATE TABLE INFO (
                    USERNAME VARCHAR (50) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    SURNAME VARCHAR(80) NULL,
                    AGE VARCHAR(20) NULL,
                    COUNTRY VARCHAR(100)NULL,
                    CITY VARCHAR(100) NULL,
                    GENDER VARCHAR(50) NULL,
                    PRIMARY KEY(USERNAME))"""
        cursor.execute(query)

        query = """INSERT INTO INFO (USERNAME, SURNAME,AGE,COUNTRY,CITY,GENDER) VALUES ('admin123','alrehaili','30','turkey','istanbul','female')"""
        cursor.execute(query)

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

        query = """INSERT INTO RST_DETAILS ( NAME, LOCATION,CATEGORY ) VALUES ('Burger king', 'Levent','Fast food')"""
        cursor.execute(query)
        query = """INSERT INTO RST_DETAILS ( NAME, LOCATION,CATEGORY ) VALUES ('Mado', 'Taksim','Turkish food')"""
        cursor.execute(query)

        query= """CREATE TABLE MYFAVORITE (
                    USERNAME VARCHAR(30) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    RESTAURANT VARCHAR(50) REFERENCES RESTAURANT(NAME) ON DELETE CASCADE,
                    RST_ID SERIAL REFERENCES RESTAURANT(ID) ON DELETE CASCADE,
                    PRIMARY KEY(USERNAME,RESTAURANT) )"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))

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