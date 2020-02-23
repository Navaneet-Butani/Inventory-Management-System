from flask import Flask
from flask_restful import Api
import types
from app.common.decorator import *
import os
import logging

app = Flask(__name__)
api = Api(app)
api.route = types.MethodType(api_route, api)

# UPLOAD_IMAGE_PATH = os.path.join(app.root_path, 'upload/inventory')
UPLOAD_IMAGE_PATH = os.path.join(app.root_path, 'upload\inventory')
LOGGING_PATH = os.path.join(app.root_path)

log_file_name = os.path.join(LOGGING_PATH, 'app_log.log')
if not os.path.exists(log_file_name):
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
logging.basicConfig(filename=log_file_name, format='%(asctime)s - %(name)s:%(levelname)s - %(message)s', filemode="a")
logger = logging.getLogger()

from app.resource import *

if __name__ == '__main__':
    app.run(debug=True)
