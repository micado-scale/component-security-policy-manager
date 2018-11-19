from enum import Enum, IntEnum
import hvac
from flask_restful import request, Resource
from app import app
from lib import json_response


# "http://127.0.0.1:8200" for localhost test,
# "http://credstore:8200" for docker environment
VAULT_URL = "http://credstore:8200"
# VAULT_URL = "http://127.0.0.1:8200"

# Number of generated unseal keys
DEFAULT_SHARES = 1

# Minimum number of keys needed to unseal the vault
DEFAULT_THRESHOLD = 1

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
        app.logger.debug('Initializing Vault.')

        client = hvac.Client(url=VAULT_URL)

        try:
            vault_initialized = client.sys.is_initialized()
        except Exception as error:
            app.logger.error('Failed to check if Vault is initialized.')
            app.logger.debug(error)
            raise VaultBackendError()

        if vault_initialized:
            app.logger.debug('Vault already initalized.')

            try:
                with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
                    self.token = token_file.read()
            except IOError as error:
                app.logger.error('Failed to read Vault token. Will not unseal Vault.')
                app.logger.debug(error)
                raise VaultBackendError()

            try:
                with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
                    unseal_keys = unseal_keys_file.read().splitlines()
            except IOError as error:
                app.logger.error('Failed to read Vault unseal keys. Will not unseal Vault.')
                app.logger.debug(error)
                raise VaultBackendError()

        else:
            try:
                vault = client.sys.initialize(1, 1)
            except Exception as error:
                app.logger.error('Failed to initialize Vault.')
                app.logger.debug(error)
                raise VaultBackendError()

            app.logger.debug('Vault initalized.')

            self.token = vault['root_token']

            try:
                with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                    token_file.write(self.token)
            except IOError as error:
                app.logger.error('Failed to write Vault token to file. Will not be able to reconnect.')
                app.logger.debug(error)
                raise VaultBackendError()

            unseal_keys = vault['keys']

            try:
                with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
                    for key in unseal_keys:
                        unseal_keys_file.write("%s\n" % key)
            except IOError as error:
                app.logger.error('Failed to write Vault unseal keys to file. Will not be able to reconnect.')
                app.logger.debug(error)
                raise VaultBackendError()

        client.token = self.token

        app.logger.debug('Unsealing Vault.')

        try:
            client.sys.submit_unseal_keys(unseal_keys)
        except Exception as error:
            app.logger.error('Failed to unseal Vault.')
            app.logger.debug(error)
            raise VaultBackendError()

        app.logger.debug('Vault unsealed.')

    def init_client(self):
        '''[summary]
        Initialize the vault client
        [description]
        '''
        app.logger.debug('Initializing vault client')

        client = hvac.Client(url=VAULT_URL)
        client.token = self.token

        app.logger.debug('Vault client initialized')

        return client


class Secrets(Resource):
    def __init__(self):
        self.vault_backend = VaultBackend()

    def post(self):
        '''[summary]
        Create or update a secret in the vault
        [description]

        Arguments:
            name -- name of secret
            value -- value of secret
        '''
        app.logger.debug('Create / update secret endpoint called')

        secret_name = request.json['name']
        secret_value = request.json['value']

        if not secret_name or not secret_value:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.WRITE_SECRET_BAD_REQUEST.value)

        client = self.vault_backend.init_client()

        secret = {'secret_value': secret_value}

        try:
            client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            app.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.WRITE_SECRET_FAIL.value)

        return json_response.create(HttpCode.CREATED.value, HttpBody.WRITE_SECRET_SUCCESS.value)

    def get(self, secret_name):
        '''[summary]
        Read a secret from the vault
        [description]

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        app.logger.debug('Read secret endpoint called')

        if not secret_name:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.READ_SECRET_BAD_REQUEST.value)

        client = self.vault_backend.init_client()

        try:
            secret = client.secrets.kv.v1.read_secret(path=secret_name)
        except hvac.exceptions.InvalidPath as error:
            return json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
        except Exception as error:
            app.logger.exception(error)
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
        app.logger.debug('Update secret endpoint called')

        json_body = request.json
        secret_value = json_body['value']

        if not secret_value:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.UPDATE_SECRET_BAD_REQUEST.value)

        client = self.vault_backend.init_client()

        try:
            secret = client.secrets.kv.v1.read_secret(path=secret_name)
        except hvac.exceptions.InvalidPath as error:
            return json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
        except Exception as error:
            app.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.UPDATE_SECRET_FAIL.value)

        secret = {'secret_value': secret_value}

        try:
            client.secrets.kv.v1.create_or_update_secret(path=secret_name, secret=secret)
        except Exception as error:
            app.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.UPDATE_SECRET_FAIL.value)

        return json_response.create(HttpCode.OK.value, HttpBody.UPDATE_SECRET_SUCCESS.value)

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from the vault
        [description]
        '''
        app.logger.debug('Delete secret endpoint called')

        if not secret_name:
            return json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.DELETE_SECRET_BAD_REQUEST.value)

        client = self.vault_backend.init_client()

        try:
            client.secrets.kv.v1.delete_secret(path=secret_name)
        except Exception as error:
            app.logger.exception(error)
            return json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.DELETE_SECRET_FAIL.value)

        return json_response.create(HttpCode.OK.value, HttpBody.DELETE_SECRET_SUCCESS.value)
