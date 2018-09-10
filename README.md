# Component-security-policy-manager
v1.0:

## Overview: 

This module provides APIs to manage sensitive information, including application sensitive information and infrastructure sensitive information.

### Infrastructure sensitive information or infrastructure secret:

+ Initialize a vault to store secrets for the infrastructure
+ Create or update a secret
+ Read a secret
+ Delete a secret

### Application sensitive information or application secret:

+ Add application sensitive information as docker secret
+ Provision the secret to application services in worker nodes

## How to use the API:

### Infrastructure sensitive information or infrastructure secret

+ Initialize a vault to store secrets

```curl -d "shares=3&threshold=2" -X POST spm:5003/v1.0/vault```

(Shares must be equal or larger than threshold. If shares > 1, threshold must be larger than 1)

+ Add a secret 'secret1' into the initialized vault. If the secret exists, it will be overwritten.

```curl -d "name=secret1&value=123" -X POST spm:5003/v1.0/secrets```

+ Update the secret named 'secret1' with a new value

```curl -d "name=secret1&value=456" -X PUT spm:5003/v1.0/secrets```

+ Read a secret named 'secret1' from the vault

```curl -d "name=secret1" -X GET spm:5003/v1.0/secrets```

+ Delete a secret named 'secret1' from the vault

```curl -d "name=secret1" -X DELETE spm:5003/v1.0/secrets```

### Application sensitive information or application secret

+ Assuming that a service named 'app1' is already created

+ Add an applicaton sensitive information as docker secret and distribute it to containers of the application app1 (If the application service has existing secrets, this function add one more while keeping the other secrets intact):

```curl -d "secret_name=db_pass1&secret_value=123&service=app1" -X POST spm:5003/v1.0/appsecrets```

+ Verify if the secret is added to the service or not by calling the below command line in the master node

```docker service inspect app1```

You shall see something like this:
	
```
Spec": {
	"TaskTemplate": { 
        "ContainerSpec": {
            "Secrets": [
            {
                "File": {
                    "Name": "secret1",
                },
                "SecretID":,
                "SecretName": "secret1"
	        },
            ...
```

## How to use command line in the master node

### Infrastructure sensitive information or infrastructure secret
+ Initialize a vault to store secrets with shares = 2, threshold = 2

```micadoctl.sh initvault 2 2```

+ Add a secret 'secret1' with value 123 into the initialized vault. If the secret exists, it will be overwritten.

```micadoctl.sh addsecret secret1 123```

+ Read a secret named 'secret1' from the vault

```micadoctl.sh readsecret secret1```

+ Delete a secret named 'secret1' from the vault

```micadoctl.sh removesecret secret1```

### Application sensitive information or application secret

+ Add a secret 'secret1' with value 123 in docker secrets and provision it to the service 'app1' (assuming that the service 'app1' is deployed already)

```micadoctl.sh addappsecret secret1 123 app1```

+ Check if 'secret1' is provisioned to 'app1' or not

```docker service inspect app1```

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

```python my_script.py```

4. Run the test script by command line

```robot test_script.rst```
