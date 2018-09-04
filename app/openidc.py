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


#SERVER_URL = "http://10.20.151.49:8180/auth/"
#CLIENT_ID = "appDM"
#REALM_NAME = "demo"
#CLIENT_SECRET = "d5e62000-4f60-40c3-8642-abfd0a9523e2"

SERVER_URL = "http://31.171.247.142:8080/auth/"
CLIENT_ID = "app02"
REALM_NAME = "app01"
CLIENT_SECRET = "581ff333-aba1-4f45-9f27-0a06704d099b" #app2
#CLIENT_SECRET = "e532ea62-2743-4cea-89b3-ffc58664f739" #APP1

#keycloak_openid = KeycloakOpenID(server_url=SERVER_URL,client_id=CLIENT_ID, realm_name=REALM_NAME, client_secret_key=CLIENT_SECRET,verify=True)
#token = keycloak_openid.token("user01","123")  


#def get_accesstoken_api():
#	return token['access_token']

#def get_refreshtoken():
#	return token['refresh_token']

def set_client_api():
	serverurl = request.values.get("server")
	realmname = request.values.get("realm")
	clientid = request.values.get("id")
 	clientsecret = request.values.get("secret")
	global keycloak_openid 
	keycloak_openid  = KeycloakOpenID(server_url=serverurl,client_id=clientid, realm_name=realmname, client_secret_key=clientsecret,verify=True)
	# not yet: check if client is valid or not
	data = {
			'code' : HTTP_CODE_OK,
			'user message'  : 'set client successfully',
			'developer message' : 'set client successfully'
	}   
	js = json.dumps(data)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	return resp

def get_tokens_api():
	username = request.values.get("username")
	password = request.values.get("password")
	try:
		token = keycloak_openid.token(username,password)
	except Exception as e:
		raise e
		data = {
			'code' : HTTP_CODE_UNAUTHORIZED,
			'user message'  : 'Invalid user credentials',
			'developer message' : 'Invalid user credentials'
		}   
		js = json.dumps(data)
		resp = Response(js, status=HTTP_CODE_UNAUTHORIZED, mimetype='application/json')
		return resp
		
	js = json.dumps(token)
	resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
	return resp
    
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

def set_admin():
	serverurl = request.values.get("server")
	adminname = request.values.get("name")
	adminpwd = request.values.get("password")
 	realmname = request.values.get("realm")
 	global keycloak_admin
	keycloak_admin = KeycloakAdmin(server_url=serverurl,
                               username=adminname,
                               password=adminpwd,
                               realm_name=realmname,
                               verify=True)
	
def create_user_api():
	email = request.values.get("email")
	username = request.values.get("username")
	password = request.values.get("password")
	firstname =request.values.get("firstname")
	lastname = request.values.get("lastname")
 	realmname = request.values.get("realm")
 	organization = request.values.get("org")
 	
	new_user = keycloak_admin.create_user({"email": email,
                    "username": username,
                    "enabled": True,
                    "firstName": firstname,
                    "lastName": lastname,
                    "credentials": [{"value": password,"type": "password",}],
                    "realmRoles": ["user_default", ],
                    "attributes": {"organization": organization}})
	data = {
			'code' : HTTP_CODE_OK,
			'user message'  : 'Created user successfully',
			'developer message' : 'Created user successfully'
	}   
	js = json.dumps(data)
	resp = Response(js, status=HTTP_CODE_BAD_OK, mimetype='application/json')
	return resp  

def retrieve_all_users_api():
	users = keycloak_admin.get_users({})
	js = json.dumps(users)
	resp = Response(js, status=HTTP_CODE_BAD_OK, mimetype='application/json')
	return resp  


def retrieve_user_by_mail_api():
	email = request.values.get("email")
	user-id-keycloak = keycloak_admin.get_user_id(email)
	user = keycloak_admin.get_user(user-id-keycloak)
	
	js = json.dumps(user)
	resp = Response(js, status=HTTP_CODE_BAD_OK, mimetype='application/json')
	return resp
	
def update_user_by_mail_api():
	email = request.values.get("email")
	payload_json = request.json
	user-id-keycloak = keycloak_admin.get_user_id(email)
	keycloak_admin.update_user(user_id=user-id-keycloak,
                                      payload=payload_json)
	data = {
			'code' : HTTP_CODE_OK,
			'user message'  : 'Update user successfully',
			'developer message' : 'Update user successfully'
	}   
	js = json.dumps(data)
	resp = Response(js, status=HTTP_CODE_BAD_OK, mimetype='application/json')
	return resp


def change_user_password_by_mail_api():
	email = request.values.get("email")
	user-id-keycloak = keycloak_admin.get_user_id(email)
	
	newpwd = request.values.get("newpwd")
	response = keycloak_admin.set_user_password(user_id=user-id-keycloak, password=newpwd, temporary=True)
  
def delete_user_api():
	email = request.values.get("email")
	user-id-keycloak = keycloak_admin.get_user_id(email)
	response = keycloak_admin.delete_user(user_id=user-id-keycloak)

#validate user
#user management
#dynamic registration
#roles management
