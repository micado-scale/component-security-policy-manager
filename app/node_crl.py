import logging
from flask import request, Response
from flask_restful import Resource
from requests import exceptions
from lib.vault_backend import VaultPkiBackend
from lib.json_response import JsonResponse


class NodeCrl(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')
        self._vault_backend = VaultPkiBackend()

    def get(self):
        '''[summary]
        Get the Certificate Revocation List for worker node certificates
        '''
        self._logger.info('Node CRL endpoint method GET from %s', request.remote_addr)

        try:
            crl = self._vault_backend.getAnonymous('/v1/pki/crl/pem')
        except exceptions.RequestException as error:
            self._logger.error('Unable to get CRL from Vault.')
            self._logger.info(error)
            return JsonResponse.create(JsonResponse.READ_SECRET_FAIL)

        return Response(crl.text, crl.status_code)
