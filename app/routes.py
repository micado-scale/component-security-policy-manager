from app import app, dksecrets, vaultclient
from flask_restful import Api

api = Api(app)

# Application sensitive information management
api.add_resource(dksecrets.Dksecrets, '/v1.0/appsecrets')
api.add_resource(dksecrets.Dksecret, '/v1.0/appsecrets/<secret_name>')

# Infrastructure sensitive information management
api.add_resource(vaultclient.Secret, '/v1.0/secrets/<secret_name>')
api.add_resource(vaultclient.Secrets, '/v1.0/secrets')

api.add_resource(vaultclient.Vaults, '/v1.0/vaults')
