import logging
from flask_restful import request, Resource
from hvac import exceptions
from lib.vault_backend import VaultBackend
from lib.json_response import JsonResponse


class Secrets(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')
        self._vault_backend = VaultBackend()

    def post(self):
        '''[summary]
        Create or update a secret in the vault
        [description]

        Arguments:
            name -- name of secret
            value -- value of secret
        '''
        self._logger.debug('Create / update secret endpoint called')

        secret_name = request.json['name']
        secret_value = request.json['value']

        if not secret_name or not secret_value:
            return JsonResponse.create(JsonResponse.WRITE_SECRET_BAD_REQUEST)

        secret = {'secret_value': secret_value}

        try:
            self._vault_backend.client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            self._logger.exception(error)
            return JsonResponse.create(JsonResponse.WRITE_SECRET_FAIL)

        return JsonResponse.create(JsonResponse.WRITE_SECRET_SUCCESS)

    def get(self, secret_name):
        '''[summary]
        Read a secret from the vault
        [description]

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        self._logger.debug('Read secret endpoint called')

        if not secret_name:
            return JsonResponse.create(JsonResponse.READ_SECRET_BAD_REQUEST)

        try:
            secret = self._vault_backend.client.secrets.kv.v1.read_secret(path=secret_name)
        except exceptions.InvalidPath as error:
            return JsonResponse.create(JsonResponse.SECRET_NOT_EXIST)
        except Exception as error:
            self._logger.exception(error)
            return JsonResponse.create(JsonResponse.READ_SECRET_FAIL)

        return JsonResponse.create(JsonResponse.READ_SECRET_SUCCESS, secret['data'])

    def put(self, secret_name):
        '''[summary]
        Update a secret in the vault
        [description]

        Arguments:
            secret_name {[type]} -- [description] Name of secret
        '''
        self._logger.debug('Update secret endpoint called')

        json_body = request.json
        secret_value = json_body['value']

        if not secret_value:
            return JsonResponse.create(JsonResponse.UPDATE_SECRET_BAD_REQUEST)

        try:
            secret = self._vault_backend.client.secrets.kv.v1.read_secret(path=secret_name)
        except exceptions.InvalidPath as error:
            return JsonResponse.create(JsonResponse.SECRET_NOT_EXIST)
        except Exception as error:
            self._logger.exception(error)
            return JsonResponse.create(JsonResponse.UPDATE_SECRET_FAIL)

        secret = {'secret_value': secret_value}

        try:
            self._vault_backend.client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            self._logger.exception(error)
            return JsonResponse.create(JsonResponse.UPDATE_SECRET_FAIL)

        return JsonResponse.create(JsonResponse.UPDATE_SECRET_SUCCESS)

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from the vault
        [description]
        '''
        self._logger.debug('Delete secret endpoint called')

        if not secret_name:
            return JsonResponse.create(JsonResponse.DELETE_SECRET_BAD_REQUEST)

        try:
            self._vault_backend.client.secrets.kv.v1.delete_secret(path=secret_name)
        except Exception as error:
            self._logger.exception(error)
            return JsonResponse.create(JsonResponse.DELETE_SECRET_FAIL)

        return JsonResponse.create(JsonResponse.DELETE_SECRET_SUCCESS)
