<<<<<<< HEAD
from app import app, dksecrets
from app import vaultclient
=======
from app import app, openidc
>>>>>>> 5644cb4b55e39da905113968aab56182547ff1a5

#@app.route('/')
#@app.route('/index')
def index():
	"""[summary]
	Hello world function
	[description]
	This function is only for testing if the web service is in operating
	"""
	return "Hello, World!"
   
app.add_url_rule('/v1.0/','index',index)

<<<<<<< HEAD
app.add_url_rule('/v1.0/create_secret','create_secret_api', dksecrets.create_secret_api, methods=['POST'])
app.add_url_rule('/v1.0/add_secret','add_secret_api', dksecrets.add_secret_api, methods=['POST'])


app.add_url_rule('/v1.0/vault','initvault', vaultclient.init_vault_api, methods=['POST'])
app.add_url_rule('/v1.0/secrets','write_secret_api', vaultclient.write_secret_api, methods=['POST'])
app.add_url_rule('/v1.0/secrets','read_secret_api', vaultclient.read_secret_api, methods=['GET'])
app.add_url_rule('/v1.0/secrets','delete_secret_api', vaultclient.delete_secret_api, methods=['PUT'])
=======
app.add_url_rule('/v1.0/userinfo','get_userinfo_api', openidc.get_userinfo_api, methods=['GET'])

app.add_url_rule('/v1.0/alltokens','get_tokens_api', openidc.get_tokens_api, methods=['GET'])

app.add_url_rule('/v1.0/tokens','logout_api', openidc.logout_api, methods=['DELETE'])
app.add_url_rule('/v1.0/tokens','refresh_token_api', openidc.refresh_token_api, methods=['PUT'])
app.add_url_rule('/v1.0/tokens','instropect_accesstoken_api', openidc.instropect_accesstoken_api, methods=['GET'])


app.add_url_rule('/v1.0/clients','set_client_api', openidc.set_client_api, methods=['PUT'])
>>>>>>> 5644cb4b55e39da905113968aab56182547ff1a5

