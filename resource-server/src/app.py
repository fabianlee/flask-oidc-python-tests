#!/usr/bin/env python
#
# Flask app using flask_oidc to act as Resource Server (microservice)
# which receives Access Token in 'Authentication: Bearer' header
#

import os
import json
import io
import logging
import ssl
import sys
import certifi
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS

sys.path += ['flask-oidc/']
from flask_oidc import OpenIDConnect
import requests

# log level mutes every request going to stdout
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
app = Flask(__name__)

print(f'certifi = {certifi.where()}')

# Type of Authentication Server: generic|keycloak|adfs
AUTH_PROVIDER = os.getenv("AUTH_PROVIDER","generic")
print(f'AUTH_PROVIDER: {AUTH_PROVIDER}')

AUTH_SERVER = os.getenv("AUTH_SERVER","")
if len(AUTH_SERVER)<1:
  raise Exception("AUTH_SERVER is required environment variable")
print(f'AUTH_SERVER: {AUTH_SERVER}')

CLIENT_BASE_APP_URL = os.getenv("CLIENT_BASE_APP_URL","http://localhost:8080")
print(f'CLIENT_BASE_APP_URL: {CLIENT_BASE_APP_URL}')

# https://flask-cors.readthedocs.io/en/latest/
# https://flask-cors.corydolphin.com/en/latest/api.html
CORS_ORIGIN = os.getenv("CORS_ORIGIN",f'{CLIENT_BASE_APP_URL}')
cors = CORS(app, supports_credentials=True, allow_headers=["Authorization","WWW-Authenticate"], expose_headers=["WWW-Authenticate","Content-Type"], resources={ r"/api/*": {"origins": f'{CORS_ORIGIN}' } })


# dictionary that will agument app config
client_secrets_dict = { 
  "web": {
    "client_id": "",
    "client_secret": ""
  }
}
# app config
app.config.update({
    'OIDC_AUTH_PROVIDER': AUTH_PROVIDER,
    'OIDC_AUTH_SERVER': AUTH_SERVER,
    'DEBUG': True,
    'OIDC_RESOURCE_SERVER_ONLY': True,
    'SECRET_KEY': 'abc123!',
    'OIDC_CLIENT_SECRETS': client_secrets_dict
})

# specific to Keycloak
REALM = os.getenv("REALM","")
if "keycloak"==AUTH_SERVER and len(REALM)<1:
  raise Exception("Keycloak servers must have REALM set")
if len(REALM)>0:
  print(f'REALM: {REALM}')
  app.config.update({
    'OIDC_OPENID_REALM' : REALM
  })

oidc = OpenIDConnect(app, prepopulate_from_well_known_url=True)

@app.route('/')
def index():
    auth_header = find_the_attribute(request.headers, "", ['Authorization','authorization'])
    if len(auth_header)>0:
      greeting = f'Hello authenticated user! I see an "Authorization" request header'
    else:
      greeting = f'Hello anonymous user. There is no "Authorization" request header'
    return render_template('index.html', greeting=greeting,access_token=auth_header)

@app.route('/access_token')
@oidc.accept_token(require_token=False)
def access_token_notrequired():
    auth_header = find_the_attribute(request.headers, "",['Authorization','authorization'])
    return render_template('access_token.html', access_token=auth_header)

@app.route('/access_token_protected')
@oidc.accept_token(require_token=True)
def access_token_required():
    auth_header = find_the_attribute(request.headers, "",['Authorization','authorization'])
    return render_template('access_token.html', access_token=auth_header)


@app.route('/api', methods=['GET','POST'])
@oidc.accept_token(require_token=True, scopes_required=['openid'])
def hello_api():
    """OAuth 2.0 protected API endpoint accessible via AccessToken"""

    print("=== BEGIN ACCESS TOKEN =======================")
    print(g.oidc_token_info)
    print("=== END ACCESS TOKEN =========================")

    user = find_the_attribute(g.oidc_token_info,"",["email","upn","sub"])
    scope = find_the_attribute(g.oidc_token_info,"",["scp","scope"])
    data = {
      "hello": f"Welcome {user}",
      "my_scopes": f'{scope}'
    }
    return data

@app.route('/api/managers', methods=['GET','POST'])
@oidc.accept_token(require_token=True, scopes_required=['openid'], groups_required=['managers'])
def hello_manager():
    """OAuth 2.0 protected API endpoint accessible via AccessToken"""

    print("=== BEGIN ACCESS TOKEN =======================")
    print(g.oidc_token_info)
    print("=== END ACCESS TOKEN =========================")

    user = find_the_attribute(g.oidc_token_info,"",["email","upn","sub"])
    scope = find_the_attribute(g.oidc_token_info,"",["scp","scope"])
    group = find_the_attribute(g.oidc_token_info,"",["group","groups"])
    data = {
      "hello": user,
      "my_scopes": scope,
      "my_groups": group
    }
    return data

# since claims can be different between auth providers (scp versus scope) (group versus groups)
# have function find the preferred one that exists
def find_the_attribute(info,defaultValue,searchList):
    for item in searchList:
      try:
        if info.get(item):
          return info[item]
      except:
        pass
    return defaultValue


if __name__ == '__main__' or __name__ == "main":

    port = int(os.getenv("PORT", 8081))
    print("Starting web server on port {}".format(port))

    app.run(host='0.0.0.0', port=port)


