from flask import Flask
from flask_restful import Api
import types
from app.common.decorator import *
import os

app = Flask(__name__)
api = Api(app)
api.route = types.MethodType(api_route, api)

upload_image_path = os.path.join(app.instance_path, 'upload/inventory')

from app.resource import *

if __name__ == '__main__':
    app.run(debug=True)
