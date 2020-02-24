import pymysql
import click
from app import logger, UPLOAD_IMAGE_PATH
from flask import current_app, g
from flask.cli import with_appcontext
import os


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
    # If name and category both exist in request
    if name and category:
        sql = "SELECT * FROM records WHERE name = %s and category = %s ORDER BY id DESC;"
        cursor = get_db().cursor()
        cursor.execute(sql, (name, category))
    else:
        # If only name is available in request
        if name:
            sql = "SELECT * FROM records WHERE name = %s ORDER BY id DESC;"
            cursor = get_db().cursor()
            cursor.execute(sql, name)

        # If only category is available in request
        elif category:
            sql = "SELECT * FROM records WHERE category = %s ORDER BY id DESC;"
            cursor = get_db().cursor()
            cursor.execute(sql, category)

    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    return data


def update_records(id, quantity):
    cursor = get_db().cursor()
    status, image_path = get_record_exist_with_given_id(id, cursor)
    # Update records if it exists
    if status:
        sql = "UPDATE records SET quantity=%s WHERE id=%s;"
        cursor.execute(sql, (quantity, id))
        get_db().commit()
        logger.info("INVENTORY RECORDS ARE UPDATED IN DATABASE.")
        close_db()
    close_db()
    return status, cursor.rowcount


def delete_records(id, name, category):
    cursor = get_db().cursor()
    # Delete By id
    if id:
        status, image_path_list = get_record_exist_with_given_id(id, cursor)
        # Delete record if it exists
        if status:
            sql = "DELETE FROM records WHERE id=%s;"
            cursor.execute(sql, id)
            get_db().commit()
            delete_image_for_given_list_of_path(image_path_list)
            logger.info("INVENTORY RECORDS ARE DELETED IN DATABASE AS PER GIVEN REQUEST.")
            close_db()
            message = "Record is deleted for id:{}.".format(id)
            return True, message
        else:
            return False, "No records found for given id to delete!"

    # Delete records by Name and Category
    elif name and category:
        status, image_path_list = get_records_exist_with_given_name_and_category(name, category, cursor)
        if status:
            sql = "DELETE FROM records WHERE name=%s and category=%s;"
            cursor.execute(sql, (name, category))
            get_db().commit()
            delete_image_for_given_list_of_path(image_path_list)
            logger.info("INVENTORY RECORDS ARE DELETED IN DATABASE AS PER GIVEN REQUEST.")
            close_db()
            message = "Records are deleted for name:{} and category:{}.".format(name, category)
            return True, message
        else:
            return False, "No records found for given name and category to delete!"

    # Delete record by Name or Category
    else:
        # Delete record by Name
        if name:
            status, image_path_list = get_records_exist_with_given_name(name, cursor)
            if status:
                sql = "DELETE FROM records WHERE name=%s;"
                cursor.execute(sql, name)
                get_db().commit()
                delete_image_for_given_list_of_path(image_path_list)
                logger.info("INVENTORY RECORDS ARE DELETED IN DATABASE AS PER GIVEN REQUEST.")
                close_db()
                message = "Records are deleted for name:{}.".format(name)
                return True, message
            else:
                return False, "No records found for given name to delete!"
        # Delete record by Category
        elif category:
            status, image_path_list = get_records_exist_with_given_category(category, cursor)
            if status:
                sql = "DELETE FROM records WHERE category=%s;"
                cursor.execute(sql, category)
                get_db().commit()
                delete_image_for_given_list_of_path(image_path_list)
                logger.info("INVENTORY RECORDS ARE DELETED IN DATABASE AS PER GIVEN REQUEST.")
                close_db()
                message = "Records are deleted for category:{}.".format(category)
                return True, message
            else:
                return False, "No records found for given name to delete!"


def get_record_exist_with_given_id(id, cursor):
    sql = "SELECT * FROM records where id=%s;"
    cursor.execute(sql, id)
    records = cursor.fetchall()
    if records:
        image_path_list = [record[6] for record in records]
        return True, image_path_list
    else:
        logger.info("NO RECORDS FOUND FOR GIVEN 'id'!")
        return False, None


def get_records_exist_with_given_name_and_category(name, category, cursor):
    sql = "SELECT * FROM records where name=%s AND category=%s;"
    cursor.execute(sql, (name, category))
    records = cursor.fetchall()
    if records:
        image_path_list = [record[6] for record in records]
        return True, image_path_list
    else:
        logger.info("NO RECORDS FOUND FOR GIVEN 'name' and 'category'!")
        return False, None


def get_records_exist_with_given_name(name, cursor):
    sql = "SELECT * FROM records where name=%s;"
    cursor.execute(sql, name)
    records = cursor.fetchall()
    if records:
        image_path_list = [record[6] for record in records]
        return True, image_path_list
    else:
        logger.info("NO RECORDS FOUND FOR GIVEN 'name'!")
        return False, None


def get_records_exist_with_given_category(category, cursor):
    sql = "SELECT * FROM records where category=%s;"
    cursor.execute(sql, category)
    records = cursor.fetchall()
    if records:
        image_path_list = [record[6] for record in records]
        return True, image_path_list
    else:
        logger.info("NO RECORDS FOUND FOR GIVEN 'category'!")
        return False, None


def delete_image_for_given_list_of_path(path_list):
    for path in path_list:
        if os.path.exists(os.path.join(UPLOAD_IMAGE_PATH, path)):
            os.remove(os.path.join(UPLOAD_IMAGE_PATH, path))
