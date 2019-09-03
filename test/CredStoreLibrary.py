import json
import requests
from OpenSSL import crypto

http_code_ok = 200
# http_code_created = 201
# http_code_bad_request = 404


class CredStoreLibrary(object):

    def __init__(self):
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

    def data_should_not_be_empty(self):
        if str(self._data) == "":
            raise AssertionError("Data should not be empty, but was '%s'"
                                 % (self._data,))

    def common_name_should_be(self, expected_data):
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, self._data)
        subject = cert.get_subject()
        if subject != expected_data:
            raise AssertionError("Expected common name was '%s' but was '%s'."
                                 % (expected_data, subject))

    def add_a_secret(self, name, value):
        url = 'http://127.0.0.1:5003/v1.0/secrets'
        payload = {'name': name, 'value': value}
        res = requests.post(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def update_a_secret(self, secretname, newvalue):
        url = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        payload = {'value': newvalue}
        res = requests.put(url, json=payload)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def delete_a_secret(self, secretname=None,):
        url = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        res = requests.delete(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']

    def read_a_secret(self, secretname=None):
        url = 'http://127.0.0.1:5003/v1.0/secrets/' + secretname
        res = requests.get(url)
        json_data = json.loads(res.text)
        self._status = json_data['code']
        if(self._status == http_code_ok):
            self._data = json_data['secret_value']

    def get_the_certification_authority(self):
        url = 'http://127.0.0.1:5003/v1.0/nodecerts/ca'
        res = requests.get(url)
        self._status = res.status_code
        self._data = res.text

    def create_a_certificate(self, cert_common_name=None):
        url = 'http://127.0.0.1:5003/v1.0/nodecerts'
        if cert_common_name is not "":
            payload = {'cert_common_name': cert_common_name}
            res = requests.post(url, json=payload)
        else:
            res = requests.post(url)
        self._status = res.status_code
        self._data = res.text
