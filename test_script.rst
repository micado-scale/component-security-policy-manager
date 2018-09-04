.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/CredStoreLibrary.py

	*** Test Cases *** 				
	User can add a secret
		Add secret   ${secretname}    ${secretvalue}
		Status should be    ${http_code_created}

	User can read a secret
		Read secret    ${secretname}
		Status should be    ${http_code_ok}
		Data should be    ${secretvalue}

	User can delete a secret
		Delete secret    ${secret_name}
		Status should be    ${http_code_ok}

	User cannot read the deleted secret
		Read secret    ${secret_name}	
		Status should be    ${http_code_not_found}

	User cannot add a secret with empty name
		Add secret   ${EMPTY}    ${secretvalue}
		Status should be    ${http_code_bad_request}

	User cannot add a secret with empty secret
		Add secret   ${secretname}    ${EMPTY}
		Status should be    ${http_code_bad_request}

	*** Variables ***
	${secretname}               secret1
	${secretvalue}              123
	${http_code_ok}              200
	${http_code_not_found}       404
	${http_code_created}		 201
	${http_code_bad_request}	 400

	*** Keywords ***
	Add secret
		[Arguments]    ${name}    ${value}
		add_a_secret    ${name}    ${value}

	Read secret
		[Arguments]    ${secretname}
		read_a_secret    ${secretname}

	Delete secret
		[Arguments]    ${secretname}
		delete_a_secret    ${secretname}