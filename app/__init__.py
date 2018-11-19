"""[summary]
Init module
[description]
The init module creates Flask object and log handler
"""
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_restful import Api


app = Flask(__name__)

# FIXME circular reference
from app import vault_client

api = Api(app)
# FIXME test methods
api.add_resource(vault_client.Secrets, '/v1.0/secrets', '/v1.0/secrets/<secret_name>')

logHandler = RotatingFileHandler('error.log', maxBytes=1000, backupCount=1)
logHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - '
    '%(levelname)s - %(message)s')
logHandler.setFormatter(formatter)

app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logHandler)
