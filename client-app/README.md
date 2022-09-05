# Summary
Python flask web server running by default on port 8000 that is intended for testing containers, especially from Kubernetes

Image is based on python:3.9-slim-buster and is ~130Mb

# Environment variables

* PORT - listen port, defaults to 8000
* APP_CONTEXT - base context path of app, defaults to '/'

# Environment variables populated from Downward API
* MY_NODE_NAME - name of k8s node
* MY_POD_NAME - name of k8s pod
* MY_POD_IP - k8s pod IP
* MY_POD_SERVICE_ACCOUNT - service account of k8s pod

# Prerequisites
* make utility (sudo apt-get install make)

# Makefile targets
* docker-build (builds image)
* docker-run-fg (runs container in foreground, ctrl-C to exit)
* docker-run-bg (runs container in background)
* k8s-apply (applies deployment to kubernetes cluster)
* k8s-delete (removes deployment on kubernetes cluster)

# getting packages correct
# https://github.com/puiterwijk/flask-oidc/issues/147
ImportError: cannot import name 'JSONWebSignatureSerializer' from 'itsdangerous'
Until locking itsdangerous=2.0.1

# avoid https verification error by adding cert to truststore
cat win2k19-adfs1.fabian.lee.pem >> lib/python3.8/site-packages/certifi/cacert.pem

export ADFS_CA_PEM=$(cat myCA.pem | sed 's/\n/ /')
