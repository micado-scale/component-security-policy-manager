from app import app, dksecrets
from app import vaultclient

'''def index():
	"""[summary]
	Hello world function
	[description]
	This function is only for testing if the web service is in operating
	"""
	return "Hello, World!"
   
app.add_url_rule('/v1.0/','index',index)'''

# Application sensitive information management
#app.add_url_rule('/v1.0/create_secret','create_secret_api', dksecrets.create_secret_api, methods=['POST'])
app.add_url_rule('/v1.0/appsecrets','add_docker_secret_api', dksecrets.add_secret_api, methods=['POST'])

# Infrastructure sensitive information management
app.add_url_rule('/v1.0/vault','initvault', vaultclient.init_vault_api, methods=['POST'])
app.add_url_rule('/v1.0/secrets','write_secret_api', vaultclient.write_secret_api, methods=['POST']) # Add or update a secret
app.add_url_rule('/v1.0/secrets','read_secret_api', vaultclient.read_secret_api, methods=['GET'])
app.add_url_rule('/v1.0/secrets','delete_secret_api', vaultclient.delete_secret_api, methods=['DELETE'])

