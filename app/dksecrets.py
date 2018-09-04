from app import app
from flask import Flask
from flask import jsonify, abort, Response
from flask_restful import reqparse, abort, Api, Resource
from flask_restful import request
import json
import os
import docker
import string

# the docker API create secret has error which is not resolved yet
def create_secret(secretname, secretvalue):
    '''[summary]
    
    [description]
    This function creates a docker secret
    Returns:
        [type] Integer -- [description] Id of the created secret
    
    Raises:
        e -- [description]
    '''
    #secret_name = request.values.get("name")
    #secret_value = request.values.get("value")

    client = docker.from_env()
    try:
        secretid = client.secrets.create(name=secretname,data = secretvalue.encode("utf-8"))
    except Exception as e:
        raise e

    '''data = {
        'code' : 200,        
        'secret name' : secret_name,
        'secret_value' : secret_value
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')

    return resp'''
    return secretid

def add_secret_api():
    '''[summary]
    
    [description]
    Creates a docker secret and distribute it to application services
    Returns:
        [type] Json object -- [description] Secret name and service name
    '''
    secret_name = request.values.get("secret")
    secret_value = request.values.get("value")
    service_name = request.values.get("service")

    client = docker.from_env()
    #secret_id = client.secrets.get(secret_name).id # Get the id of the secret
    secret_id = create_secret(secret_name, secret_value)
    secret = docker.types.SecretReference(secret_id = secret_id,secret_name=secret_name) # Create a SecretReference object
    client.services.get(service_name).update(secrets=[secret]) # Update the service by adding the secret

    data = {
        'code' : 200,        
        'secret name' : secret_name,
        'service name' : service_name
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')

    return resp