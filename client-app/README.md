# flask-oidc-python-tests/client-app

Python Flask web app that serves as the "Client Application" entity in an OAuth2 Authorization Code flow.

It orchestrates authentication with the ADFS server, and receives a callback with token which is exchanged for ID and Access Token.

## Env vars required for Keycloak

Configured per (my article on Keycloak setup)[]

```
export AUTH_SERVER=keycloak.kubeadm.local
export AUTH_PROVIDER=keycloak
export CLIENT_ID=<the oauth2 client id>
export CLIENT_SECRET=<the oauth2 client secret>
export SCOPE=openid email profile

export REALM=myrealm

# add custom CA from Keycloak, otherwise CERTIFICATE_VERIFY_FAILED errors
export CA_PEM=$(cat kubeadmCA.pem | sed 's/\n/ /')
```

## Env vars required for ADFS

Configured per (my article on ADFS setup)[https://fabianlee.org/2022/08/08/kvm-creating-a-windows2019-adfs-server-using-powershell/].

```
export AUTH_SERVER=win2k19-adfs1.fabian.lee
export AUTH_PROVIDER=adfs
export CLIENT_ID=<the oauth2 client id>
export CLIENT_SECRET=<the oauth2 client secret>
export SCOPE=openid allatclaims

# matches 'Redirect URI' from ADFS server app
export CALLBACK_ROUTE=/login/oauth2/code/adfs

# add custom CA from ADFS, otherwise CERTIFICATE_VERIFY_FAILED errors
export CA_PEM=$(cat adfsCA.pem | sed 's/\n/ /')
```

## Run using local Python

```
# need 3.x
python --version

# make sure Python3 and other essential OS packages are installed
sudo apt-get update
sudo apt-get install software-properties-common python3 python3-dev python3-pip python3-venv make curl git -y

# get my enhanced fork of flask-oidc
git clone https://github.com/fabianlee/flask-oidc.git

# setup virtual env for pip modules
python -m venv .
source bin/activate
pip install -r requirements.txt

# add custom CA certificate from 'CA_PEM' to trust store file
python src/add_ca.py3

# start OAuth2 Client App on port 8080
python src/app.py
```

## Run using local Docker daemon

Same environment variables from above need to be exported.

```
docker --version

# clear out any older runs
docker rm docker-flask-oidc-client-app

# run docker image locally, listening on localhost:8080
docker run \
--network host \
-p 8080:8080 \
--name docker-flask-oidc-client-app \
-e AUTH_SERVER=$AUTH_SERVER \
-e AUTH_PROVIDER=$AUTH_PROVIDER \
-e CLIENT_ID=$CLIENT_ID \
-e CLIENT_SECRET=$CLIENT_SECRET \
-e SCOPE="$SCOPE" \
-e REALM="$REALM" \
-e CALLBACK_ROUTE="$CALLBACK_ROUTE" \
-e CA_PEM="$CA_PEM" \
fabianlee/docker-flask-oidc-client-app:1.0.0
```


## Notes

Image is based on python:3.9-slim-buster and is ~191Mb

Had to lock pip module itsdangerous=2.0.1
https://github.com/puiterwijk/flask-oidc/issues/147
ImportError: cannot import name 'JSONWebSignatureSerializer' from 'itsdangerous'

Manual addition to local CA trust store
cat myCA.pem >> lib/python3.8/site-packages/certifi/cacert.pem

