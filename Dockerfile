FROM python:3
ADD app /app
ADD lib /lib
ADD requirements.txt /
ADD security_policy_manager.py /
ADD secretvaultmessages.json /
RUN pip install -r requirements.txt
CMD [ "python", "./security_policy_manager.py" ]
