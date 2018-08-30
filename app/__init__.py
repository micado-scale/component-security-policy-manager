<<<<<<< HEAD
"""[summary]
Init module
[description]
The init module creates Flask object, databases, and logging handler
"""
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
# create application object of class Flask

app = Flask(__name__)

from app import routes
from app import dksecrets
=======
"""[summary]
Init module
[description]
The init module creates Flask object, databases, and logging handler
"""
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
# create application object of class Flask

app = Flask(__name__)

from app import routes
from app import openidc
>>>>>>> 5644cb4b55e39da905113968aab56182547ff1a5
