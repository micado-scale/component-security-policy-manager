import json
from flask import Response


def create(http_code,
           message_label,
           info_for_developer="",
           additional_json={}):
    '''[summary]
    Create a json object to respond a http request
    [description]
    Arguments:
    http_code {[type]} -- [description]
    message_label {[type]} -- [description]
    Keyword Arguments:
    info_for_developer {str} -- [description] (default: {""}) Additional
    information in string format
    additional_json {dict} -- [description] (default: {{}}) Additional
    information in json format
    Returns:
    Response [type] -- [description] http response
    '''
    data = {
        'code': http_code,
        'message': msg_dict[message_label] + info_for_developer
    }
    data.update(additional_json)
    js = json.dumps(data)
    resp = Response(js, status=http_code, mimetype='application/json')
    return resp


with open('secretvaultmessages.json', 'r', encoding='utf-8') as messagefile:
    msg_dict = json.load(messagefile)
