#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 06:43:11 2019

@author: elisabettadinitto
"""

from flask import (
    Flask, render_template, request, redirect, flash, url_for, session, g
)

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from psycopg2 import (
        connect
)


# Create the application instance
app = Flask(__name__, template_folder="templates")
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else :
            myFile = open('dbConfig.txt')
            connStr = myFile.readline()
            conn = connect(connStr)
            cur = conn.cursor()
            cur.execute(
            'SELECT user_id FROM blog_user WHERE user_name = %s', (username,))
            if cur.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                cur.close()
                conn.close()

        if error is None:
            cur.execute(
                'INSERT INTO blog_user (user_name, user_password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

        flash(error)

    return render_template('auth/register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        conn = connect(connStr)
        cur = conn.cursor()
        error = None
        cur.execute(
            'SELECT * FROM blog_user WHERE user_name = %s', (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#@app.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        conn = connect(connStr)
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM blog_user WHERE user_id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
    if g.user is None:
        return False
    else: 
        return True


# Create a URL route in our application for "/"
@app.route('/')
@app.route('/index')
def index():
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
    cur = conn.cursor()
    cur.execute(
            """SELECT blog_user.user_name, post.post_id, post.created, post.title, post.body 
               FROM blog_user, post WHERE  
                    blog_user.user_id = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    load_logged_in_user()

    return render_template('blog/index.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if load_logged_in_user():
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('index'))
            else : 
                    myFile = open('dbConfig.txt')
                    connStr = myFile.readline()
                    conn = connect(connStr)
                    cur = conn.cursor()
                    cur.execute('INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)', 
                               (title, body, g.user[0])
                               )
                    cur.close()
                    conn.commit()
                    conn.close()
                    return redirect(url_for('index'))
        else :
            return render_template('blog/create.html')
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))
   
def get_post(id):
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
    cur = conn.cursor()
    cur.execute(
        """SELECT *
           FROM post
           WHERE post.post_id = %s""",
        (id,)
    )
    post = cur.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if post[1] != g.user[0]:
        abort(403)

    return post

@app.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    if load_logged_in_user():
        post = get_post(id)
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('index'))
            else : 
                myFile = open('dbConfig.txt')
                connStr = myFile.readline()
                conn = connect(connStr)
                cur = conn.cursor()
                cur.execute('UPDATE post SET title = %s, body = %s'
                               'WHERE post_id = %s', 
                               (title, body, id)
                               )
                cur.close()
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
        else :
            return render_template('blog/update.html', post=post)
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
                
    cur = conn.cursor()
    cur.execute('DELETE FROM post WHERE post_id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))                               

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)