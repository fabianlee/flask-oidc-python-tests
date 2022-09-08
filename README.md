## flask-oidc-python-tests

blog: https://fabianlee.org/2022/09/06/python-flask-oidc-protecting-client-app-and-resource-server-using-windows-2019-adfs/

Python Flask implementation of OAuth2 Client App and Resource Server entities using [enhanced fork of flask-oidc](https://github.com/fabianlee/flask-oidc).

* [Client Application, web app running on port 8080](client-app/README.md)
* [Resource Server, microservice running on port 8081](resource-server/README.md)

## Components

* Python 3.8.10
* Docker 20.10.6
* [Flask-OIDC personal fork, augmented for ADFS](https://github.com/fabianlee/flask-oidc)


## Tested on OAuth2 Authentication Servers

* [Windows 2019 ADFS](https://fabianlee.org/2022/08/22/microsoft-configuring-an-application-group-for-oauth2-oidc-on-adfs-2019/)
* [Keycloak 19.01 on Kubernetes](https://www.keycloak.org/getting-started/getting-started-kube)
