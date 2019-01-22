import logging
from flask import request
from flask import Response
from flask_restful import Resource
from lib.kubernetes_backend import KubernetesBackend, KubernetesBackendError


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
            self._logger.debug(error)
            return Response('Unable to create Kubernetes secret.', 500)

        return Response('Created', 201)

    # def delete(self, token):
    #     '''[summary]
    #     Delete a join token.
    #     [description]
    #     Deletes a join token from Kubernetes.

    #     Arguments:
    #         [type] string -- [description] client's join token
    #     '''
    #     self._logger.info('Join Tokens endpoint method DELETE token %s from %s', token, request.remote_addr)

    #     try:
    #         res = subprocess.run(['kubeadm', 'token', 'delete', token], capture_output=True)
    #     except Exception as error:
    #         self._logger.error('Unable to call kubeadm.')
    #         self._logger.debug(error)
    #         return Response('Unable to delete Kubernetes token.', 500)

    #     return Response(res.stdout, 200)
