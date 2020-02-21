from werkzeug.utils import redirect, secure_filename
from app.common.api_contract import *
from app.service.inventory import *
from flask import request, jsonify, Response
from flask_restful import Resource, marshal, fields
from app import app, api, UPLOAD_IMAGE_PATH, logger
from app.db import *
from datetime import datetime
import os
import time
import json

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_image_name(filename):
    time_str = time.strftime("%Y%m%d-%H%M%S")
    print("'inventory_image'+timestr+filename.rsplit('.', 1)[1].lower():", 'inventory_image'+time_str+filename.rsplit('.', 1)[1].lower())
    return 'inventory_image'+time_str+"."+filename.rsplit('.', 1)[1].lower()


@api.route('/inventory/insert')
class InsertInventoryRecords(Resource):
    def post(self):
        logger.info("INSERT API CALLED!")
        is_valid, request_data, file = get_insert_request_data(request)
        image_name = get_image_name(file.filename)
        full_file_path = os.path.join(UPLOAD_IMAGE_PATH, image_name)

        # Show error message for invalid request data with status code
        if not is_valid:
            logger.warning("INVALID REQUEST DATA FOUND!")
            error_msg = "Invalid request data found! Form data should contain: File(value = Uploaded Image), " \
                        "name(value = String), category(value = String), quantity(value = Integer)"
            return Response(error_msg, status=400)

        # Serializing the request_data
        data = marshal(request_data, fields=insert_request_fields)
        sql = "INSERT INTO records (name, category, manufacturing_time, quantity, expiry_time, uploaded_image_name) " \
              "VALUES (%s, %s, NOW(), %s, NOW() + INTERVAL 30 DAY, %s);"
        cursor = get_db().cursor()
        cursor.execute(sql, (data['name'], data['category'], data['quantity'], image_name))
        get_db().commit()
        logger.info("INVENTORY RECORD IS INSERTED IN DATABASE")
        close_db()

        if file and allowed_file(file.filename):
            file.save(full_file_path)
            logger.info("INVENTORY IMAGE IS UPLOADED SUCCESSFULLY")
        return jsonify(success=True)


@api.route('/inventory/search')
class SearchInventoryRecords(Resource):
    def get(self):
        logger.info("INSERT API CALLED!")
        is_valid, name, category = get_search_request_data(request)

        if not is_valid:
            logger.warning("INVALID REQUEST DATA FOUND!")
            error_msg = "Invalid request data found! Search parameter should br like name(value = String), " \
                        "category(value = String)"
            return Response(error_msg, status=400)

        print("name:", name)
        print(category)
        records = retrieve_record(name=name, category=category)
        response_data = []
        print("records:", records)
        for record in records:
            data = marshal(record, fields=get_request_fields)
            data['is_expired'] = datetime.now() > record['expiry_time']
            data['uploaded_image_path'] = os.path.join(UPLOAD_IMAGE_PATH, data['uploaded_image_name'])
            del data['uploaded_image_name']
            response_data.append(data)
        print("response_data:", response_data)
        return jsonify(response_data)
