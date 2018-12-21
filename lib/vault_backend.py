import logging
import requests
from hvac import Client


# "http://127.0.0.1:5003" for localhost test,
# "http://spm:5003" for docker environment
# SPM_URL = "http://spm:5003"
SPM_URL = "http://127.0.0.1:5003"

# "http://127.0.0.1:8200" for localhost test,
# "http://credstore:8200" for docker environment
# VAULT_URL = "http://credstore:8200"
VAULT_URL = "http://127.0.0.1:8200"

# Number of generated unseal keys
VAULT_SHARES = 1

# Minimum number of keys needed to unseal the vault
VAULT_THRESHOLD = 1

# File to store vault token
VAULT_TOKEN_FILE = 'vaulttoken'

# File to store keys to unseal the vault
UNSEAL_KEYS_FILE = 'unsealkeys'


class VaultBackendError(Exception):
    pass


class VaultBackend:
    # The Borg Singleton
    __shared_state = {}

    client = None

    def __init__(self):
        '''[summary]
        Initializes and unseals the Vault
        [description]
        Initializes the Vault, if it has not been initialized yet and unseals it.
        '''
        # The Borg Singleton
        self.__dict__ = self.__shared_state

        if not self.client:
            self._logger = logging.getLogger('flask.app')

            self._logger.debug('Initializing Vault.')

            self.client = Client(url=VAULT_URL)

            if self._is_vault_initialized():
                self._logger.debug('Vault already initalized.')

                self._load_keys()
            else:
                vault = self._init_vault()
                self._token = vault['root_token']
                self._unseal_keys = vault['keys']

                self._logger.debug('Vault initalized.')

                self._save_keys()

            self.client.token = self._token

            self._logger.debug('Unsealing Vault.')

            self._unseal_vault()

            self._logger.debug('Vault unsealed.')

    def _load_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'r', encoding='utf-8') as token_file:
                self._token = token_file.read()
        except IOError as error:
            self._logger.error('Failed to read Vault token. Will not unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'r', encoding='utf-8') as unseal_keys_file:
                self._unseal_keys = unseal_keys_file.read().splitlines()
        except IOError as error:
            self._logger.error('Failed to read Vault unseal keys. Will not unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _save_keys(self):
        try:
            with open(VAULT_TOKEN_FILE, 'w', encoding='utf-8') as token_file:
                token_file.write(self._token)
        except IOError as error:
            self._logger.error('Failed to write Vault token to file. Will not be able to reconnect.')
            self._logger.debug(error)
            raise VaultBackendError()

        try:
            with open(UNSEAL_KEYS_FILE, 'w', encoding='utf-8') as unseal_keys_file:
                for key in self._unseal_keys:
                    unseal_keys_file.write("%s\n" % key)
        except IOError as error:
            self._logger.error('Failed to write Vault unseal keys to file. Will not be able to reconnect.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _is_vault_initialized(self):
        try:
            return self.client.sys.is_initialized()
        except Exception as error:
            self._logger.error('Failed to check if Vault is initialized.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _init_vault(self):
        try:
            return self.client.sys.initialize(VAULT_SHARES, VAULT_THRESHOLD)
        except Exception as error:
            self._logger.error('Failed to initialize Vault.')
            self._logger.debug(error)
            raise VaultBackendError()

    def _unseal_vault(self):
        try:
            self.client.sys.submit_unseal_keys(self._unseal_keys)
        except Exception as error:
            self._logger.error('Failed to unseal Vault.')
            self._logger.debug(error)
            raise VaultBackendError()


class VaultPkiBackend:
    # The Borg Singleton
    __shared_state = {}

    _vault_backend = None

    def __init__(self, ):
        # The Borg Singleton
        self.__dict__ = self.__shared_state

        if not self._vault_backend:
            # this takes care of initialization, getting and the token unsealing
            self._vault_backend = VaultBackend()

            self._logger = logging.getLogger('flask.app')

            self._init_pki()

    def get(self, path):
        return requests.get(VAULT_URL + path, headers={'X-Vault-Token': self._vault_backend._token})

    def getAnonymous(self, path):
        return requests.get(VAULT_URL + path)

    def post(self, path, payload=None):
        return requests.post(VAULT_URL + path, headers={'X-Vault-Token': self._vault_backend._token}, json=payload)

    def list(self, path):
        return requests.request('LIST', VAULT_URL + path, headers={'X-Vault-Token': self._vault_backend._token})

    def _init_pki(self):
        self._logger.debug('Initializing Vault PKI backend.')

        try:
            if self._mount_pki_backend():
                self._generate_root_ca()
                self._set_urls()
                self._create_role()
            else:
                self._logger.debug('Vault PKI backend already initialized.')
        except Exception as error:
            self._logger.error('Failed to initialize Vault PKI backend.')
            self._logger.debug(error)

            raise VaultBackendError()

    def _mount_pki_backend(self):
        self._logger.debug('Enabling Vault PKI Secrets backend.')

        params = {
            'type': 'pki',
            'config': {
                'default_lease_ttl': '8760h',
                'max_lease_ttl': '43830h'
            }
        }

        resp = self.post('/v1/sys/mounts/pki', params)

        self._logger.debug('HTTP %s: %s', resp.status_code, resp.text)

        if resp.status_code == 204:
            return True
        elif resp.status_code == 400:
            return False
        else:
            raise VaultBackendError()

    def _generate_root_ca(self):
        self._logger.debug('Generating root CA.')

        params = {
            'common_name': 'micado',
            'ttl': '43830h'
        }

        resp = self.post('/v1/pki/root/generate/internal', params)

        self._logger.debug('HTTP %s: %s', resp.status_code, resp.text)

        if resp.status_code != 200:
            raise VaultBackendError()

    def _set_urls(self):
        self._logger.debug('Updating distribution URL\'s.')

        params = {
            'issuing_certificates': SPM_URL + '/v1.0/nodecerts/ca',
            'crl_distribution_points': SPM_URL + '/v1.0/nodecrl'
        }

        resp = self.post('/v1/pki/config/urls', params)

        self._logger.debug('HTTP %s: %s', resp.status_code, resp.text)

        if resp.status_code != 204:
            raise VaultBackendError()

    def _create_role(self):
        self._logger.debug('Creating role for signing.')

        params = {
            'allowed_domains': ['micado'],
            'allow_subdomains': 'true',
            'max_ttl': '8760h'
        }

        resp = self.post('/v1/pki/roles/micado', params)

        self._logger.debug('HTTP %s: %s', resp.status_code, resp.text)

        if resp.status_code != 204:
            raise VaultBackendError()
