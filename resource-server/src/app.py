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
from flask import Flask, request, jsonify, g
from flask_cors import CORS

sys.path += ['flask-oidc/']
from flask_oidc import OpenIDConnect
import requests

# log level mutes every request going to stdout
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
app = Flask(__name__)

# https://flask-cors.readthedocs.io/en/latest/
# https://flask-cors.corydolphin.com/en/latest/api.html
CORS_ORIGIN = os.getenv("CORS_ORIGIN","http://localhost:8080")
cors = CORS(app, supports_credentials=True, allow_headers=["Authorization","WWW-Authenticate"], expose_headers=["WWW-Authenticate","Content-Type"], resources={ r"/api/*": {"origins": f'{CORS_ORIGIN}' } })

ADFS = os.getenv("ADFS","win2k19-adfs1.fabian.lee")
print(f'ADFS: {ADFS}')

# dictionary instead of requiring client_secrets.json file
# better for configuring docker containers
client_secrets_dict = {
  "web": {
    "auth_uri": "https://${ADFS}/adfs/oauth2/authorize/",
    "client_id": "",
    "client_secret": "",
    "token_uri": ""
  }
}

app.config.update({
    'DEBUG': True,
    'OIDC_RESOURCE_SERVER_ONLY': True,
    'SECRET_KEY': '',
    'OIDC_ADFS' : f'{ADFS}',
    'OIDC_CLIENT_SECRETS': client_secrets_dict
})

oidc = OpenIDConnect(app)

@app.route('/api', methods=['GET','POST'])
@oidc.accept_token(require_token=True, scopes_required=['openid'])
def hello_api():
    """OAuth 2.0 protected API endpoint accessible via AccessToken"""

    print("=== BEGIN ACCESS TOKEN =======================")
    print(g.oidc_token_info)
    print("=== END ACCESS TOKEN =========================")

    data = {
      "hello": f"Welcome {g.oidc_token_info['email']}",
      "my_scopes": f"s{g.oidc_token_info['scp']}"
    }
    return data


if __name__ == '__main__' or __name__ == "main":

    port = int(os.getenv("PORT", 8081))
    print("Starting web server on port {}".format(port))

    app.run(host='0.0.0.0', port=port)


