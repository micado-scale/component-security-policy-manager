import os.path
import subprocess
import sys
import requests
import os
import json

http_code_ok = 200
class CredStoreLibrary(object):

    def __init__(self):
        #self._sut_path = os.path.join(os.path.dirname(__file__),
         #                             '..', 'sut', 'login.py')
        self._status = ''
        self._data = ''

    def print_hello(self):
        url     = 'http://127.0.0.1:5003/v1.0/'
        res = requests.get(url)
        self._status = res.status_code

    def add_a_secret(self, name, value):
        url     = 'http://127.0.0.1:5003/v1.0/addsecret'
        payload = {'name': name, 'value': value}
        res = requests.post(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']     

    def status_should_be(self, expected_status):
        if expected_status != str(self._status):
            raise AssertionError("Expected status to be '%s' but was '%s'."
                                 % (expected_status, self._status))

    def data_should_be(self, expected_data):
        if expected_data != str(self._data):
            raise AssertionError("Expected data to be '%s' but was '%s'."
                               % (expected_data, self._data))

    def delete_a_secret(self, secretname=None,):
        url     = 'http://127.0.0.1:5003/v1.0/deletesecret'
        payload = {'name': secretname}
        res = requests.put(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def read_a_secret(self, secretname=None):
        url     = 'http://127.0.0.1:5003/v1.0/readsecret'
        payload = {'name': secretname}
        res = requests.get(url, data=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']
        if(self._status == http_code_ok):
            self._data = json_data['data']['secret_value']