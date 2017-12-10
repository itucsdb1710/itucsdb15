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
from main import site

@site.route('/restaurant/<rst_id>', methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('site.main_page'))
        elif request.form['action'] == 'favorite':
            try:
                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """SELECT NAME FROM RESTAURANT WHERE (ID = %s)"""
                    cursor.execute(query,rst_id[0])
                    name = cursor.fetchall()

                    query = """INSERT INTO MYFAVORITE(USERNAME, RESTAURANT,RST_ID) VALUES(%s, %s,%s)"""
                    cursor.execute(query,(current_user.userName,name[0],rst_id[0]))

                    connection.commit()
                return redirect(url_for('site.restaurant_page', rst_id = rst_id))
            except Exception as e:
                return redirect(url_for('site.restaurant_page', rst_id = rst_id))
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