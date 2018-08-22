# Component OIDC Client
Requirement: install python-keycloak, flask, flask_restful
> sudo su

> pip install python-keycloak flask flask_restful

How to use APIs:
- Get user information

http://[IP address of OIDC client]/v1.0/userinfo?token=[access_token] (GET)

- Verify access token and get its information (Instropect)

http://[IP address of OIDC client]/v1.0/tokens?token=[access_token] (GET)

- Refresh tokens

http://[IP address of OIDC client]/v1.0/tokens?token=[refresh_token] (PUT)

- Log out

http://[IP address of OIDC client]/v1.0/tokens?token=[refresh_token] (DELETE)

- Retrieve tokens from username and password

http://[IP address of OIDC client]/v1.0/alltokens?username=[username]&password=[password] (GET)