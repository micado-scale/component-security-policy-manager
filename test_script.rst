.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/CredStoreLibrary.py

	*** Test Cases *** 				
	Print hello 					
		print_hello
		Status should be	${http_code_ok}

	User can add a secret
		Add secret   ${secretname}    ${secretvalue}
		Status should be    ${http_code_ok}

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

	*** Variables ***
	${secretname}               secret1
	${secretvalue}              123
	${http_code_ok}              200
	${http_code_not_found}       404

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