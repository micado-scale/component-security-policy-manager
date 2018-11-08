import hvac
from flask_restful import request, marshal, fields, Resource
from app import app
from lib import json_response

# CONSTANT VALUES
# "http://127.0.0.1:8200" for localhost test,
# "http://credstore:8200" for docker environment
# If lack of http, it causes error: requests.exceptions.InvalidSchema:
# No connection adapters were found for 'credstore:8200/v1/sys/init'
VAULT_URL = "http://credstore:8200"
# VAULT_URL = "http://127.0.0.1:8200"

# HTTP codes
# Success
HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201
# Clients's errors
HTTP_CODE_BAD_REQUEST = 400
HTTP_CODE_NOT_FOUND = 404
# Server error
HTTP_CODE_SERVER_ERR = 500

# Number of generated keys
DEFAULT_SHARES = 1
# Number of minimum keys needed to unseal the vault
DEFAULT_THRESHOLD = 1

# File to store vault token
VAULT_TOKEN_FILE = 'vaulttoken'
# File to store keys to unseal the vault
UNSEAL_KEYS_FILE = 'unsealkeys'
# END - CONSTANT VALUES

# MODELS
vault_init_params = {
    'shares': fields.Integer,
    'threshold': fields.Integer
}
# END - MODELS

# INTERNAL FUNCTIONS


def read_token():
    """[summary]
    Read the token from file 'vaulttoken'
    [description]

    Returns:
      [type] string -- [description] the token
    """
    try:
        f = open(VAULT_TOKEN_FILE, 'r', encoding='utf-8')
        root_token = f.read()
        f.close()
    except Exception as e:
        app.logger.error(e)
        raise
    return root_token


def read_unseal_keys():
    """[summary]
    Read keys used to unseal the vault from file 'unsealkeys'
    [description]

    Returns:
      [type] List -- [description] List of keys
    """
    try:
        f = open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8')
        unseal_keys = f.read().splitlines()
        f.close()
        return unseal_keys
    except Exception as e:
        app.logger.error(e)
        raise


def init_client():
    """[summary]
    Initialize the vault client
    [description]

    Returns:
      [type] -- [description]
    """
    client = hvac.Client(url=VAULT_URL)
    return client


def unseal_vault(client):
    """[summary]
    Unseal (open) the vault
    [description]
    This must be done prior to read contents from the vault.
    Arguments:
      vault client {[type]} -- [description] vault client
    """
    client.token = read_token()
    # unseal the vault
    unseal_keys = read_unseal_keys()
    client.unseal_multi(unseal_keys)


def seal_vault(client):
    """[summary]
    Seal the vault
    [description]
    This should be done to protect the vault while not using it
    Arguments:
      vault client {[type]} -- [description] vault client
    """
    client.seal()
# END - INTERNAL FUNCTIONS

# RESOURCES


class Vaults(Resource):
    def post(self):
        """[summary]
        Initialize a vault in the Vault Server (Credential Store)
        [description]
        A number of keys will be generated from the master key, then the
        master key is thrown away (The Server will not store the key). The
        generated keys are kept by the Vault Client (Security Policy Manager)

        shares = The number of generated keys
        threshold = The minimum number of generated keys needed to unseal the
            vault
        """
        json_body = request.json

        marshal_json = marshal(json_body, vault_init_params)

        shares = marshal_json['shares']
        threshold = marshal_json['threshold']

        if(threshold > shares or
           (shares >= 2 and threshold == 1) or
           shares <= 0 or
           threshold <= 0):
            resp = json_response.create(HTTP_CODE_BAD_REQUEST,
                                        'init_vault_fail_due_to_parameter')
            return resp

        vault_exist = False
        try:
            client = init_client()
            vault_exist = client.is_initialized()
        except Exception as e:
            app.logger.error(e)
            # Fail to initialize vault
            resp = json_response.create(HTTP_CODE_SERVER_ERR,
                                        'init_vault_fail')
            return resp

        if(vault_exist):  # if vault existed
            resp = json_response.create(HTTP_CODE_CREATED, 'vault_exists')
            return resp
        else:
            vault = client.initialize(shares, threshold)
            root_token = vault['root_token']
            unseal_keys = vault['keys']
            # write root token into file
            f = open(VAULT_TOKEN_FILE, 'w', encoding='utf-8')
            f.write(root_token)
            f.close()

            # write unseal_keys into file
            f = open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8')
            for key in unseal_keys:
                f.write("%s\n" % key)
            f.close()
            # Initialize vault successfully
            resp = json_response.create(HTTP_CODE_CREATED,
                                        'init_vault_success')
            return resp


