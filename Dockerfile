FROM python:3-slim
ADD my_script.py /
ADD app /app
ADD resource.csv /
RUN easy_install pip
RUN pip install flask
RUN pip install flask_restful
RUN pip install docker
RUN pip install hvac
RUN pip install python-keycloak
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN bash -c 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
RUN apt-get update
RUN apt-get install -y --allow-unauthenticated kubeadm
RUN rm -rf /var/lib/apt/lists/*
CMD [ "python", "./my_script.py" ]
