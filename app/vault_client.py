from enum import Enum, IntEnum
import hvac
from flask_restful import request, marshal, fields, Resource
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
    WRITE_SECRET_BAD_REQUEST = 'write_secret_bad_request'
    READ_SECRET_SUCCESS = 'read_secret_success'
    READ_SECRET_BAD_REQUEST = 'read_secret_bad_request'
    UPDATE_SECRET_SUCCESS = 'update_secret_success'
    UPDATE_SECRET_BAD_REQUEST = 'update_secret_bad_request'
    DELETE_SECRET_SUCCESS = 'delete_secret_success'
    DELETE_SECRET_BAD_REQUEST = 'delete_secret_bad_request'
    SECRET_NOT_EXIST = 'secret_not_exist'


class Vaults(Resource):
    def post(self):
        '''[summary]
        Initialize a vault in the Vault Server (Credential Store)
        [description]
        A number of keys will be generated from the master key, then the
        master key is thrown away (The Server will not store the key). The
        generated keys are kept by the Vault Client (Security Policy Manager)

        shares = The number of generated keys
        threshold = The minimum number of generated keys needed to unseal the
            vault
        '''
        app.logger.debug('Init vault endpoint called')

        json_body = request.json

        marshal_json = marshal(json_body, _vault_init_params)

        shares = marshal_json['shares']
        threshold = marshal_json['threshold']

        if threshold > shares or shares >= 2 and threshold == 1 or shares < 1 or threshold < 1:
            resp = json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.INIT_VAULT_BAD_REQUEST.value)
            return resp

        vault_exist = False
        try:
            client = _init_client()
            vault_exist = client.is_initialized()
        except Exception as e:
            app.logger.exception(e)
            resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.INIT_VAULT_FAIL.value)
            return resp

        if vault_exist:
            resp = json_response.create(HttpCode.CREATED.value, HttpBody.VAULT_EXISTS.value)
            return resp
        else:
            vault = client.initialize(shares, threshold)
            root_token = vault['root_token']
            unseal_keys = vault['keys']

            try:
                _write_token(root_token)
            except IOError as error:
                resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.INIT_VAULT_FAIL.value)
                return resp

            try:
                _write_unseal_keys(unseal_keys)
            except IOError as error:
                resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.INIT_VAULT_FAIL.value)
                return resp

            resp = json_response.create(HttpCode.CREATED.value, HttpBody.INIT_VAULT_SUCCESS.value)
            return resp


class Secrets(Resource):
    def post(self):
        '''[summary]
        Create or update a secret in the vault
        [description]

        Arguments:
            name -- name of secret
            value -- value of secret
        '''
        app.logger.debug('Create / update secret endpoint called')

        json_body = request.json
        secret_name = json_body['name']
        secret_value = json_body['value']

        if not secret_name or not secret_value:
            resp = json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.WRITE_SECRET_BAD_REQUEST.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.exception(e)
            resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.VAULT_NOT_INITIALIZED.value)
            return resp

        client.write('secret/'+secret_name,
                     secret_value=secret_value)
        _seal_vault(client)

        resp = json_response.create(HttpCode.CREATED.value, HttpBody.WRITE_SECRET_SUCCESS.value)
        return resp


class Secret(Resource):
    def get(self, secret_name):
        '''[summary]
        Read a secret from the vault
        [description]

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        app.logger.debug('Read secret endpoint called')

        if not secret_name:
            resp = json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.READ_SECRET_BAD_REQUEST.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.exception(e)
            resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.VAULT_NOT_INITIALIZED.value)
            return resp

        secret_values = client.read('secret/'+secret_name)
        _seal_vault(client)

        if not secret_values:
            resp = json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
            return resp
        else:
            resp = json_response.create(HttpCode.OK.value,
                                        HttpBody.READ_SECRET_SUCCESS.value,
                                        additional_json=secret_values)
            return resp

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from the vault
        [description]
        '''
        app.logger.debug('Delete secret endpoint called')

        if not secret_name:
            resp = json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.DELETE_SECRET_BAD_REQUEST.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.exception(e)
            resp = json_response.create(HttpCode.SERVER_ERROR.value,  HttpBody.VAULT_NOT_INITIALIZED.value)
            return resp

        client.delete('secret/'+secret_name)
        _seal_vault(client)

        resp = json_response.create(HttpCode.OK.value, HttpBody.DELETE_SECRET_SUCCESS.value)
        return resp

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
            resp = json_response.create(HttpCode.BAD_REQUEST.value, HttpBody.UPDATE_SECRET_BAD_REQUEST.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.exception(e)
            resp = json_response.create(HttpCode.SERVER_ERROR.value, HttpBody.VAULT_NOT_INITIALIZED.value)
            return resp

        secret_values = client.read('secret/'+secret_name)

        if not secret_values:
            resp = json_response.create(HttpCode.NOT_FOUND.value, HttpBody.SECRET_NOT_EXIST.value)
            return resp
        else:
            client.write('secret/'+secret_name,
                         secret_value=secret_value)
            _seal_vault(client)
            resp = json_response.create(HttpCode.OK.value, HttpBody.UPDATE_SECRET_SUCCESS.value)
            return resp


def _write_token(root_token):
    app.logger.debug('Writing vault token')

    try:
        with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
            token_file.write(root_token)
    except IOError as error:
        app.logger.exception(error)
        raise

    app.logger.debug('Vault token written')


def _read_token():
    '''[summary]
    Read the token from file 'vaulttoken'
    [description]

    Returns:
    [type] string -- [description] the token
    '''
    app.logger.debug('Reading vault token')

    try:
        with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
            root_token = token_file.read()
    except IOError as error:
        app.logger.exception(error)
        raise

    app.logger.debug('Vault token read')

    return root_token


def _write_unseal_keys(unseal_keys):
    app.logger.debug('Writing vault unseal keys')

    try:
        with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
            for key in unseal_keys:
                # FIXME \n
                unseal_keys_file.write("%s\n" % key)
    except IOError as error:
        app.logger.exception(error)

    app.logger.debug('Unseal keys written')


def _read_unseal_keys():
    '''[summary]
    Read keys used to unseal the vault from file 'unsealkeys'
    [description]

    Returns:
    [type] List -- [description] List of keys
    '''
    app.logger.debug('Reading vault unseal keys')

    try:
        with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
            unseal_keys = unseal_keys_file.read().splitlines()
    except IOError as error:
        app.logger.exception(error)
        raise

    app.logger.debug('Unseal keys read')

    return unseal_keys


def _init_client():
    '''[summary]
    Initialize the vault client
    [description]
    '''
    app.logger.debug('Initializing vault client')

    client = hvac.Client(url=VAULT_URL)

    app.logger.debug('Vault client initialized')

    return client


def _unseal_vault(client):
    '''[summary]
    Unseal (open) the vault
    [description]
    This must be done prior to read contents from the vault.
    Arguments:
    vault client {[type]} -- [description] vault client
    '''
    app.logger.debug('Unsealing vault')

    client.token = _read_token()
    unseal_keys = _read_unseal_keys()
    client.unseal_multi(unseal_keys)

    app.logger.debug('Vault unsealed')


def _seal_vault(client):
    '''[summary]
    Seal the vault
    [description]
    This should be done to protect the vault while not using it
    Arguments:
    vault client {[type]} -- [description] vault client
    '''
    app.logger.debug('Sealing vault')

    client.seal()

    app.logger.debug('Vault sealed')


_vault_init_params = {
    'shares': fields.Integer,
    'threshold': fields.Integer
}
