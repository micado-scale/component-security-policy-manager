import logging
import json
from flask import Response


def create(http_code,
           message_label,
           additional_json={}):
    '''[summary]
    Create a json object to respond a http request
    [description]
    Arguments:
    http_code {[type]} -- [description] HTTP status code
    message_label {[type]} -- [description] Message in the HTTP response body
    Returns:
    Response [type] -- [description] HTTP response object
    '''
    logger = logging.getLogger('flask.app')

    logger.debug(f'Creating json response with HTTP status {http_code} message "{msg_dict[message_label]}" and additional prameters {additional_json}')
    data = {
        'code': http_code,
        'message': msg_dict[message_label]
    }
    data.update(additional_json)
    js = json.dumps(data)
    resp = Response(js, status=http_code, mimetype='application/json')
    return resp


with open('lib/secretvaultmessages.json', 'r', encoding='utf-8') as messagefile:
    msg_dict = json.load(messagefile)
