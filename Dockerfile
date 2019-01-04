FROM python:3-slim

ADD app /app
ADD lib /lib
ADD requirements.txt /
ADD security_policy_manager.py /
ADD lib/secretvaultmessages.json /

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN bash -c 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
RUN apt-get update
RUN apt-get install -y --allow-unauthenticated kubeadm curl
RUN rm -rf /var/lib/apt/lists/*

CMD [ "python", "./security_policy_manager.py" ]

