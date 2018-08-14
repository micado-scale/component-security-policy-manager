.. default-role:: code
.. code:: robotframework

	*** Settings *** 				
	Library     lib/LoginLibrary.py

	*** Test Cases *** 				
	Print hello 					
		print_hello
		Status should be	${http_code_ok}

	User can add a secret
		add_secret   ${secretname}    ${secretvalue}
		Status should be    ${http_code_ok}

	User can read a secret
		read_secret    ${secret_name}
		Status should be    ${http_code_ok}

	User can delete a secret
		delete_secret    ${secret_name}
		Status should be    ${http_code_ok}

	*** Variables ***
	${secretname}               'secret1'
	${secretvalue}              '123'
	${http_code_ok}              200

	*** Keywords ***