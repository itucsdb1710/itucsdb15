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

@site.route('/edit_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    if request.method == 'POST':

        if request.form['action'] == 'delete':
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM POST WHERE (POSTID= %s)"""
                cursor.execute(query, [comment_id])
                connection.commit()
            return redirect(url_for('site.main_page'))

        else:
            return render_template('edit_comment.html')
    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM POST WHERE POSTID = %s"""

            cursor.execute(query, [comment_id])
            post = cursor.fetchall()

            connection.commit()
        return render_template('edit_comment.html', post = post)

@site.route('/restaurant/<rst_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant_page(rst_id):
    if request.method == 'POST':
        location = request.form['Location']
        food = request.form['Food']

        if len(location)!=0 or len(food)!=0 :
            execute=[]
            query="""UPDATE RST_DETAILS SET """
            if len(location)!=0:
                execute+=[str(location)]
                query+="""LOCATION=%s"""
            if len(food)!=0:
                execute+=[str(food)]
                if len(location)!=0:
                    query+=""", """
                query+="""CATEGORY=%s"""

            query+=""" WHERE (ID=%s)"""
            execute+=[rst_id[0]]

            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
               cursor = connection.cursor()
               cursor.execute(query, execute)
               connection.commit()
               return redirect(url_for('site.restaurant_page',rst_id=rst_id))
        else:
               return redirect(url_for('site.restaurant_page',rst_id=rst_id))
    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM RESTAURANT WHERE ID = %s"""
            cursor.execute(query, rst_id[0])
            names = cursor.fetchall()

            connection.commit()
        return render_template('edit_restaurant.html', user = current_user, names = names)
@site.route('/favorites/', methods=['GET', 'POST'])
@login_required
def favorites_page():
    if request.method == 'POST':
        if request.form['action'] == 'remove':
            restaurant = request.form['restaurant']
            username= current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM MYFAVORITE WHERE (USERNAME= %s and RESTAURANT = %s)"""

                cursor.execute(query,(username, restaurant))
                connection.commit()

            return redirect(url_for('site.favorites_page'))
    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM MYFAVORITE """
                cursor.execute(query)
                favs=cursor.fetchall()
                connection.commit()
        return render_template('favorite.html', favs = favs,user=current_user)

