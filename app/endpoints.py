from flask_restful import Api
from app import app, docker_secrets, vault_client

api = Api(app)

# Application sensitive information management
api.add_resource(docker_secrets.Dksecrets, '/v1.0/appsecrets')
api.add_resource(docker_secrets.Dksecret, '/v1.0/appsecrets/<secret_name>')

# Infrastructure sensitive information management
api.add_resource(vault_client.Secrets, '/v1.0/secrets')
api.add_resource(vault_client.Secret, '/v1.0/secrets/<secret_name>')

api.add_resource(vault_client.Vaults, '/v1.0/vaults')
