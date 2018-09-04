from flask import Flask
from flask import jsonify, abort, Response
from flask_restful import request
from flask_restful import reqparse
import hvac
import os
import json
import csv

# "http://127.0.0.1:8200" for localhost test, "http://credstore:8200" for docker environment
#VAULT_URL = "http://credstore:8200" # If lack of http, it causes error: requests.exceptions.InvalidSchema: No connection adapters were found for 'credstore:8200/v1/sys/init'
VAULT_URL = "http://127.0.0.1:8200"

# http codes
# Success
HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400
#HTTP_CODE_UNAUTHORIZED = 401
HTTP_CODE_NOT_FOUND = 404
#HTTP_CODE_LOCKED = 423
# Server error
#HTTP_CODE_SERVER_ERR = 500

DEFAULT_SHARES = 1
DEFAULT_THRESHOLD = 1

VAULT_TOKEN_FILE = 'vaulttoken'
UNSEAL_KEYS_FILE = 'unsealkeys'

# import the resource of all messages
reader = csv.DictReader(open('resource.csv', 'r'))
msg_dict = {}
for row in reader:
	msg_dict[row['Code']] = row['Message']


def init_vault_api():
    """[summary]
    Initialize a vault in the Vault Server (Credential Store)
    [description]
    A number of keys will be generated from the master key, then the master key is thrown away (The Server will not store the key). The generated keys are kept by the Vault Client (Security Policy Manager)
    shares = The number of generated keys
    threshold = The minimum number of generated keys needed to unseal the vault
    """
    parser = reqparse.RequestParser()
    parser.add_argument('shares', type=int, help='Default: threshold=1, shares=1', default=DEFAULT_SHARES)
    parser.add_argument('threshold', type=int, help='Default: threshold=1, shares=1', default = DEFAULT_THRESHOLD)

    args = parser.parse_args()
    shares = args['shares']
    threshold = args['threshold']

    client = init_client()
    
    if(client.is_initialized()==False): # if vault is not initialized yet
        try:
            vault = client.initialize(shares,threshold)
            root_token = vault['root_token']
            unseal_keys = vault['keys']
            # write root token into file
            f = open(VAULT_TOKEN_FILE, 'w')
            f.write(root_token)
            f.close()

	        # write unseal_keys into file
            f = open(UNSEAL_KEYS_FILE,'w')
            for key in unseal_keys:
                f.write("%s\n" % key)
            f.close()
        except Exception as e:
            raise e
       
        data = {
			'code' : HTTP_CODE_CREATED,
			'user message'  : msg_dict['init_vault_success'],#'Initialize vault successfully',
			'developer message' : msg_dict['init_vault_success']
		}
    else: # if vault existed
        data = {
			'code' : HTTP_CODE_OK,
			'user message'  : msg_dict['vault_existed'],#Vault is existed
			'developer message' : msg_dict['vault_existed']
		}
    
    js = json.dumps(data)
    resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
    return resp
    

def read_token():
    """[summary]
    Read the token from file 'vaulttoken'
    [description]
    
    Returns:
      [type] string -- [description] the token
    """
    f = open(VAULT_TOKEN_FILE, 'r')
    root_token = f.read()
    f.close()
    return root_token

def read_unseal_keys():
    """[summary]
    Read keys used to unseal the vault from file 'unsealkeys'
    [description]
    
    Returns:
      [type] List -- [description] List of keys
    """
    f = open(UNSEAL_KEYS_FILE, 'r')
    unseal_keys = f.read().splitlines()
    f.close()
    return unseal_keys

def init_client():
    """[summary]
    Initialize the vault client
    [description]
    
    Returns:
      [type] -- [description]
    """
    client = hvac.Client(url=VAULT_URL)
    return client
    
def unseal_vault(client):
    """[summary]
    Unseal (open) the vault
    [description]
    This must be done prior to read contents from the vault.
    Arguments:
      vault client {[type]} -- [description] vault client
    """
    client.token = read_token()
    # unseal the vault
    unseal_keys = read_unseal_keys()
    client.unseal_multi(unseal_keys)

