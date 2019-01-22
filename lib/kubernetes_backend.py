import logging
import base64
import kubernetes.client
from kubernetes.client.rest import ApiException


class KubernetesBackendError(Exception):
    pass


class KubernetesBackend:
    # The Borg Singleton
    __shared_state = {}

    _api = None

    def __init__(self):

        # The Borg Singleton
        self.__dict__ = self.__shared_state

        if not self._api:
            self._logger = logging.getLogger('flask.app')

            self._logger.info('Initializing Kubernetes Client.')

            configuration = kubernetes.client.Configuration()
            api_client = kubernetes.client.ApiClient(configuration)
            self._api = kubernetes.client.CoreV1Api(api_client)

            if self._is_secret_initialized():
                self._logger.info('K8S Secret already initalized.')
            else:
                self._logger.info('Initializing K8S Secret.')

                self._init_secret()

                self._logger.info('K8S Secret initalized.')

    def _is_secret_initialized(self):
        self._get_secret()

        return True

    def _init_secret(self):
        secret = kubernetes.client.V1Secret()
        secret.api_version = 'v1'
        secret.metadata = kubernetes.client.V1ObjectMeta()
        secret.metadata.name = 'appSecret'

        try:
            api_response = self._api.create_namespaced_secret('default', secret)
        except ApiException as error:
            self._logger.error('Failed to initialize K8S Secret.')
            self._logger.info(error)

            raise KubernetesBackendError()

        self._logger.info(api_response.data)

    def _get_secret(self):
        try:
            secret = self._api.read_namespaced_secret('appSecret', 'default')
        except ApiException as error:
            self._logger.error('Failed to read K8S Secret.')
            self._logger.info(error)

            raise KubernetesBackendError()

        return secret

    def _put_secret(self, secret):
        try:
            self._api.replace_namespaced_secret('appSecret', 'default', secret)
        except ApiException as error:
            self._logger.error('Failed to update K8S Secret.')
            self._logger.info(error)

            raise KubernetesBackendError()

    def create_secret(self, name, value):
        secret = self._get_secret()

        secret.data[name] = base64.b64encode(value)

        self._put_secret(secret)

    def read_secret(self, name):
        secret = self._get_secret()

        # FIXME 404 vs 500

        return base64.b64decode(secret.data[name])

    def update_secret(self, name, value):
        self.create_secret(name, value)

    def delete_secret(self, name, value):
        secret = self._get_secret()

        try:
            del secret.data[name]
        except KeyError:
            pass

        self._put_secret(secret)
