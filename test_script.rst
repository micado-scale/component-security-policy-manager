.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/CredStoreLibrary.py

	*** Test Cases *** 	
	Admin cannot initialize a vault with unsatisfied parameters
		Init vault     ${shares}   ${invalid_threshold}
		Status should be 	${http_code_bad_request}

	Admin can initialize a vault
		Init vault     ${shares}   ${threshold}
		Status should be 	${http_code_created}

	Admin can add a secret
		Add secret   ${secretname}    ${secretvalue}
		Status should be    ${http_code_created}

	Admin can read a secret
		Read secret    ${secretname}
		Status should be    ${http_code_ok}
		Data should be    ${secretvalue}

	Admin can update a secret
		Update secret    ${secretname}    ${new_secretvalue}
		Status should be    ${http_code_ok}
		Read secret    ${secretname}
		Status should be    ${http_code_ok}
		Data should be    ${new_secretvalue}

	Admin can delete a secret
		Delete secret    ${secret_name}
		Status should be    ${http_code_ok}

	Admin cannot read the deleted secret
		Read secret    ${secret_name}	
		Status should be    ${http_code_not_found}

	Admin cannot add a secret with empty name
		Add secret   ${EMPTY}    ${secretvalue}
		Status should be    ${http_code_bad_request}

	Admin cannot add a secret with empty secret
		Add secret   ${secretname}    ${EMPTY}
		Status should be    ${http_code_bad_request}

	Admin can add an application secret into docker services
		Add application secret    ${appsecret_name}     ${appsecret_value}    ${servicename}
		Status should be    ${http_code_created}

	Admin can retrieve secret_id after the secret is created
		Retrieve application secret id   ${appsecret_name}
		Status should be    ${http_code_ok} 

	Admin can delete an application secret from docker services
		Delete application secret    ${appsecret_name}     ${servicename}
		Status should be    ${http_code_ok}

	Admin cannot retrieve secret_id after the secret is deleted
		Retrieve application secret id    ${appsecret_name}
		Status should be    ${http_code_bad_request} 

	*** Variables ***
	${secretname}               secret1
	${secretvalue}              123
	${new_secretvalue}          456
	${http_code_ok}              200
	${http_code_not_found}       404
	${http_code_created}		 201
	${http_code_bad_request}	 400
	${shares}					 3
	${threshold}				 2
	${invalid_threshold}		 0

	${appsecret_name}            appsecret7
	${appsecret_value}            123
	${servicename}               app1

	*** Keywords ***
	Add secret
		[Arguments]    ${name}    ${value}
		add_a_secret    ${name}    ${value}

	Read secret
		[Arguments]    ${secretname}
		read_a_secret    ${secretname}

	Update secret    
		[Arguments]    ${name}    ${newvalue}
		update_a_secret    ${name}    ${newvalue}

	Delete secret
		[Arguments]    ${secretname}
		delete_a_secret    ${secretname}

	Init vault
		[Arguments]    ${shares}   ${threshold}
		init_a_vault     ${shares}   ${threshold} 

	Add application secret
		[Arguments]    ${name}    ${value}   ${service}
		create_app_secret    ${name}    ${value}    ${service}

	Delete application secret
		[Arguments]    ${name}    ${service}
		delete_app_secret    ${name}    ${service}

	Retrieve application secret id
		[Arguments]    ${name}
		retrieve_app_secret_id    ${name}
