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
from .commonfunc import *

##### CONSTANT VALUES
HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201

# Clients's errors
HTTP_CODE_BAD_REQUEST = 400

DEBUG_MODE = False
##### END - CONSTANT VALUES

##### INTERNAL FUNCTIONS
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

def delete_secret(secretname):
    '''[summary]
    Delete a docker secret
    [description]
    
    Arguments:
        secretname {[type]} -- [description] Name of secret
    '''
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    try:
        if DEBUG_MODE:
            print('\nDelete docker secret')

        secret_id = client.api.secrets(filters={"name" : secretname})[0]['ID']

        if DEBUG_MODE:
            print('\nSecret id:', secret_id)
        client.api.remove_secret(secret_id)

    except Exception as e:
        app.logger.error(e)
        raise

##### END - INTERNAL FUNCTIONS

##### RESOURCES
class Dksecrets(Resource):
    def post(self):
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

        json_body = request.json

        secret_name = json_body['name'] # Secret name
        secret_value = json_body['value'] #Secret value
        service_name = json_body['service'] #Application/ service name
        
        # Verify query arguments
        if(secret_name is None or secret_value  is None or service_name is None or secret_name=='' or  secret_value=='' or service_name==''): 
            resp = create_json_response(HTTP_CODE_BAD_REQUEST,'bad_request_write_dksecret')
            return resp

        if DEBUG_MODE:
            print('\nADD APPLICATION SECRET INTO DOCKER')

        try:    
            client = docker.APIClient(base_url='unix://var/run/docker.sock')
            service = client.services(filters={"name" : service_name}).pop(0) # Get the service by name
        except Exception as e:
            app.logger.error(e)
            resp = create_json_response(HTTP_CODE_BAD_REQUEST,'non_exist_service')
            return resp

        # Create docker secret and add it to corresponding service
        try:
            secret_id = create_secret(secret_name, secret_value) # Create docker secret
        except Exception as e:
            #app.logger.error(e)
            resp = create_json_response(HTTP_CODE_BAD_REQUEST,'existed_secret')
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

        if DEBUG_MODE:
            print("Task template", task_tmpl.container_spec)

        client.update_service(service=service_id, name=service_name, version=service_version,
            task_template=task_tmpl, fetch_current_spec=True) # Update service with new secret list

        if DEBUG_MODE:
            print("Config of service after update:", client.inspect_service(service=service_name))

        resp = create_json_response(HTTP_CODE_CREATED,'write_dksecret_success')
        return resp

class Dksecret(Resource):
    def delete(self,secret_name):
        '''[summary]
        Remove secret from a service.
        [description]
        Remove secret from all container of a services. If there are no other services using the secret, delete the secret from docker swarm
        Arguments:
            secret_name {[type]} -- [description] Name of secret
        
        Returns:
            Json [type] -- [description] Returned message
        
        Raises:
            e -- [description]
        '''
        json_body = request.json
        service_name = json_body['service'] #Application/ service name
        
        if DEBUG_MODE:
            print('\nDELETE SERVICE SECRET')

        try:    
            client = docker.APIClient(base_url='unix://var/run/docker.sock')
            service = client.services(filters={"name" : service_name}).pop(0) # Get the service by name
        except Exception as e:
            app.logger.error(e)
            resp = create_json_response(HTTP_CODE_BAD_REQUEST,'non_exist_service')
            return resp

        service_id = service['ID'] # get service_id
        service_version = service['Version']['Index'] # get service_version

        container_spec = service['Spec']['TaskTemplate']['ContainerSpec'] #get service container specification
        current_secrets = []
        try:
            current_secrets = container_spec['Secrets']
            if DEBUG_MODE:
                print('\nSecret list before removed: ', current_secrets)
                print('1 item: ',current_secrets[0])
                print('Type of current_secrets: ', type(current_secrets))
                print('Type of item: ', type(current_secrets[0]))
                print('Secret name of 1st item: ', current_secrets[0]['SecretName'])
            
            update_current_secrets = [x for x in current_secrets if x['SecretName'] != secret_name]
            
            if DEBUG_MODE:
                print('\nSecret list after removed: ', update_current_secrets)

            container_spec['Secrets'] = update_current_secrets  
        except Exception as e:
            app.logger.error(e)
            raise e

        task_tmpl = docker.types.TaskTemplate(container_spec) # Create TaskTemplate from container specification

        if DEBUG_MODE:
            print("\nTask template", task_tmpl.container_spec)

        client.update_service(service=service_id, name=service_name, version=service_version,
            task_template=task_tmpl, fetch_current_spec=True) # Update service with new secret list

        if DEBUG_MODE:
            print("\nConfig of service after update:", client.inspect_service(service=service_name))

        # Try to delete docker secret (if no other services are using it)
        try:
            delete_secret(secret_name)
        except Exception as e:
            app.logger.error(e)
            pass

        resp = create_json_response(HTTP_CODE_OK,'remove_dksecret_success')
        return resp
    def get(self, secret_name):
        '''[summary]
        Retrieve id of a secret
        [description]
        
        Arguments:
            secret_name {[type]} -- [description] Name of secret
        
        Returns:
            [type] -- [description]
        '''
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        if DEBUG_MODE:
            print('\nRetrieve docker secret')

        try:
            secret_id = client.api.secrets(filters={"name" : secret_name})[0]['ID']

            if DEBUG_MODE:
                print('\nSecret id:', secret_id)
            info = {'secret_id':secret_id}
            resp = create_json_response(HTTP_CODE_OK,'secret_exists', additional_json =info)
            return resp
        except Exception as e:
            app.logger.error(e)
            resp = create_json_response(HTTP_CODE_BAD_REQUEST,'non_exist_secret')
            return resp
##### END - RESOURCES