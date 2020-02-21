from app.common.api_contract import *
from flask import request, jsonify
from flask_restful import Resource, marshal, fields
from app import app, api
from app.db import *


@api.route('/insert')
class InsertInventoryRecords(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        # data = (marshal(json_data, fields=inventory_fields))
        cursor = get_db().cursor()
        sql = "INSERT INTO records (name, category, manufacturing_time, quantity, expiry_time) VALUES (%s, %s, NOW(), %s, NOW() + INTERVAL 30 DAY);"
        cursor.execute(sql, (json_data['name'], json_data['category'], json_data['quantity']))
        get_db().commit()
        close_db()
        return jsonify(success=True)
