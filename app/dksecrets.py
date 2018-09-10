from app import app
from flask import Flask
from flask import jsonify, abort, Response
from flask_restful import reqparse, abort, Api, Resource
from flask_restful import request
import json
import os
import docker
import string
import csv

# import the resource of all messages
reader = csv.DictReader(open('resource_dksecret.csv', 'r'))
msg_dict = {}
for row in reader:
    msg_dict[row['Code']] = row['Message']

HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400

def create_secret(secretname, secretvalue):
    '''[summary]
    Create a docker secret
    [description]
        secretname -- name of secret
        secretvalue -- value of secret
    Returns:
        [type] Integer -- [description] Id of the created secret
    
    Raises:
        e -- [description]
    '''
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    try:
        secret=client.api.create_secret(name=secretname,data=secretvalue.encode('utf-8'))
        secretid=secret.get('ID')

    except Exception as e:
        app.logger.error(e)
        raise

    return secretid

def add_secret_api():
    '''[summary]
    Creates a docker secret and distribute it to docker service
    [description]
    Input:
        name -- secret's name
        value -- secret's value
        service -- service' name
    Assuming that the service exists, this API creates a docker secret from the inputted name and value, then distribute the docker secret to the corresponding service
    Returns:
        [type] Json object -- [description] Successful message or error message
    '''

    # Parse query arguments
    parser = reqparse.RequestParser()
    parser.add_argument('name', help='Secret name')
    parser.add_argument('value', help='Secret value')
    parser.add_argument('service', help='Application/ service name')

    args = parser.parse_args()
    secret_name = args['name']
    secret_value = args['value']
    service_name = args['service']
    
    # Verify query arguments
    if(secret_name is None or secret_value  is None or service_name is None or secret_name=='' or  secret_value=='' or service_name==''): 
        data = {
            'code' : HTTP_CODE_BAD_REQUEST,
            'user message'  : msg_dict['bad_request_write_dksecret'],#'Bad request',
            'developer message' : msg_dict['bad_request_write_dksecret']
        }
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
        return resp

    # Create docker secret and add it to corresponding service
    try:
        secret_id = create_secret(secret_name, secret_value) # Create docker secret
    except Exception as e:
        data = {
            'code' : HTTP_CODE_BAD_REQUEST,
            'user message'  : msg_dict['existed_secret'],#'Bad request',
            'developer message' : msg_dict['existed_secret']
        }
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
        return resp

    try:    
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        service = client.services(filters={"name" : service_name}).pop(0) # Get the service by name
    except Exception as e:
        app.logger.error(e)
        data = {
            'code' : HTTP_CODE_BAD_REQUEST,
            'user message'  : msg_dict['non_exist_service'],#'Bad request',
            'developer message' : msg_dict['non_exist_service']
        }
        js = json.dumps(data)
        resp = Response(js, status=HTTP_CODE_BAD_REQUEST, mimetype='application/json')
        return resp

    service_id = service['ID'] # get service_id
    service_version = service['Version']['Index'] # get service_version
        
    container_spec = service['Spec']['TaskTemplate']['ContainerSpec'] #get service container specification
    current_secrets = []
    try:
        current_secrets = container_spec['Secrets'] # get the service's current secret list (if existed)
    except:
        pass

    secret_list = [docker.types.SecretReference(secret_id,secret_name)] # Create list of SecretReference
    container_spec['Secrets']=current_secrets+secret_list # update list of secrets for the service
    task_tmpl = docker.types.TaskTemplate(container_spec) # Create TaskTemplate from container specification
    #print "task template"
    #print task_tmpl.container_spec

    client.update_service(service=service_id,name=service_name,version=service_version,task_template=task_tmpl) # Update service with new secret list
    #print "config of service after update"
    #print client.inspect_service(service=service_name)

    data = {
        'code' : HTTP_CODE_CREATED,        
        'user message'  : msg_dict['write_dksecret_success'],
        'developer message'  : msg_dict['write_dksecret_success']
    }
    js = json.dumps(data)
    resp = Response(js, status=HTTP_CODE_CREATED, mimetype='application/json')

    return resp