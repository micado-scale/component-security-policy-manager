from app import app, openidc

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

app.add_url_rule('/v1.0/userinfo','get_userinfo_api', openidc.get_userinfo_api, methods=['GET'])

#app.add_url_rule('/v1.0/access_token','get_accesstoken_api', openidc.get_accesstoken_api, methods=['GET'])

app.add_url_rule('/v1.0/tokens','logout_api', openidc.logout_api, methods=['DELETE'])
app.add_url_rule('/v1.0/tokens','refresh_token_api', openidc.refresh_token_api, methods=['PUT'])
app.add_url_rule('/v1.0/tokens','instropect_accesstoken_api', openidc.instropect_accesstoken_api, methods=['GET'])


