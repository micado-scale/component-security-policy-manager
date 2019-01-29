# Component-security-policy-manager
v2.0:

## Overview: 

This module provides APIs to manage sensitive information, including application sensitive information and infrastructure sensitive information.

### Infrastructure sensitive information or infrastructure secret:

+ Create,
+ Read,
+ Update or
+ Delete a secret in Hashicorp Vault

### Application sensitive information or application secret:

+ Create,
+ Read,
+ Update or
+ Delete an application secret in kubernetes

### Worker node IPsec certificates:

+ Create,
+ Read or
+ Revoke a certificate,
+ Get Certificate Revocation List

### Worker node kubernetes join tokens:

+ Create or
+ Invalidate a join token

### Security Enablers:

+ Crypto Engine
+ Image Integrity Verifier

## How to use the API:

### Infrastructure sensitive information or infrastructure secret

+ Add a secret 'secret1' into the vault. If the secret exists, it will be overwritten.

```curl -H "Content-Type: application/json" -d '{"name":"secret1","value":"123"}' -X POST spm:5003/v1.0/secrets```

+ Update the secret named 'secret1' with a new value

```curl -H "Content-Type: application/json" -d '{"value":"456"}' -X PUT spm:5003/v1.0/secrets/secret1```

+ Read a secret named 'secret1' from the vault

```curl -X GET spm:5003/v1.0/secrets/secret1```

+ Delete a secret named 'secret1' from the vault

```curl -X DELETE spm:5003/v1.0/secrets/secret1```

### Application sensitive information or application secret

+ Add an applicaton sensitive information as kubernetes secret and distribute it to pods. If the application service has existing secrets, this function add one more while keeping the other secrets intact.

```curl -H "Content-Type: application/json" -d '{"name":"secret1","value":"123"}' -X POST spm:5003/v1.0/appsecrets```

+ Retrieve kubernetes secret with id 'secret1'

```curl -X GET spm:5003/v1.0/appsecrets/secret1```

+ Remove a secret named 'secret1' from the service

```curl -X DELETE spm:5003/v1.0/appsecrets/secret1```

## How to use the automatic test script for managing secrets infrastructure sensitive information:

Assuming that you installed Robot framework successfully (Please follow this link if you has not installed the Robot framework yet: https://github.com/robotframework/QuickStartGuide/blob/master/QuickStart.rst#demo-application)

1. Launch the vault server in localhost:

  * Download the vault server from https://www.vaultproject.io/downloads.html

  * Create a config file named vault.hcl with the below content:

```
storage "file" {
	path = "datafile"
}
listener "tcp" {
	address     = "127.0.0.1:8200"
	tls_disable = 1
}
```

(all secrets will be written in the file 'datafile' which resides in the same directory with the executable file 'vault')

  * Launch the vault server by command line

```./vault server -config=vault.hcl```

2. Edit the file app/vaultclient.py to change VAULT_URL into

```VAULT_URL = "http://127.0.0.1:8200"```

3. Run the source code by command line

```gunicorn -b 0.0.0.0:5003 app:app```

4. Run the test script by command line

```robot test/test_script.rst```
