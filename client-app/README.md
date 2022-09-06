# flask-oidc-python-tests/client-app

Python Flask web app that serves as the "Client Application" entity in an OAuth2 Authorization Code flow.

blog: 

## Run using local Python

```
# need 3.x
python --version

# setup virtual env for pip modules
python -m venv .
source bin/activate
pip install -r requirements.txt

# your ADFS server
export ADFS=win2k19-adfs1.fabian.lee

# OAuth2 client, secret, scope
export ADFS_CLIENT_ID=<the oauth2 client id>
export ADFS_CLIENT_SECRET=<the oauth2 client secret>
export ADFS_SCOPE="openid allatclaims api_delete"

# add custom CA from ADFS server to CA filestore
# you must provide the 'myCA.pem' file
export ADFS_CA_PEM=$(cat myCA.pem | sed 's/\n/ /')
python src/add_ca.py3

# start on port 8080
python src/app.py
```

## Run using local Docker daemon

Image is based on python:3.9-slim-buster and is ~191Mb

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
docker rm docker-flask-oidc-client-app

# run docker image locally, listening on localhost:8080
docker run \
--network host \
-p 8080:8080 \
--name docker-flask-oidc-client-app \
-e ADFS_CLIENT_ID=$ADFS_CLIENT_ID \
-e ADFS_CLIENT_SECRET=$ADFS_CLIENT_SECRET \
-e ADFS=$ADFS \
-e ADFS_SCOPE="$ADFS_SCOPE" \
-e ADFS_CA_PEM="$ADFS_CA_PEM" \
fabianlee/docker-flask-oidc-client-app:1.0.0
```


## Notes

Had to lock pip module itsdangerous=2.0.1
https://github.com/puiterwijk/flask-oidc/issues/147
ImportError: cannot import name 'JSONWebSignatureSerializer' from 'itsdangerous'

Manual addition to local CA trust store
cat myCA.pem >> lib/python3.8/site-packages/certifi/cacert.pem

