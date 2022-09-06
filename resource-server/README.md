# flask-oidc-python-tests/resource-server

Python Flask web app that serves as the "Resource Server" entity in an OAuth2 Authorization Code flow.

It exposes a protected microservice at ":8081/api" that accepts an OAuth2 Access Token for authorization.

blog: 

## Run using local Python

```
# need 3.x
python --version

# make sure Python3 and other essential OS packages are installed
sudo apt-get update
sudo apt-get install software-properties-common python3 python3-dev python3-pip python3-venv make curl git -y

# setup virtual env for pip modules
python -m venv .
source bin/activate
pip install -r requirements.txt

# your ADFS server
export ADFS=win2k19-adfs1.fabian.lee

# add custom CA from ADFS server to CA filestore
# you must provide the 'myCA.pem' file
export ADFS_CA_PEM=$(cat myCA.pem | sed 's/\n/ /')
python src/add_ca.py3

# start on port 8080
python src/app.py
```

## Run using local Docker daemon

Image is based on python:3.9-slim-buster and is ~152Mb

```
docker --version

# your ADFS server
export ADFS=win2k19-adfs1.fabian.lee

# OAuth2 client, secret, scope
export ADFS_CLIENT_ID=<the oauth2 client id>
export ADFS_CLIENT_SECRET=<the oauth2 client secret>
export ADFS_SCOPE="openid allatclaims api_delete"

# add custom CA from ADFS server to CA filestore
# you must provide the 'myCA.pem' file
export ADFS_CA_PEM=$(cat myCA.pem | sed 's/\n/ /')

# clear out any older runs
docker rm docker-flask-oidc-resource-server

# run docker image locally, listening on localhost:8080
docker run \
--network host \
-p 8080:8080 \
--name docker-flask-oidc-resource-server \
-e ADFS_CLIENT_ID=$ADFS_CLIENT_ID \
-e ADFS_CLIENT_SECRET=$ADFS_CLIENT_SECRET \
-e ADFS=$ADFS \
-e ADFS_SCOPE="$ADFS_SCOPE" \
-e ADFS_CA_PEM="$ADFS_CA_PEM" \
fabianlee/docker-flask-oidc-resource-server:1.0.0
```


## Notes

Had to lock pip module itsdangerous=2.0.1
https://github.com/puiterwijk/flask-oidc/issues/147
ImportError: cannot import name 'JSONWebSignatureSerializer' from 'itsdangerous'

Manual addition to local CA trust store
cat myCA.pem >> lib/python3.8/site-packages/certifi/cacert.pem

