from app.common.api_contract import *
from app.service.inventory import *
from flask import request, jsonify, Response
from flask_restful import Resource, marshal
from app import app, api, UPLOAD_IMAGE_PATH, logger
from app.db import *
from datetime import datetime
import os
import time

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_image_name(filename):
    time_str = time.strftime("%Y%m%d-%H%M%S")
    return 'inventory_image'+time_str+"."+filename.rsplit('.', 1)[1].lower()


@api.route('/inventory/insert')
class InsertInventoryRecords(Resource):
    def post(self):
        logger.info("INSERT API CALLED!")
        is_valid, request_data, file = get_insert_request_data(request)

        # Show error message for invalid request data with status code
        if not is_valid:
            logger.warning("INVALID REQUEST DATA FOUND!")
            error_msg = "Invalid request data found! Form data should contain: File(value = Uploaded Image), " \
                        "name(value = String), category(value = String), quantity(value = Integer)"
            return Response(error_msg, status=400)

        # Getting the request data
        image_name = get_image_name(file.filename)
        full_file_path = os.path.join(UPLOAD_IMAGE_PATH, image_name)

        # Serializing the request_data
        data = marshal(request_data, fields=insert_request_fields)

        # Inserting records into Database
        # Have considered manufacturing_time as current time and expiry_time = manufacturing_time + 30 Days
        sql = "INSERT INTO records (name, category, manufacturing_time, quantity, expiry_time, uploaded_image_name) " \
              "VALUES (%s, %s, NOW(), %s, NOW() + INTERVAL 30 DAY, %s);"
        cursor = get_db().cursor()
        cursor.execute(sql, (data['name'], data['category'], data['quantity'], image_name))
        get_db().commit()
        logger.info("INVENTORY RECORD IS INSERTED IN DATABASE")
        close_db()

        # Validate uploaded image type and Store valid image type in directory
        if file and allowed_file(file.filename):
            file.save(full_file_path)
            logger.info("INVENTORY IMAGE IS UPLOADED SUCCESSFULLY")
        return jsonify(success=True)


@api.route('/inventory/search')
class SearchInventoryRecords(Resource):
    def get(self):
        logger.info("INSERT API CALLED!")
        is_valid, name, category = get_search_request_data(request)

        # Show error message for invalid request data with status code
        if not is_valid:
            logger.warning("INVALID REQUEST DATA FOUND!")
            error_msg = "Invalid request data found! Search parameter should be like name(value = String), " \
                        "category(value = String)"
            return Response(error_msg, status=400)

        records = retrieve_record(name=name, category=category)
        response_data = []
        for record in records:
            # Serializing the data
            data = marshal(record, fields=get_request_fields)
            data['is_expired'] = datetime.now() > record['expiry_time']
            data['uploaded_image_path'] = os.path.join(UPLOAD_IMAGE_PATH, data['uploaded_image_name'])
            del data['uploaded_image_name']
            response_data.append(data)
        return jsonify(response_data)


@api.route('/inventory/update')
class UpdateInventoryRecords(Resource):
    def put(self):
        id = request.args.get('id')
        quantity = request.args.get('quantity')

        # Show error message for invalid request data with status code
        if not id or not quantity:
            logger.warning("INVALID REQUEST FOR UPDATE RECORDS!")
            error_msg = "Invalid request data found! Search parameter should be like id(value = Integer), " \
                        "quantity(value = Integer)"
            return Response(error_msg, status=400)
        else:
            records_exists, updated_rows_count = update_records(id, quantity)
            if updated_rows_count == 0:
                # If no records available for given id.
                if records_exists and not records_exists:
                    message = "No records available for id:{}".format(id)
                    return Response(message, status=400)
            message = "Row is updated for id:{}".format(id)
            return Response(message, status=200)


@api.route('/inventory/delete')
class DeleteInventoryRecords(Resource):
    def delete(self):
        id = request.args.get('id')
        name = request.args.get('name')
        category = request.args.get('category')

        # Show error message for invalid request data with status code
        if not id and not name and not category:
            logger.warning("INVALID REQUEST FOR DELETE RECORDS!")
            error_msg = "Invalid request data found! Parameter should be like id(value = Integer) " \
                        "or name(value = Integer) or category(value = Integer) or name(value = Integer), " \
                        "category(value = Integer)"
            return Response(error_msg, status=400)
        else:
            is_deleted, message = delete_records(id, name, category)
            if is_deleted:
                status_code = 200
            else:
                status_code = 400
            return Response(message, status=status_code)
