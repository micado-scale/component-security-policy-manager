<<<<<<< HEAD
# component-security-policy-manager
v1.0:

Docker secret:

- add docker secret
- provision the secret to application service
- the docker API create secret has error which is not resolved yet

Infrastructure secrets:

- Initialize a vault to store secrets for the infrastructure
- Create a secret
- Read a secret
- Delete a secret

How to use the API:

Example:


With docker secrets

+ Create a docker secret named db_pass1 with value 123:

curl -d "name=db_pass1&value=123" -X POST spm:5003/v1.0/create_secret

+ Add the existed secret dp_pass1 into the application service named app1:

curl -d "secret=db_pass1&service=app1" -X POST spm:5003/v1.0/add_secret


With hashicorp vault

+ Initialize a vault to store secrets

curl -d "shares=3&threshold=2" -X POST spm:5003/v1.0/vault

+ Add a secret 'secret1' into the initialized vault

curl -d "name=secret1&value=123" -X POST spm:5003/v1.0/secrets

+ Read a secret named 'secret1' from the vault

curl -d "name=secret1" -X GET spm:5003/v1.0/secrets

+ Delete a secret named 'secret1' from the vault

curl -d "name=secret1" -X PUT spm:5003/v1.0/secrets
=======
# Component OIDC Client
Requirement: install python-keycloak, flask, flask_restful
> sudo su

> pip install python-keycloak flask flask_restful

How to use APIs:
- Get user information

http://[IP address of OIDC client]:5001/v1.0/userinfo?token=[access_token] (GET)

- Verify access token and get its information (Instropect)

http://[IP address of OIDC client]:5001/v1.0/tokens?token=[access_token] (GET)

- Refresh tokens

http://[IP address of OIDC client]:5001/v1.0/tokens?token=[refresh_token] (PUT)

- Log out

http://[IP address of OIDC client]:5001/v1.0/tokens?token=[refresh_token] (DELETE)

- Retrieve tokens from username and password

http://[IP address of OIDC client]:5001/v1.0/alltokens?username=[username]&password=[password] (GET)
>>>>>>> 5644cb4b55e39da905113968aab56182547ff1a5
