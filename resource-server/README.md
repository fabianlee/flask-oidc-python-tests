# flask-oidc-python-tests/resource-server

Python Flask web app that serves as the "Resource Server" entity in an OAuth2 Authorization Code flow.

It exposes a protected microservice at port 8081 that accepts an OAuth2 Access Token for authorization.

* GET /api - test of authenticated user
* GET /api/managers - authenticated user who is member of 'managers' group

![OAuth2 entities and flow](https://raw.githubusercontent.com/fabianlee/oauth2-client-app-golang/main/diagrams/oauth2-oidc-entities.drawio.png)

## Env vars required for Keycloak

Configured per [my article on Keycloak setup]()

```
export AUTH_SERVER=keycloak.kubeadm.local
export AUTH_PROVIDER=keycloak

# add custom CA from Keycloak, otherwise CERTIFICATE_VERIFY_FAILED errors
export CA_PEM=$(cat kubeadmCA.pem | sed 's/\n/ /')
```

## Env vars required for ADFS

Configured per [my article on ADFS setup](https://fabianlee.org/2022/08/08/kvm-creating-a-windows2019-adfs-server-using-powershell/).

```
export AUTH_SERVER=win2k19-adfs1.fabian.lee
export AUTH_PROVIDER=adfs

# add custom CA from ADFS, otherwise CERTIFICATE_VERIFY_FAILED errors
export CA_PEM=$(cat adfsCA.pem | sed 's/\n/ /')
```

## Env vars required for Google

Configured per [my article on Google OAuth2 setup](https://fabianlee.org/2022/09/13/oauth2-configuring-google-for-oauth2-oidc/).

```
export AUTH_SERVER=accounts.google.com
export AUTH_PROVIDER=google

# no custom cert needed, it has a public CA
```

## Env vars required for okta

Configured per [my article on okta OAuth2 setup](https://fabianlee.org/2022/09/12/oauth2-configuring-okta-for-oauth2-oidc/).

```
export AUTH_SERVER=dev-xxxx.okta.com
export AUTH_PROVIDER=okta

# no custom cert needed, it has a public CA
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

# start Resource Server on port 8081, microservice at /api protected by OAuth2 Access Token
python src/app.py
```

## Run using local Docker daemon

```
docker --version

# clear out any older runs
docker rm docker-flask-oidc-resource-server

# run docker image locally, listening on localhost:8081
docker run \
--network host \
-p 8081:8081 \
--name docker-flask-oidc-resource-server \
-e AUTH_SERVER=$AUTH_SERVER \
-e AUTH_PROVIDER=$AUTH_PROVIDER \
-e CA_PEM="$CA_PEM" \
fabianlee/docker-flask-oidc-resource-server:1.0.0
```

## Testing JWT access token from command line

Assumes you have already set environment variables, and run add_ca.py3 which adds custom CA to trust store.

```
export JWT=<the access token>

# runs tests against /api and /api/managers using bearer token
./test-jwt-auth.sh
```



## Notes

Image is based on python:3.9-slim-buster and is ~152Mb

Had to lock pip module itsdangerous=2.0.1
https://github.com/puiterwijk/flask-oidc/issues/147
ImportError: cannot import name 'JSONWebSignatureSerializer' from 'itsdangerous'

Manual addition to local CA trust store
cat myCA.pem >> lib/python3.8/site-packages/certifi/cacert.pem

