"""[summary]
Init module
[description]
The init module creates Flask object and log handler
"""
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

app = Flask(__name__)

from app import endpoints

logHandler = RotatingFileHandler('error.log', maxBytes=1000, backupCount=1)
logHandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - '
    '%(levelname)s - %(message)s')
logHandler.setFormatter(formatter)

app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logHandler)
