## flask-oidc-python-tests

Python Flask implementation of OAuth2 Client App and Resource Server entities using [enhanced fork of flask-oidc](https://github.com/fabianlee/flask-oidc).

* [Client Application, web app running on port 8080](client-app/README.md)
* [Resource Server, microservice running on port 8081](resource-server/README.md)

![OAuth2 entities and flow](https://raw.githubusercontent.com/fabianlee/oauth2-client-app-golang/main/diagrams/oauth2-oidc-entities.drawio.png)

### Tested on OAuth2+OIDC Authentication Servers

* [Windows 2019 ADFS](https://fabianlee.org/2022/08/22/microsoft-configuring-an-application-group-for-oauth2-oidc-on-adfs-2019/)
* [Keycloak 19.01 on Kubernetes](https://fabianlee.org/2022/09/10/kubernetes-keycloak-iam-deployed-into-kubernetes-cluster-for-oauth2-oidc/)
* [Google OAuth2](https://fabianlee.org/2022/09/13/oauth2-configuring-google-for-oauth2-oidc/)
* [okta](https://fabianlee.org/2022/09/12/oauth2-configuring-okta-for-oauth2-oidc/)

### Components

* Python 3.8.10
* Docker 20.10.6
* [Flask-OIDC personal fork, enhanced](https://github.com/fabianlee/flask-oidc)

### My related blog articles

* [Flask-OIDC with Windows 2019 ADFS Authentication Server](https://fabianlee.org/2022/09/06/python-flask-oidc-protecting-client-app-and-resource-server-using-windows-2019-adfs/)


