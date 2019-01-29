import logging
from flask import request
from flask import Response
from flask_restful import Resource
import requests
import requests.exceptions


CRYPTO_ENGINE_URL = "http://crypto_engine:5000"


class CryptoEngine(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')

    def get(self, path):
        self._logger.info('Crypto Engine endpoint method GET path %s from %s', path, request.remote_addr)

        try:
            resp = requests.post(CRYPTO_ENGINE_URL + '/api/v1.0/' + path)
        except requests.exceptions.RequestException as error:
            self._logger.error('Crypto Engine unreachable.')
            self._logger.info(error)
            return Response('Crypto Engine unreachable.', 500)

        return Response(resp.content, resp.status_code)

    def post(self, path):
        self._logger.info('Crypto Engine endpoint method POST path %s from %s', path, request.remote_addr)

        try:
            resp = requests.post(CRYPTO_ENGINE_URL + '/api/v1.0/' + path, data=request.get_data())
        except requests.exceptions.RequestException as error:
            self._logger.error('Crypto Engine unreachable.')
            self._logger.info(error)
            return Response('Crypto Engine unreachable.', 500)

        return Response(resp.content, resp.status_code)
