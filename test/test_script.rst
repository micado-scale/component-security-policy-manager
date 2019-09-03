.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     CredStoreLibrary.py

	*** Test Cases *** 	
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

	Admin can get the certification authority
		Get certification authority
		Status should be    ${http_code_ok}
                Data should not be empty

	Admin can get a certificate
		Get a certificate   ${EMPTY}
		Status should be    ${http_code_ok}
                Data should not be empty

	Admin can get a named certificate
		Get a certificate   ${secretname}
		Status should be    ${http_code_ok}
                Data should not be empty

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

        Get certification authority
		get_the_certification_authority

        Get a certificate
		[Arguments]    ${cert_common_name}
		create_a_certificate    ${cert_common_name}
               
