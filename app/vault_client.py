from enum import Enum, IntEnum
import logging
import hvac
from flask_restful import request, Resource
from lib import json_response


# "http://127.0.0.1:8200" for localhost test,
# "http://credstore:8200" for docker environment
VAULT_URL = "http://credstore:8200"
# VAULT_URL = "http://127.0.0.1:8200"

# Number of generated unseal keys
VAULT_SHARES = 1

# Minimum number of keys needed to unseal the vault
VAULT_THRESHOLD = 1

# File to store vault token
VAULT_TOKEN_FILE = 'vaulttoken'

# File to store keys to unseal the vault
UNSEAL_KEYS_FILE = 'unsealkeys'


class HttpCode(IntEnum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    SERVER_ERROR = 500


class HttpBody(Enum):
    VAULT_EXISTS = 'vault_exists'
    INIT_VAULT_SUCCESS = 'init_vault_success'
    INIT_VAULT_FAIL = 'init_vault_fail'
    INIT_VAULT_BAD_REQUEST = 'init_vault_bad_request'
    VAULT_NOT_INITIALIZED = 'vault_not_initialized'
    WRITE_SECRET_SUCCESS = 'write_secret_success'
    WRITE_SECRET_FAIL = 'write_secret_fail'
    WRITE_SECRET_BAD_REQUEST = 'write_secret_bad_request'
    READ_SECRET_SUCCESS = 'read_secret_success'
    READ_SECRET_FAIL = 'read_secret_fail'
    READ_SECRET_BAD_REQUEST = 'read_secret_bad_request'
    UPDATE_SECRET_SUCCESS = 'update_secret_success'
    UPDATE_SECRET_FAIL = 'update_secret_fail'
    UPDATE_SECRET_BAD_REQUEST = 'update_secret_bad_request'
    DELETE_SECRET_SUCCESS = 'delete_secret_success'
    DELETE_SECRET_FAIL = 'delete_secret_fail'
    DELETE_SECRET_BAD_REQUEST = 'delete_secret_bad_request'
    SECRET_NOT_EXIST = 'secret_not_exist'


class VaultBackendError(Exception):
    pass


class VaultBackend:
    def __init__(self):
        '''[summary]
        Initializes and unseals the Vault
        [description]
        Initializes the Vault, if it has not been initialized yet and unseals it.
        '''
        self.logger = logging.getLogger('flask.app')

        self.logger.debug('Initializing Vault.')

        self.client = hvac.Client(url=VAULT_URL)

        if self._is_vault_initialized():
            self.logger.debug('Vault already initalized.')

            self._load_keys()
        else:
            vault = self._init_vault()
            self._token = vault['root_token']
            self._unseal_keys = vault['keys']

            self.logger.debug('Vault initalized.')

            self._save_keys()

        self.client.token = self._token

        self.logger.debug('Unsealing Vault.')

        self._unseal_vault()

        self.logger.debug('Vault unsealed.')

    def _load_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
                self._token = token_file.read()
        except IOError as error:
            self.logger.error('Failed to read Vault token. Will not unseal Vault.')
            self.logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
                self._unseal_keys = unseal_keys_file.read().splitlines()
        except IOError as error:
            self.logger.error('Failed to read Vault unseal keys. Will not unseal Vault.')
            self.logger.debug(error)
            raise VaultBackendError()

    def _save_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                token_file.write(self._token)
        except IOError as error:
            self.logger.error('Failed to write Vault token to file. Will not be able to reconnect.')
            self.logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
                for key in self._unseal_keys:
                    unseal_keys_file.write("%s\n" % key)
        except IOError as error:
            self.logger.error('Failed to write Vault unseal keys to file. Will not be able to reconnect.')
            self.logger.debug(error)
            raise VaultBackendError()

    def _is_vault_initialized(self):
        try:
            return self.client.sys.is_initialized()
        except Exception as error:
            self.logger.error('Failed to check if Vault is initialized.')
            self.logger.debug(error)
            raise VaultBackendError()

    def _init_vault(self):
        try:
            return self.client.sys.initialize(VAULT_SHARES, VAULT_THRESHOLD)
        except Exception as error:
            self.logger.error('Failed to initialize Vault.')
            self.logger.debug(error)
            raise VaultBackendError()

    def _unseal_vault(self):
        try:
            self.client.sys.submit_unseal_keys(self._unseal_keys)
        except Exception as error:
            self.logger.error('Failed to unseal Vault.')
            self.logger.debug(error)
            raise VaultBackendError()


class Secrets(Resource):
    def __init__(self):
        self.logger = logging.getLogger('flask.app')
        self.vault_backend = VaultBackend()

    def post(self):
        '''[summary]
        Create or update a secret in the vault
        [description]

        Arguments:
            name -- name of secret
            value -- value of secret
        '''
        self.logger.debug('Create / update secret endpoint called')

        secret_name = request.json['name']
        secret_value = request.json['value']

        if not secret_name or not secret_value:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.WRITE_SECRET_BAD_REQUEST.value)

        secret = {'secret_value': secret_value}

        try:
            self.vault_backend.client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            self.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.WRITE_SECRET_FAIL.value)

        return json_response.create(HttpCode.CREATED.value, HttpBody.WRITE_SECRET_SUCCESS.value)

    def get(self, secret_name):
        '''[summary]
        Read a secret from the vault
        [description]

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        self.logger.debug('Read secret endpoint called')

        if not secret_name:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.READ_SECRET_BAD_REQUEST.value)

        try:
            secret = self.vault_backend.client.secrets.kv.v1.read_secret(path=secret_name)
        except hvac.exceptions.InvalidPath as error:
            return json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
        except Exception as error:
            self.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.READ_SECRET_FAIL.value)

        return json_response.create(HttpCode.OK.value,
                                    HttpBody.READ_SECRET_SUCCESS.value,
                                    additional_json=secret['data'])

    def put(self, secret_name):
        '''[summary]
        Update a secret in the vault
        [description]

        Arguments:
            secret_name {[type]} -- [description] Name of secret
        '''
        self.logger.debug('Update secret endpoint called')

        json_body = request.json
        secret_value = json_body['value']

        if not secret_value:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.UPDATE_SECRET_BAD_REQUEST.value)

        try:
            secret = self.vault_backend.client.secrets.kv.v1.read_secret(path=secret_name)
        except hvac.exceptions.InvalidPath as error:
            return json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
        except Exception as error:
            self.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.UPDATE_SECRET_FAIL.value)

        secret = {'secret_value': secret_value}

        try:
            self.vault_backend.client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            self.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.UPDATE_SECRET_FAIL.value)

        return json_response.create(HttpCode.OK.value, HttpBody.UPDATE_SECRET_SUCCESS.value)

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from the vault
        [description]
        '''
        self.logger.debug('Delete secret endpoint called')

        if not secret_name:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.DELETE_SECRET_BAD_REQUEST.value)

        try:
            self.vault_backend.client.secrets.kv.v1.delete_secret(path=secret_name)
        except Exception as error:
            self.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.DELETE_SECRET_FAIL.value)

        return json_response.create(HttpCode.OK.value, HttpBody.DELETE_SECRET_SUCCESS.value)
