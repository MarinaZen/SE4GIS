#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 23:54:08 2019

@author: elisabettadinitto
"""

from psycopg2 import (
        connect
)

cleanup = (
        'DROP TABLE IF EXISTS blog_user CASCADE',
        'DROP TABLE IF EXISTS post'
        )

commands = (
        """
        CREATE TABLE blog_user (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) UNIQUE NOT NULL,
            user_password VARCHAR(255) NOT NULL
        )
        """,
        """ 
        CREATE TABLE post (
                post_id SERIAL PRIMARY KEY,
                author_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                title VARCHAR(350) NOT NULL,
                body VARCHAR(500) NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES blog_user (user_id)
        )
        """)

sqlCommands = (
        'INSERT INTO blog_user (user_name, user_password) VALUES (%s, %s) RETURNING user_id',
        'INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)'
        )        
conn = connect("dbname=elisabettadinitto user=elisabettadinitto password=eli")
cur = conn.cursor()
for command in cleanup :
    cur.execute(command)
for command in commands :
    cur.execute(command)
    print('execute command')
cur.execute(sqlCommands[0], ('Giuseppe', '3ety3e7'))
userId = cur.fetchone()[0]
cur.execute(sqlCommands[1], ('My First Post', 'This is the post body', userId))
cur.execute('SELECT * FROM post')
print(cur.fetchall())

cur.close()
conn.commit()
conn.close()
