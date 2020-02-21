from flask_restful import fields

inventory_fields = {
    "name": fields.String,
    "category": fields.String,
    "quantity": fields.Integer
}