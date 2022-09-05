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
from flask import Flask, request, jsonify, g, render_template

sys.path += ['flask-oidc/']
from flask_oidc import OpenIDConnect
import requests

# log level mutes every request going to stdout
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

ADFS = os.getenv("ADFS","win2k19-adfs1.fabian.lee")
print(f'ADFS: {ADFS}')

# do a smoke test right up front that checks whether ADFS certs have been loaded
# if not, no reason going forward
print(f'certifi = {certifi.where()}')
http = httplib2.Http() #disable_ssl_certificate_validation=True)
try:
  content = http.request(f'https://{ADFS}/adfs/.well-known/openid-configuration')[1]
  #print( content.decode() )
  print("SUCCESS pulling /adfs/.well-known/openid-configuration, proves ADFS certificate is valid in CA filestore")
except ssl.SSLCertVerificationError as e:
  print("SSL verification error, ADFS cert and root not loaded into the root CA")
  raise(e)
  exit(3)
except Exception as e:
  print("ERROR could not reach ADFS well known configuration using httplib2")
  raise(e)
  exit(3)

ADFS_CLIENT_ID = os.getenv("ADFS_CLIENT_ID","")
print(f'ADFS_CLIENT_ID: {ADFS_CLIENT_ID}')
ADFS_CLIENT_SECRET = os.getenv("ADFS_CLIENT_SECRET","")
print(f'ADFS_CLIENT_SECRET: {ADFS_CLIENT_SECRET}')

ADFS_SCOPE = os.getenv("ADFS_SCOPE","openid allatclaims api_delete")
print(f'ADFS_SCOPE: {ADFS_SCOPE}')

ADFS_REDIRECT_URI = os.getenv("ADFS_REDIRECT_URI","http://localhost:8080/adfs/oauth2/token")
print(f'ADFS_REDIRECT_URI: {ADFS_REDIRECT_URI}')

# dictionary instead of requiring 'client_secrets.json' file
# better for configuring docker containers
client_secrets_dict = {
  "web": {
        "auth_uri": f'https://{ADFS}/adfs/oauth2/authorize/',
        "client_id": f'{ADFS_CLIENT_ID}',
        "client_secret": f'{ADFS_CLIENT_SECRET}',
        "redirect_uri": f'{ADFS_REDIRECT_URI}',
        "token_uri": f'https://{ADFS}/adfs/oauth2/token/'
  }
}

app.config.update({
    'SECRET_KEY': 'abc123!',
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': client_secrets_dict,
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_ADFS' : f'{ADFS}',
    'OIDC_VALID_ISSUERS': f'https://{ADFS}/adfs',
    'OIDC_EXTRA_REQUEST_AUTH_PARAMS': { 'resource': f'{ADFS_CLIENT_ID}'},
    'OIDC_CALLBACK_ROUTE': "/login/oauth2/code/adfs", # overrides default /oidc_callback
    'OIDC_USER_INFO_ENABLED': False,
    'OIDC_SCOPES': ADFS_SCOPE.split(' '),
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_TOKEN_TYPE_HINT': 'code'
})

oidc = OpenIDConnect(app)

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

    info = oidc.user_getinfo(['aud', 'upn','email', 'sub','nonce','given_name','group','role','scp','iss','iat','exp'])
    print(f'id_token: {g.oidc_id_token}')
    print('=== BEGIN ID TOKEN =====')
    for s in info.items():
      print(s)
    print('=== END ID TOKEN =====')

    # pull claims from ID token
    username = info.get('upn')
    email = info.get('email')
    user_id = info.get('sub')
    issued_at = datetime.datetime.fromtimestamp(info.get("iat"))
    expires_at = datetime.datetime.fromtimestamp(info.get("exp"))

    # get access token
    access_token = oidc.get_access_token()
    print('=== BEGIN ACCESS TOKEN =====')
    print(access_token)
    print('=== END ACCESS TOKEN =====')

    return render_template('access_token.html', id_token=info, issued_at=issued_at, expires_at=expires_at, access_token=access_token)

@app.route('/logout')
def logout():
    """Performs local logout by removing the session cookie."""

    oidc.logout()
    return render_template('logout.html')
    #return 'Hi, you have been logged out! <a href="/">Back to Home</a>'



if __name__ == '__main__' or __name__ == "main":

    port = int(os.getenv("PORT", 8080))
    print("Starting web server on port {}".format(port))

    app.run(host='0.0.0.0', port=port)
