FROM python:3-slim

COPY app /spm/app
COPY lib /spm/lib
COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN bash -c 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
RUN apt-get update
RUN apt-get install -y --allow-unauthenticated kubeadm curl
RUN rm -rf /var/lib/apt/lists/* /tmp/requirements.txt
WORKDIR /spm
CMD [ "gunicorn", "-b", "0.0.0.0:5003", "app:app"]
