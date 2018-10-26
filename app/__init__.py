"""[summary]
Init module
[description]
The init module creates Flask object, databases, and logging handler
"""
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

# create application object of class Flask
app = Flask(__name__)

from app import endpoints

# initialize the log handler: The handler used is RotatingFileHandler which
# rotates the log file when the size of the file exceeds a certain limit.
logHandler = RotatingFileHandler('error.log', maxBytes=1000, backupCount=1)
# set the log handler level
logHandler.setLevel(logging.INFO)
# create formatter and add it to the handlers: date time - name of package -
# file name (module name) - function name - line number -
# level (error, infor,...) - message
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - '
    '%(levelname)s - %(message)s')
logHandler.setFormatter(formatter)

# set the app logger level:  ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logHandler)
