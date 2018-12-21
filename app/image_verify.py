import logging
from flask import request
from flask import Response
from flask_restful import Resource
import requests
import requests.exceptions


IMAGE_VERIFIER_URL = "http://iivr:5000"


class ImageVerify(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')

    def post(self):
        self._logger.debug('Image verify endpoint called.')

        try:
            resp = requests.post(IMAGE_VERIFIER_URL + '/api/v1.0/image_verify', data=request.get_data())
        except requests.exceptions.RequestException as error:
            self._logger.error('Image Verifier unreachable.')
            self._logger.debug(error)
            return Response('Image Verifier unreachable.', 500)

        return Response(resp.content, resp.status_code)
