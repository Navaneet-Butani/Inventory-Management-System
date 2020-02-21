import pymysql
import click
from flask import current_app, g
from flask.cli import with_appcontext
import json


def connect_db():
    return pymysql.connect(
        user='root',
        password='123',
        database='db_inventory',
        host='localhost'
    )


def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def retrieve_record(name=None, category=None):
    print("Inside name", name)
    print("Inside category", category)

    if name and category:
        sql = "SELECT * FROM records WHERE name = %s and category = %s ORDER BY id DESC;"
        cursor = get_db().cursor()
        print(name)
        print(category)
        cursor.execute(sql, (name, category))
    else:
        if name:
            sql = "SELECT * FROM records WHERE name = %s ORDER BY id DESC;"
            cursor = get_db().cursor()
            cursor.execute(sql, name)
        elif category:
            print("Called:", category)
            sql = "SELECT * FROM records WHERE category = %s ORDER BY id DESC;"
            cursor = get_db().cursor()
            cursor.execute(sql, category)
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row))
            for row in cursor.fetchall()]

    return data
