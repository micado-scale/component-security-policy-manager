from flask_restful import Api
from app import app, vault_client

api = Api(app)

# Vault initialization
api.add_resource(vault_client.Vaults, '/v1.0/vaults')

# Infrastructure secrets
api.add_resource(vault_client.Secrets, '/v1.0/secrets')
api.add_resource(vault_client.Secret, '/v1.0/secrets/<secret_name>')