class Secrets(Resource):
    def post(self):
        '''[summary]
         Write or update a secret to the vault
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
                secret_name == ''):  # verify parameters
            resp = json_response.create(HTTP_CODE_BAD_REQUEST,
                                        'bad_request_write_secret')
            return resp

        client = init_client()
        try:
            unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HTTP_CODE_SERVER_ERR,
                                        'vault_not_initialized')
            return resp

        client.write('secret/'+secret_name,
                     secret_value=secret_value)  # , lease='1h'
        seal_vault(client)

        resp = json_response.create(HTTP_CODE_CREATED, 'write_secret_success')
        return resp


class Secret(Resource):
    def get(self, secret_name):
        """[summary]
        Read a secret from the vault
        [description]

        Returns:
          [type] json -- [description] a dictionary of all relevant
          information of the secret
        """
        if(secret_name is None or secret_name == ''):  # verify parameters
            resp = json_response.create(HTTP_CODE_BAD_REQUEST,
                                        'bad_request_read_secret')
            return resp

        # unseal the vault
        client = init_client()
        try:
            unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HTTP_CODE_SERVER_ERR,
                                        'vault_not_initialized')
            return resp

        secret_values = client.read('secret/'+secret_name)
        seal_vault(client)

        if(secret_values is None):  # If the required secret does not exist
            resp = json_response.create(HTTP_CODE_NOT_FOUND,
                                        'secret_not_exist')
            return resp
        else:
            resp = json_response.create(HTTP_CODE_OK,
                                        'read_secret_success',
                                        additional_json=secret_values)
            return resp

    def delete(self, secret_name):
        """[summary]
        Remove a secret from the vault
        [description]
        """
        if(secret_name is None or secret_name == ''):  # verify parameters
            # 'Lack of secret name'
            resp = json_response.create(HTTP_CODE_BAD_REQUEST,
                                        'bad_request_delete_secret')
            return resp

        # unseal the vault
        client = init_client()
        try:
            unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HTTP_CODE_SERVER_ERR,
                                        'vault_not_initialized')
            return resp

        client.delete('secret/'+secret_name)
        seal_vault(client)

        # 'Delete secret successfully
        resp = json_response.create(HTTP_CODE_OK, 'delete_secret_success')
        return resp

    def put(self, secret_name):
        '''[summary]
        Update a secret in the vault
        [description]

        Arguments:
            secret_name {[type]} -- [description] Name of secret

        Returns:
            [type] -- [description]
        '''
        json_body = request.json
        secret_value = json_body['value']

        if(secret_value is None or secret_value == ''):  # verify parameters
            # 'Lack of secret name'
            resp = json_response.create(HTTP_CODE_BAD_REQUEST,
                                        'bad_request_update_secret')
            return resp

        # unseal the vault
        client = init_client()
        try:
            unseal_vault(client)
        except Exception as e:
            app.logger.error(e)
            resp = json_response.create(HTTP_CODE_SERVER_ERR,
                                        'vault_not_initialized')
            return resp

        secret_values = client.read('secret/'+secret_name)

        if(secret_values is None):  # If the required secret does not exist
            resp = json_response.create(HTTP_CODE_NOT_FOUND,
                                        'secret_not_exist')
            return resp
        else:
            client.write('secret/'+secret_name,
                         secret_value=secret_value)  # , lease='1h'
            seal_vault(client)
            resp = json_response.create(HTTP_CODE_OK, 'update_secret_success')
            return resp
# END - RESOURCES
