from enum import Enum
import logging
import json
from flask import Response


class JsonResponse(Enum):
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

    @classmethod
    def create(cls, message_label, payload={}):
        '''[summary]
        Create a json object to respond a http request.
        [description]
        Arguments:
        message_label {[type]} -- [description] Message in the HTTP response body, loaded from json file.
        payload {[type]} -- [description] Payload in the json response, defaults to empty.
        Returns:
        Response [type] -- [description] HTTP response object
        '''
        logger = logging.getLogger('flask.app')

        logger.debug(f'Creating json response with HTTP status {cls._msg_dict[message_label.value][0]}, '
                     f'message "{cls._msg_dict[message_label.value][1]}" and payload {payload}')

        data = {
            'code': cls._msg_dict[message_label.value][0],
            'message': cls._msg_dict[message_label.value][1]
        }
        data.update(payload)
        js = json.dumps(data)

        return Response(js, status=cls._msg_dict[message_label.value][0], mimetype='application/json')


with open('lib/secretvaultmessages.json', 'r', encoding='utf-8') as messagefile:
    JsonResponse._msg_dict = json.load(messagefile)
