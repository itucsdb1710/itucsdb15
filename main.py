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

@site.route('/restaurant/<rst_id>', methods=['GET', 'POST'])
def restaurant_page(rst_id):
    if request.method == 'POST':
        if request.form['action'] == 'send':
            comment = request.form['commentInput']
            username = current_user.userName
            if request.form['x'] == '1':
                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """INSERT INTO POST(USERNAME, COMMENT,RATE) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(username, comment,1))

                    query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and COMMENT = %s)"""
                    cursor.execute(query,(username, comment))

                    postid = cursor.fetchall()

                    query = """INSERT INTO POSTCAST(RSTID, POSTID) VALUES(%s, %s)"""
                    cursor.execute(query,(rst_id[0], postid[0][0]))
            elif request.form['x'] == '2':

                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """INSERT INTO POST(USERNAME, COMMENT,RATE) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(username, comment,2))

                    query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and COMMENT = %s)"""
                    cursor.execute(query,(username, comment))

                    postid = cursor.fetchall()

                    query = """INSERT INTO POSTCAST(RSTID, POSTID) VALUES(%s, %s)"""
                    cursor.execute(query,(rst_id[0], postid[0][0]))
            elif request.form['x'] == '3':

                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """INSERT INTO POST(USERNAME, COMMENT,RATE) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(username, comment,3))

                    query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and COMMENT = %s)"""
                    cursor.execute(query,(username, comment))

                    postid = cursor.fetchall()

                    query = """INSERT INTO POSTCAST(RSTID, POSTID) VALUES(%s, %s)"""
                    cursor.execute(query,(rst_id[0], postid[0][0]))
            elif request.form['x'] == '4':
                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """INSERT INTO POST(USERNAME, COMMENT,RATE) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(username, comment,4))

                    query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and COMMENT = %s)"""
                    cursor.execute(query,(username, comment))

                    postid = cursor.fetchall()

                    query = """INSERT INTO POSTCAST(RSTID, POSTID) VALUES(%s, %s)"""
                    cursor.execute(query,(rst_id[0], postid[0][0]))
            elif request.form['x'] == '5':
                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """INSERT INTO POST(USERNAME, COMMENT,RATE) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(username, comment,5))

                    query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and COMMENT = %s)"""
                    cursor.execute(query,(username, comment))

                    postid = cursor.fetchall()

                    query = """INSERT INTO POSTCAST(RSTID, POSTID) VALUES(%s, %s)"""
                    cursor.execute(query,(rst_id[0], postid[0][0]))
                    connection.commit()

            return redirect(url_for('site.restaurant_page', rst_id = rst_id))
        elif request.form['action'] == 'delete':
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM POSTCAST WHERE RSTID = %s"""
                cursor.execute(query, [rst_id[0]])

                query = """DELETE FROM RESTAURANT WHERE ID = %s"""
                cursor.execute(query, [rst_id[0]])

                connection.commit()
            return redirect(url_for('site.restaurant_page'))
        else:
            return render_template('restaurant_page.html', rst_id = rst_id)
    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT POSTID FROM POSTCAST WHERE RSTID = %s"""
            cursor.execute(query, rst_id[0])
            postids = cursor.fetchall()

            query = """SELECT * FROM RESTAURANT WHERE ID = %s"""
            cursor.execute(query, rst_id[0])

            names = cursor.fetchall()

            query = """SELECT * FROM RST_DETAILS WHERE ID = %s"""
            cursor.execute(query, rst_id[0])
            food = cursor.fetchall()
            posts = []
            for id in postids:
                query = """SELECT * FROM POST WHERE POSTID = %s"""
                cursor.execute(query, [id[0]])
                posts.append(cursor.fetchall())

            connection.commit()
        return render_template('restaurant_page.html', posts = posts, user = current_user, names = names,food=food)

@site.route('/edit_comment/<comment_id>', methods=['GET', 'POST'])
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

