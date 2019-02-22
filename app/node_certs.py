import logging
import json
import uuid
from flask import request, Response
from flask_restful import Resource
from requests import exceptions
from lib.vault_backend import VaultPkiBackend
from lib.json_response import JsonResponse


class NodeCerts(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')
        self._vault_backend = VaultPkiBackend()

    def post(self):
        '''[summary]
        Register a new worker node in the Vault PKI.
        [description]
        A new certificate is generated for the client and is returned along with the private key.
        '''
        self._logger.info('Node Certs endpoint method POST from %s', request.remote_addr)

        worker_uuid = uuid.uuid4().hex

        params = {
            'common_name': worker_uuid + '.workernode.micado',
            'format': 'pem_bundle'
        }

        try:
            cert = self._vault_backend.post('/v1/pki/issue/micado', params)
        except exceptions.RequestException as error:
            self._logger.error('Unable to generate certificate in Vault PKI.')
            self._logger.info(error)
            return JsonResponse.create(JsonResponse.WRITE_SECRET_FAIL)

        if cert.status_code != 200:
            return Response(cert.text, cert.status_code)
        else:
            data = json.loads(cert.text)

            self._logger.info('Generated certificate with serial %s', data['data']['serial_number'])

            return Response(data['data']['certificate'], 200)

    def get(self, serial=None):
        '''[summary]
        Get a client certificate.
        [description]
        Returns a client's certificate identified by the serial.

        Arguments:
            [type] string -- [description] certificate's serial

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        self._logger.info('Node Certs endpoint method GET serial %s from %s', serial, request.remote_addr)

        if not serial:
            return self._list()

        try:
            if serial == 'ca':
                cert = self._vault_backend.getAnonymous('/v1/pki/ca/pem')
            else:
                cert = self._vault_backend.getAnonymous('/v1/pki/cert/' + serial)
        except exceptions.RequestException as error:
            self._logger.error('Unable to get certificate from Vault.')
            self._logger.info(error)
            return JsonResponse.create(JsonResponse.READ_SECRET_FAIL)

        if cert.status_code != 200 or serial == 'ca':
            return Response(cert.text, cert.status_code)
        else:
            data = json.loads(cert.text)
            return Response(data['data']['certificate'], 200)

    def _list(self):
        try:
            certlist = self._vault_backend.list('/v1/pki/certs')
        except exceptions.RequestException as error:
            self._logger.error('Unable to list certificates in Vault PKI.')
            self._logger.info(error)
            return JsonResponse.create(JsonResponse.WRITE_SECRET_FAIL)

        if certlist.status_code != 200:
            return Response(certlist.text, certlist.status_code)
        else:
            data = json.loads(certlist.text)
            return Response('\n'.join(data['data']['keys']), 200)

    def delete(self, serial=None):
        '''[summary]
        Revoke a certificate.
        [description]
        Revokes a client's certificate identified by the serial.

        Arguments:
            [type] string -- [description] certificate's serial
        '''
        self._logger.info('Node Certs endpoint method DELETE serial %s from %s', serial, request.remote_addr)

        if not serial:
            return JsonResponse.create(JsonResponse.DELETE_SECRET_BAD_REQUEST)

        params = {
            'serial_number': serial
        }

        try:
            resp = self._vault_backend.post('/v1/pki/revoke', params)
        except exceptions.RequestException as error:
            self._logger.error('Unable to revoke certificate in Vault PKI.')
            self._logger.info(error)
            return JsonResponse.create(JsonResponse.DELETE_SECRET_FAIL)

        if resp.status_code != 200:
            return Response(resp.text, resp.status_code)
        else:
            data = json.loads(resp.text)
            return Response(json.dumps(data['data']), 200)
