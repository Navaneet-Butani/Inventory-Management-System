import pymysql
import click
from flask import current_app, g
from flask.cli import with_appcontext


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
