from flask_restful import fields

insert_request_fields = {
    "name": fields.String,
    "category": fields.String,
    "quantity": fields.Integer
}

get_request_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "category": fields.String,
    "quantity": fields.Integer,
    "manufacturing_time": fields.DateTime,
    "expiry_time": fields.DateTime,
    "uploaded_image_name": fields.String
}