import logging
import hvac
from flask_restful import request, Resource
from lib.json_response import JsonResponse


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


class VaultBackendError(Exception):
    pass


class VaultBackend:
    # The Borg Singleton
    __shared_state = {}

    client = None

    def __init__(self):
        '''[summary]
        Initializes and unseals the Vault
        [description]
        Initializes the Vault, if it has not been initialized yet and unseals it.
        '''
        # The Borg Singleton
        self.__dict__ = self.__shared_state

        if not self.client:
            self._logger = logging.getLogger('flask.app')

            self._logger.debug('Initializing Vault.')

            self.client = hvac.Client(url=VAULT_URL)

            if self._is_vault_initialized():
                self._logger.debug('Vault already initalized.')

                self._load_keys()
            else:
                vault = self._init_vault()
                self._token = vault['root_token']
                self._unseal_keys = vault['keys']

                self._logger.debug('Vault initalized.')

                self._save_keys()

            self.client.token = self._token

            self._logger.debug('Unsealing Vault.')

            self._unseal_vault()

            self._logger.debug('Vault unsealed.')

    def _load_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
                self._token = token_file.read()
        except IOError as error:
            self._logger.error('Failed to read Vault token. Will not unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
                self._unseal_keys = unseal_keys_file.read().splitlines()
        except IOError as error:
            self._logger.error('Failed to read Vault unseal keys. Will not unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _save_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                token_file.write(self._token)
        except IOError as error:
            self._logger.error('Failed to write Vault token to file. Will not be able to reconnect.')
            self._logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
                for key in self._unseal_keys:
                    unseal_keys_file.write("%s\n" % key)
        except IOError as error:
            self._logger.error('Failed to write Vault unseal keys to file. Will not be able to reconnect.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _is_vault_initialized(self):
        try:
            return self.client.sys.is_initialized()
        except Exception as error:
            self._logger.error('Failed to check if Vault is initialized.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _init_vault(self):
        try:
            return self.client.sys.initialize(VAULT_SHARES, VAULT_THRESHOLD)
        except Exception as error:
            self._logger.error('Failed to initialize Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _unseal_vault(self):
        try:
            self.client.sys.submit_unseal_keys(self._unseal_keys)
        except Exception as error:
            self._logger.error('Failed to unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()


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
        except hvac.exceptions.InvalidPath as error:
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
        except hvac.exceptions.InvalidPath as error:
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
