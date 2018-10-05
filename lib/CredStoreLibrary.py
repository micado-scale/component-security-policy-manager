import os.path
import subprocess
import sys
import requests
import os
import json

http_code_ok = 200
#http_code_created = 201
#http_code_bad_request = 404

class CredStoreLibrary(object):

    def __init__(self):
        #self._sut_path = os.path.join(os.path.dirname(__file__),
         #                             '..', 'sut', 'login.py')
        self._status = ''
        self._data = ''

    def status_should_be(self, expected_status):
        if expected_status != str(self._status):
            raise AssertionError("Expected status to be '%s' but was '%s'."
                                 % (expected_status, self._status))

    def data_should_be(self, expected_data):
        if expected_data != str(self._data):
            raise AssertionError("Expected data to be '%s' but was '%s'."
                               % (expected_data, self._data))

    def add_a_secret(self, name, value):
        url     = 'http://127.0.0.1:5003/v1.0/secrets'
        payload = {'name': name, 'value': value}
        res = requests.post(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']     

    def update_a_secret(self,secretname,newvalue):
        url     = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        payload = {'value': newvalue}
        res = requests.put(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code'] 

    def delete_a_secret(self, secretname=None,):
        url     = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def read_a_secret(self, secretname=None):
        url     = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']
        if(self._status == http_code_ok):
            self._data = json_data['data']['secret_value']

    def init_a_vault(self, shares, threshold):
        url     = 'http://127.0.0.1:5003/v1.0/vaults'
        payload = {'shares': shares, 'threshold': threshold}
        res = requests.post(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def create_app_secret(self, secretname, secretvalue, servicename):
        url     = 'http://127.0.0.1:5003/v1.0/appsecrets'
        payload = {'name': secretname, 'value': secretvalue, 'service': servicename}
        res = requests.post(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def delete_app_secret(self, secretname, servicename):
        url     = 'http://127.0.0.1:5003/v1.0/appsecrets/' + secretname
        payload = {'service': servicename}
        res = requests.delete(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def retrieve_app_secret_id(self, secretname):
        url     = 'http://127.0.0.1:5003/v1.0/appsecrets/' + secretname
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']