
from app import app, dksecrets

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
# app.add_url_rule('/getuser','get_user', dbmodels.get_user,methods=['GET'])
# endpoint to create new user
app.add_url_rule('/v1.0/create_secret','create_secret_api', dksecrets.create_secret_api, methods=['POST'])
app.add_url_rule('/v1.0/add_secret','add_secret_api', dksecrets.add_secret_api, methods=['POST'])