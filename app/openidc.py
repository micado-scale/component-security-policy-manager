from flask import Flask
from flask import jsonify, abort, Response
from flask_restful import request
from keycloak import KeycloakOpenID
import os
import json
import csv

# http codes
# Success
HTTP_CODE_OK = 200
# HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400
HTTP_CODE_UNAUTHORIZED = 401
HTTP_CODE_NOT_FOUND = 404
#HTTP_CODE_LOCKED = 423
# Server error
HTTP_CODE_SERVER_ERR = 500

# import the resource of all messages
'''reader = csv.DictReader(open('resource.csv', 'r'))
msg_dict = {}
for row in reader:
	msg_dict[row['Code']] = row['Message']'''


SERVER_URL = "http://10.20.151.49:8180/auth/"
CLIENT_ID = "appDM"
REALM_NAME = "Demo"
CLIENT_SECRET = "d5e62000-4f60-40c3-8642-abfd0a9523e2"

keycloak_openid = KeycloakOpenID(server_url=SERVER_URL,client_id=CLIENT_ID, realm_name=REALM_NAME, client_secret_key=CLIENT_SECRET,verify=True)
#token = keycloak_openid.token("user01","123")  


#def get_accesstoken_api():
#	return token['access_token']

#def get_refreshtoken():
#	return token['refresh_token']
    
def get_userinfo_api():
	access_token = request.values.get("token")
	try:
		userinfo = keycloak_openid.userinfo(access_token)
	except:
		data = {
			'code' : HTTP_CODE_UNAUTHORIZED,
			'user message'  : 'Authentication error: Invalid token',
			'developer message' : 'Authentication error: Invalid token'
		}   
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_UNAUTHORIZED, mimetype='application/json')
		return resp

		
	js = json.dumps(userinfo)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	return resp

def logout_api():
	# refresh_token = get_refreshtoken()
	refresh_token = request.values.get("token")
	keycloak_openid.logout(refresh_token)
		
	data = {
			'code' : HTTP_CODE_OK,
			'user message'  : 'User is logged out',
			'developer message' : 'User is logged out'
	}   
	js = json.dumps(data)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	return resp

# retrieve the active state of a token
def refresh_token_api():
	refresh_token = request.values.get("token")
	try:
		new_token = keycloak_openid.refresh_token(refresh_token)
	except:
		data = {
			'code' : HTTP_CODE_UNAUTHORIZED,
			'user message'  : 'Session is not active',
			'developer message' : 'Session is not active'
		}   
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_UNAUTHORIZED, mimetype='application/json')
		return resp 
			
	js = json.dumps(new_token)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	global token
	token = new_token
	return resp

def instropect_accesstoken_api():
	access_token = request.values.get("token")
	try:
		token_info = keycloak_openid.introspect(access_token)
	except Exception as e:
		data = {
			'code' : HTTP_CODE_BAD_REQUEST,
			'user message'  : 'Invalid token',
			'developer message' : 'Invalid token'
		}   
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
		return resp 
		
	js = json.dumps(token_info)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	return resp

#validate user
#user management
#dynamic registration
#roles management
