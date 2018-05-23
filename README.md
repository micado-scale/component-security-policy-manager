# component-security-policy-manager
v1.0:
- add docker secret
- provision the secret to application service
- the docker API create secret has error which is not resolved yet

How to use the API:
Example:
+ Create a docker secret named db_pass1 with value 123
curl -d "name=db_pass1&value=123" -X POST spm:5003/v1.0/create_secret
+ Add the existed secret dp_pass1 into the application service named app1
curl -d "secret=db_pass1&service=app1" -X POST spm:5003/v1.0/add_secret