def seal_vault(client):
    """[summary]
    Seal the vault
    [description]
    This should be done to protect the vault while not using it
    Arguments:
      vault client {[type]} -- [description] vault client
    """
    client.seal()
    
def write_secret_api():
    """[summary]
    Write/ update a secret to the vault
    [description]
    Arguments:
        name -- name of secret
        value -- value of secret
    """
    parser = reqparse.RequestParser()
    parser.add_argument('name',  help='Name of sensitive information')
    parser.add_argument('value', help='Value of sensitive information')

    args = parser.parse_args()
    secret_name = args['name']
    secret_value = args['value']

    if(secret_name is None or secret_value  is None or secret_value=='' or  secret_name==''): # verify parameters
        data = {
			'code' : HTTP_CODE_BAD_REQUEST,
			'user message'  : msg_dict['bad_request_write_secret'],#'Bad request',
			'developer message' : msg_dict['bad_request_write_secret']
		}
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
        return resp
    
    client = init_client()
    unseal_vault(client)  
    client.write('secret/'+secret_name, secret_value=secret_value, lease='1h')
    seal_vault(client)

    data = {
        'code' : HTTP_CODE_CREATED,
        'user message'  : msg_dict['write_secret_success'],#'Add secret successfully',
        'developer message' : msg_dict['write_secret_success']
    }
    js = json.dumps(data)
    resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
    return resp

def read_secret_api():
    """[summary]
    Read a secret from the vault
    [description]
    
    Returns:
      [type] json -- [description] a dictionary of all relevant information of the secret
    """

    parser = reqparse.RequestParser()
    parser.add_argument('name',help='Name of sensitive information')

    args = parser.parse_args()
    secret_name = args['name']

    if(secret_name is None or  secret_name==''): # verify parameters
        data = {
			'code' : HTTP_CODE_BAD_REQUEST,
			'user message'  : msg_dict['bad_request_read_secret'],#'Add user successfully',
			'developer message' : msg_dict['bad_request_read_secret']
		}
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
        return resp
    # unseal the vault
    client = init_client()
    unseal_vault(client) 
    secret_values = client.read('secret/'+secret_name)
    seal_vault(client)
    
    if(secret_values is None): # If the required secret does not exist
        data = {
            'code' : HTTP_CODE_NOT_FOUND,
            'user message'  : msg_dict['secret_not_exist'],#'Secret does not exist',
            'developer message' : msg_dict['secret_not_exist']
        }
        js = json.dumps(data)
    else:
        data = {
            'code' : HTTP_CODE_OK,
            'user message'  : msg_dict['read_secret_success'],#'Read secret successfully',
            'developer message' : msg_dict['read_secret_success']
        }
        data.update(secret_values)
        js = json.dumps(data)

    resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
    return resp

def delete_secret_api():
    """[summary]
    Remove a secret from the vault
    [description]
    """

    parser = reqparse.RequestParser()
    parser.add_argument('name',help='Name of sensitive information')

    args = parser.parse_args()
    secret_name = args['name']

    if(secret_name is None or  secret_name==''): # verify parameters
        data = {
			'code' : HTTP_CODE_BAD_REQUEST,
			'user message'  : msg_dict['bad_request_delete_secret'],#'Lack of secret name',
			'developer message' : msg_dict['bad_request_delete_secret']
		}
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
        return resp
        
    # unseal the vault
    client = init_client()
    unseal_vault(client) 
    client.delete('secret/'+secret_name)
    seal_vault(client)

    data = {
        'code' : HTTP_CODE_OK,
        'user message'  : msg_dict['delete_secret_success'],#'Delete secret successfully',
        'developer message' : msg_dict['delete_secret_success']
    }
    js = json.dumps(data)
    resp = Response(js, status=HTTP_CODE_OK, mimetype='application/json')
    return resp
