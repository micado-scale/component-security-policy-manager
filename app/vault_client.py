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
    ok = 200
    created = 201
    bad_request = 400
    not_found = 404
    server_error = 500


class HttpBody(Enum):
    init_vault_success = 'init_vault_success'
    vault_exists = 'vault_exists'
    init_vault_fail = 'init_vault_fail'
    init_vault_fail_due_to_parameter = 'init_vault_fail_due_to_parameter'
    vault_not_initialized = 'vault_not_initialized'
    write_secret_success = 'write_secret_success'
    bad_request_write_secret = 'bad_request_write_secret'
    read_secret_success = 'read_secret_success'
    bad_request_read_secret = 'bad_request_read_secret'
    update_secret_success = 'update_secret_success'
    bad_request_update_secret = 'bad_request_update_secret'
    delete_secret_success = 'delete_secret_success'
    bad_request_delete_secret = 'bad_request_delete_secret'
    secret_not_exist = 'secret_not_exist'


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
        json_body = request.json

        marshal_json = marshal(json_body, _vault_init_params)

        shares = marshal_json['shares']
        threshold = marshal_json['threshold']

        if(threshold > shares or
           (shares >= 2 and threshold == 1) or
           shares <= 0 or
           threshold <= 0):
            resp = json_response.create(HttpCode.bad_request.value, HttpBody.init_vault_fail_due_to_parameter.value)
            return resp

        vault_exist = False
        try:
            client = _init_client()
            vault_exist = client.is_initialized()
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HttpCode.server_error.value, HttpBody.init_vault_fail.value)
            return resp

        if(vault_exist):
            resp = json_response.create(HttpCode.created.value, HttpBody.vault_exists.value)
            return resp
        else:
            vault = client.initialize(shares, threshold)
            root_token = vault['root_token']
            unseal_keys = vault['keys']

# TODO: exception handling
            with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                token_file.write(root_token)

# TODO: exception handling
            with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
                for key in unseal_keys:
                    # FIXME \n
                    unseal_keys_file.write("%s\n" % key)

            resp = json_response.create(HttpCode.created.value, HttpBody.init_vault_success.value)
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
        json_body = request.json
        secret_name = json_body['name']
        secret_value = json_body['value']

        if (secret_name is None or
            secret_value is None or
            secret_value == '' or
                secret_name == ''):
            resp = json_response.create(HttpCode.bad_request.value, HttpBody.bad_request_write_secret.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HttpCode.server_error.value, HttpBody.vault_not_initialized.value)
            return resp

        client.write('secret/'+secret_name,
                     secret_value=secret_value)
        _seal_vault(client)

        resp = json_response.create(HttpCode.created.value, HttpBody.write_secret_success.value)
        return resp


class Secret(Resource):
    def get(self, secret_name):
        '''[summary]
        Read a secret from the vault
        [description]

        Returns:
            [type] json -- [description] a dictionary of secret data and associated metadata as per Vault documentation
        '''
        if(secret_name is None or secret_name == ''):
            resp = json_response.create(HttpCode.bad_request.value, HttpBody.bad_request_read_secret.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HttpCode.server_error.value, HttpBody.vault_not_initialized.value)
            return resp

        secret_values = client.read('secret/'+secret_name)
        _seal_vault(client)

        if(secret_values is None):
            resp = json_response.create(HttpCode.not_found.value, HttpBody.secret_not_exist.value)
            return resp
        else:
            resp = json_response.create(HttpCode.ok.value,
                                        HttpBody.read_secret_success.value,
                                        additional_json=secret_values)
            return resp

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from the vault
        [description]
        '''
        if(secret_name is None or secret_name == ''):
            resp = json_response.create(HttpCode.bad_request.value, HttpBody.bad_request_delete_secret.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HttpCode.server_error.value,  HttpBody.vault_not_initialized.value)
            return resp

        client.delete('secret/'+secret_name)
        _seal_vault(client)

        resp = json_response.create(HttpCode.ok.value, HttpBody.delete_secret_success.value)
        return resp

    def put(self, secret_name):
        '''[summary]
        Update a secret in the vault
        [description]

        Arguments:
            secret_name {[type]} -- [description] Name of secret
        '''
        json_body = request.json
        secret_value = json_body['value']

        if(secret_value is None or secret_value == ''):
            resp = json_response.create(HttpCode.bad_request.value, HttpBody.bad_request_update_secret.value)
            return resp

        client = _init_client()
        try:
            _unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HttpCode.server_error.value, HttpBody.vault_not_initialized.value)
            return resp

        secret_values = client.read('secret/'+secret_name)

        if(secret_values is None):
            resp = json_response.create(HttpCode.not_found.value, HttpBody.secret_not_exist.value)
            return resp
        else:
            client.write('secret/'+secret_name,
                         secret_value=secret_value)
            _seal_vault(client)
            resp = json_response.create(HttpCode.ok.value, HttpBody.update_secret_success.value)
            return resp


def _read_token():
    '''[summary]
    Read the token from file 'vaulttoken'
    [description]

    Returns:
    [type] string -- [description] the token
    '''
    try:
        with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
            root_token = token_file.read()
    except IOError as error:
        app.logger.error(error)
        raise
    return root_token


def _read_unseal_keys():
    '''[summary]
    Read keys used to unseal the vault from file 'unsealkeys'
    [description]

    Returns:
    [type] List -- [description] List of keys
    '''
    try:
        with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
            unseal_keys = unseal_keys_file.read().splitlines()
    except IOError as error:
        app.logger.error(error)
        raise
    return unseal_keys


def _init_client():
    '''[summary]
    Initialize the vault client
    [description]
    '''
    client = hvac.Client(url=VAULT_URL)
    return client


def _unseal_vault(client):
    '''[summary]
    Unseal (open) the vault
    [description]
    This must be done prior to read contents from the vault.
    Arguments:
    vault client {[type]} -- [description] vault client
    '''
    client.token = _read_token()
    unseal_keys = _read_unseal_keys()
    client.unseal_multi(unseal_keys)


def _seal_vault(client):
    '''[summary]
    Seal the vault
    [description]
    This should be done to protect the vault while not using it
    Arguments:
    vault client {[type]} -- [description] vault client
    '''
    client.seal()


_vault_init_params = {
    'shares': fields.Integer,
    'threshold': fields.Integer
}
