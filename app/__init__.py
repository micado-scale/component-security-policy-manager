'''[summary]
Init module
[description]
The init module creates Flask object and log handler
'''
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_restful import Api
from app.secrets import Secrets
from app.node_certs import NodeCerts
from app.node_crl import NodeCrl
from app.join_tokens import JoinTokens
from app.crypto_engine import CryptoEngine
from app.image_verify import ImageVerify


app = Flask(__name__)
api = Api(app)
api.add_resource(Secrets, '/v1.0/secrets', '/v1.0/secrets/<secret_name>')
api.add_resource(NodeCerts, '/v1.0/nodecerts', '/v1.0/nodecerts/<serial>')
api.add_resource(NodeCrl, '/v1.0/nodecrl')
api.add_resource(JoinTokens, '/v1.0/jointokens', '/v1.0/jointokens/<token>')
api.add_resource(CryptoEngine, '/v1.0/cryptoengine/<path:path>')
api.add_resource(ImageVerify, '/v1.0/imageverify')

logHandler = RotatingFileHandler('error.log', maxBytes=1000, backupCount=1)
logHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - '
    '%(levelname)s - %(message)s')
logHandler.setFormatter(formatter)

app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logHandler)
