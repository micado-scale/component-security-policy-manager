import logging
import subprocess
from flask import Response
from flask_restful import Resource


class JoinTokens(Resource):
    def __init__(self):
        self._logger = logging.getLogger('flask.app')

    def post(self):
        '''[summary]
        Register a new worker node in Kubernetes.
        [description]
        A new join token is generated for the client and is returned along with the private key.
        '''
        self._logger.debug('Create join token endpoint called')

        try:
            res = subprocess.run(['kubeadm', 'token', 'create', '--print-join-command'], capture_output=True)
        except Exception as error:
            self._logger.error('Unable to call kubeadm.')
            self._logger.debug(error)
            return Response('Unable to generate Kubernetes token.', 500)

        return Response(res.stdout, 200)

    def delete(self, token):
        '''[summary]
        Delete a join token.
        [description]
        Deletes a join token from Kubernetes.

        Arguments:
            [type] string -- [description] client's join token
        '''
        self._logger.debug('Delete join token endpoint called')

        try:
            res = subprocess.run(['kubeadm', 'token', 'delete', token], capture_output=True)
        except Exception as error:
            self._logger.error('Unable to call kubeadm.')
            self._logger.debug(error)
            return Response('Unable to delete Kubernetes token.', 500)

        return Response(res.stdout, 200)
