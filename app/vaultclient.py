from flask import Flask
from flask import jsonify, abort, Response
from flask_restful import request
import hvac
import os
import json

VAULT_URL = "http://127.0.0.1:8200"


# 1. Initialize vault client linking to vault server by ip
def init_vault_api():
    """[summary]
    Initialize a vault in the Vault Server (Credential Store)
    [description]
    A number of keys will be generated from the master key, then the master key is thrown away (The Server will not store the key). The generated keys are kept by the Client (Security Policy Manager)
    shares = The number of generated keys
    threshold = The minimum number of generated keys needed to unseal the vault
    """

    shares = int(request.values.get("shares"))
    threshold = int(request.values.get("threshold"))
   
    client = init_client()
    
    if(client.is_initialized()==False):
       vault = client.initialize(shares,threshold)
       root_token = vault['root_token']
       unseal_keys = vault['keys']
       # write root token into file
       f = open('vaultoken', 'w')
       f.write(root_token)
       f.close()

	   # write unseal_keys into file
       f = open('unsealkeys','w')
       for key in unseal_keys:
           f.write("%s\n" % key)
       f.close()
       return "Initialized vault successfully!"
    else:
       return "Vault is alread initialized!"
       
    

    
def read_token():
    """[summary]
    Read the token from file
    [description]
    
    Returns:
      [type] string -- [description] the token
    """
    f = open('vaultoken', 'r')
    root_token = f.read()
    f.close()
    return root_token

def read_unseal_keys():
    """[summary]
    Read keys used to unseal the fault from file
    [description]
    
    Returns:
      [type] List -- [description] List of keys
    """
    f = open('unsealkeys', 'r')
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
      client {[type]} -- [description]
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
      client {[type]} -- [description]
    """
    client.seal()
    
def write_secret_api():
    """[summary]
    Write a secret to the vault
    [description]
    name = name of secret
    value = value of secret
    """
    secret_name = request.values.get("name").encode('ascii','ignore')
    secret_value = request.values.get("value")
    client = init_client()
    unseal_vault(client)  
    client.write('secret/'+secret_name, secret_value=secret_value, lease='1h')
    seal_vault(client)
    return "Added secret successfully"

def read_secret_api():
    """[summary]
    Read a secret from the vault
    [description]
    
    Returns:
      [type] json -- [description] a dictionary of all relevant information of the secret
    """
    secret_name = request.values.get("name").encode('ascii','ignore')
    # unseal the vault
    client = init_client()
    unseal_vault(client) 
    secret_values = client.read('secret/'+secret_name)
    seal_vault(client)
    return json.dumps(secret_values)

def delete_secret_api():
    """[summary]
    Remove a secret from the vault
    [description]
    """
    secret_name = request.values.get("name").encode('ascii','ignore')
    # unseal the vault
    client = init_client()
    unseal_vault(client) 
    secret_values = client.delete('secret/'+secret_name)
    seal_vault(client)
    return "Deleted the secret successfully!"
