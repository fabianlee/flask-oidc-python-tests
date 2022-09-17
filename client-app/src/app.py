#!/usr/bin/env python
#
# Flask application using flask_oidc to act as Client Application (web app)
#

import os
import json
import io
import logging
import ssl
import sys
import certifi
import httplib2
import datetime
from werkzeug.urls import url_encode
from flask import Flask, request, jsonify, g, render_template, redirect

sys.path += ['flask-oidc/']
from flask_oidc import OpenIDConnect
import requests

# log level mutes every request going to stdout
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

# location of CA trust store file
print(f'certifi = {certifi.where()}')

# Type of Authentication Server: generic|keycloak|adfs
AUTH_PROVIDER = os.getenv("AUTH_PROVIDER","generic")
print(f'AUTH_PROVIDER: {AUTH_PROVIDER}')

# FQDN of OAuth2 Authentication Server
AUTH_SERVER = os.getenv("AUTH_SERVER","")
if len(AUTH_SERVER)<1:
  raise Exception("AUTH_SERVER is required environment variable")
print(f'AUTH_SERVER: {AUTH_SERVER}')

CLIENT_ID = os.getenv("CLIENT_ID","")
print(f'CLIENT_ID: {CLIENT_ID}')
CLIENT_SECRET = os.getenv("CLIENT_SECRET","")
print(f'CLIENT_SECRET: {CLIENT_SECRET}')

SCOPE = os.getenv("SCOPE","openid") # keycloak: 'openid email profile' # ADFS 'openid allatclaims api_delete'
print(f'SCOPE: {SCOPE}')

CLIENT_BASE_APP_URL = os.getenv("CLIENT_BASE_APP_URL","http://localhost:8080")
print(f'CLIENT_BASE_APP_URL: {CLIENT_BASE_APP_URL}')

# Auth Server has permission to redirect here
REDIRECT_URI = os.getenv("REDIRECT_URI","")
if len(REDIRECT_URI)<1 and "keycloak"==AUTH_PROVIDER:
  REDIRECT_URI = "*"
elif len(REDIRECT_URI)<1 and "adfs"==AUTH_PROVIDER:
  REDIRECT_URI = f'{CLIENT_BASE_APP_URL}/adfs/oauth2/token'
elif len(REDIRECT_URI)<1:
  REDIRECT_URI = "*"
print(f'REDIRECT_URI: {REDIRECT_URI}')

# dictionary that will agument app config
client_secrets_dict = {
  "web": {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": f'{REDIRECT_URI}'
  }
}
# app config settings
app.config.update({
    'OIDC_AUTH_PROVIDER': AUTH_PROVIDER,
    'OIDC_AUTH_SERVER': AUTH_SERVER,
    'OIDC_CLIENT_BASE_APP_URL': CLIENT_BASE_APP_URL,
    'OIDC_CLIENT_SECRETS': client_secrets_dict,

    'SECRET_KEY': 'abc123!',
    'DEBUG': True,
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': False,
    'OIDC_SCOPES': SCOPE.split(' ') if len(SCOPE)>0 else [],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_TOKEN_TYPE_HINT': 'code'
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

# allows override for Client App to say where code will be posted back
CALLBACK_ROUTE = os.getenv("CALLBACK_ROUTE","") # '/oidc_callback' is default for flask-oidc module
if len(CALLBACK_ROUTE)>0:
  print(f'CALLBACK_ROUTE: {CALLBACK_ROUTE}')
  app.config.update({
    'OIDC_CALLBACK_ROUTE': CALLBACK_ROUTE
  })

# ADFS requires non-standard 'resource' query parameter
if "adfs"==AUTH_SERVER:
  app.config.update({
    'OIDC_EXTRA_REQUEST_AUTH_PARAMS': { 'resource': f'{CLIENT_ID}'}
  })


oidc = OpenIDConnect(app, prepopulate_from_well_known_url=True)

@app.route('/')
def index():
    """Page that shows either authenticated user name OR login link
    """
    return render_template('index.html', user_loggedin=oidc.user_loggedin, oidc=oidc)

@app.route('/protected')
@oidc.require_login
def protected_path():
    """Protected endpoint that extracts private information from the OpenID Connect id_token.
       Uses the accompanied access_token to access a backend service.
    """

    info = oidc.user_getinfo(['aud', 'upn','email', 'sub','nonce','given_name','group','groups', 'role','scp','scope','iss','iat','exp'])
    print(f'id_token: {g.oidc_id_token}')
    print('=== BEGIN ID TOKEN =====')
    for s in info.items():
      print(s)
    print('=== END ID TOKEN =====')

    # pull claims from ID token
    scope = find_the_attribute(info,"",["scp","scope"])
    issued_at = datetime.datetime.fromtimestamp(info.get("iat"))
    expires_at = datetime.datetime.fromtimestamp(info.get("exp"))

    # get access token
    access_token = oidc.get_access_token()
    print('=== BEGIN ACCESS TOKEN =====')
    print(access_token)
    print('=== END ACCESS TOKEN =====')

    return render_template('access_token.html', id_token=info, issued_at=issued_at, expires_at=expires_at, scope=scope, access_token=access_token)

@app.route('/logout')
def logout():
    """Performs local logout by removing the session cookie."""

    oidc.logout()

    if "keycloak"==AUTH_PROVIDER:
      params = url_encode({ "post_logout_redirect_uri": f'{CLIENT_BASE_APP_URL}/', "client_id": CLIENT_ID })
      base_logout = oidc.get_client_secrets()['end_session_endpoint']
      logout_url = f'{base_logout}?{params}'
      print(f'sending to Keycloak logout: {logout_url}')
      return redirect(logout_url)
    elif "adfs"==AUTH_PROVIDER:
      id_token = request.cookies.get('oidc_id_token')
      print(f'id_token {id_token}')
      # this known issue might be the cause of not being able to specify 'id_token_hint'
      # https://support.microsoft.com/en-us/topic/september-21-2021-kb5005625-os-build-17763-2210-preview-5ae2f63d-a9ce-49dd-a5e6-e05b90dc1cd8
      params = url_encode({ "post_logout_redirect_uri": f'{CLIENT_BASE_APP_URL}/' }) #, "id_token_hint": id_token })
      base_logout = oidc.get_client_secrets()['end_session_endpoint']
      logout_url = f'{base_logout}?{params}'
      print(f'sending to ADFS logout: {logout_url}')
      return redirect(logout_url)
    else:
      return render_template('logout.html')


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

    port = int(os.getenv("PORT", 8080))
    print("Starting web server on port {}".format(port))

    app.run(host='0.0.0.0', port=port)
