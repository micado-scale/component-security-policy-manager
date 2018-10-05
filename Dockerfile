FROM python:3
ADD my_script.py /
ADD app /app
ADD resource.csv /
RUN easy_install pip
RUN pip install flask
RUN pip install flask_restful
RUN pip install docker
RUN pip install hvac
CMD [ "python", "./my_script.py" ]
