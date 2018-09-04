# Component-security-policy-manager
v1.0:

# Overview: 

This module provides APIs to manage sensitive information, including application sensitive information and infrastructure sensitive information.

##Application sensitive information or secret:

+ Add application sensitive information as docker secret
+ Provision the secret to application services in worker nodes

##Infrastructure sensitive information or secret:

+ Initialize a vault to store secrets for the infrastructure
+ Create or update a secret
+ Read a secret
+ Delete a secret

# How to use the API:

## Application sensitive information or secret

+ Add an applicaton sensitive information as docker secret and distribute it to containers of the application app1:

curl -d "secret_name=db_pass1&secret_value=123&service=app1" -X POST spm:5003/v1.0/add_secret


## Infrastructure sensitive information or secret

+ Initialize a vault to store secrets

curl -d "shares=3&threshold=2" -X POST spm:5003/v1.0/vault

(Shares must be equal or larger than threshold. If shares > 1, threshold must be larger than 1)

+ Add a secret 'secret1' into the initialized vault

curl -d "name=secret1&value=123" -X POST spm:5003/v1.0/secrets

+ Update the secret named 'secret1' with a new value

curl -d "name=secret1&value=456" -X POST spm:5003/v1.0/secrets

+ Read a secret named 'secret1' from the vault

curl -d "name=secret1" -X GET spm:5003/v1.0/secrets

+ Delete a secret named 'secret1' from the vault

curl -d "name=secret1" -X DELETE spm:5003/v1.0/secrets


# How to use the automatic test script:

Assuming that you installed Robot framework successfully (Please follow this link if you has not installed the Robot framework yet: https://github.com/robotframework/QuickStartGuide/blob/master/QuickStart.rst#demo-application)

Run the following command line

+ robot test_script.rst
