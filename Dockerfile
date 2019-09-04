FROM python:3-slim

COPY app /spm/app
COPY bin /usr/local/bin
COPY lib /spm/lib
COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt
RUN pip install terminaltables
RUN apt-get update
RUN apt-get install -y apt-transport-https curl gnupg
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN bash -c 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
RUN apt-get update
RUN apt-get install -y --allow-unauthenticated kubeadm curl
RUN rm -rf /var/lib/apt/lists/* /tmp/requirements.txt
WORKDIR /spm
CMD [ "gunicorn", "-b", "0.0.0.0:5003", "app:app"]
HEALTHCHECK --interval=10s --timeout=2s --retries=50 CMD curl -f -X GET http://127.0.0.1:5003/v1.0/nodecerts/ca || exit 1
