import logging
from flask import request
from flask import Response
from flask_restful import Resource
from lib.kubernetes_backend import KubernetesBackend, KubernetesBackendError, KubernetesBackendKeyNotFoundError


class AppSecrets(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')
        self._kubernetes_backend = KubernetesBackend()

    def post(self):
        '''[summary]
        Create a secret in kubernetes
        [description]

        Arguments:
            name -- name of secret
            value -- value of secret
        '''
        secret_name = request.json['name']
        secret_value = request.json['value']

        self._logger.info('App Secrets endpoint method POST secret "%s" from %s', secret_name, request.remote_addr)

        if not secret_name or not secret_value:
            return Response('Unable to create Kubernetes secret, missing parameters.', 400)

        try:
            self._kubernetes_backend.create_secret(secret_name, secret_value)
        except KubernetesBackendError as error:
            self._logger.error('Unable to create Kubernetes secret.')
            self._logger.info(error)
            return Response('Unable to create Kubernetes secret.', 500)

        return Response('Created', 201)

    def get(self, secret_name):
        '''[summary]
        Read a secret from kubernetes
        [description]

        Returns:
            [type] string -- [description] the secret value
        '''
        self._logger.info('App Secrets endpoint method GET secret "%s" from %s', secret_name, request.remote_addr)

        if not secret_name:
            return Response('Unable to read Kubernetes secret, missing parameters.', 400)

        try:
            secret = self._kubernetes_backend.read_secret(secret_name)
        except KubernetesBackendKeyNotFoundError:
            return Response('Kubernetes secret not found.', 404)
        except KubernetesBackendError as error:
            self._logger.error('Unable to read Kubernetes secret.')
            self._logger.info(error)
            return Response('Unable to read Kubernetes secret.', 500)

        return Response(secret, 200)

    def put(self, secret_name):
        '''[summary]
        Update a secret in kubernetes
        [description]

        Arguments:
            secret_name {[type]} -- [description] Name of secret
        '''
        self._logger.info('App Secrets endpoint method PUT secret "%s" from %s', secret_name, request.remote_addr)

        json_body = request.json
        secret_value = json_body['value']

        if not secret_name or not secret_value:
            return Response('Unable to update Kubernetes secret, missing parameters.', 400)

        try:
            secret = self._kubernetes_backend.update_secret(secret_name)
        except KubernetesBackendKeyNotFoundError:
            return Response('Secret not found.', 404)
        except KubernetesBackendError as error:
            self._logger.error('Unable to update Kubernetes secret.')
            self._logger.info(error)
            return Response('Unable to update Kubernetes secret.', 500)

        return Response('Updated', 200)

    def delete(self, secret_name):
        '''[summary]
        Delete a secret from kubernetes
        [description]
        '''
        self._logger.info('App Secrets endpoint method DELETE secret "%s" from %s', secret_name, request.remote_addr)

        if not secret_name:
            return Response('Unable to delete Kubernetes secret, missing parameters.', 400)

        try:
            self._kubernetes_backend.delete_secret(secret_name)
        except KubernetesBackendError as error:
            self._logger.error('Unable to delete Kubernetes secret.')
            self._logger.info(error)
            return Response('Unable to delete Kubernetes secret.', 500)

        return Response('Deleted', 200)
