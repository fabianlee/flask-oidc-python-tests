#!/usr/bin/env python
#
# Adds CA cert from environment to python CA trust file 
#

import os
import io
import sys
import certifi

# adds to local CA trust store file, if not already there
def add_to_ca_trust(cafile,myCA):
  is_found = open(cafile, 'r').read().find(myCA) >= 0
  print(f'is myCA found? {is_found}')

  if is_found:
    print("SKIP myCA already found in CA trust store file")
  else:
    print("ADD myCA to CA trust store file")
    with open(cafile, 'a') as outfile:
      outfile.write(myCA)
    

# location of python CA trust file
cafile = certifi.where()
print(f'certifi = {cafile}')

CA_PEM = os.getenv("CA_PEM","")
CA_PEM_FILE = os.getenv("CA_PEM_FILE","")

if len(CA_PEM)>0:

  print("CA_PEM looks like environment variable")
  # make sure to replace any spaces or carriage return back to EOL
  if CA_PEM.startswith('-----BEGIN CERTIFICATE-----') and CA_PEM.endswith('-----END CERTIFICATE-----'):
    content = CA_PEM.split('-----BEGIN CERTIFICATE-----')[1] # get all after
    content = content.split('-----END CERTIFICATE-----')[0] # get all before
    content = content.replace('\r','\n')
    content = content.replace(' ','\n')
    CA_PEM = '-----BEGIN CERTIFICATE-----' + content + '-----END CERTIFICATE-----\n'
    print("done with substitution of CR and spaces to new lines")
  print(f'custom CA:\n{CA_PEM}')
  add_to_ca_trust(cafile,CA_PEM)

elif os.path.exists("myCA.pem"):

  print("found myCA.pem in current directory, going to read contents")
  with open('myCA.pem','r') as mycafile:
    myCA = mycafile.read()
  print(f'custom CA:\n{myCA}')

  add_to_ca_trust(cafile,myCA)

elif os.path.exists(CA_PEM_FILE):

  print("CA_PEM_FILE is pointed to file, going to read contents")
  with open(CA_PEM_FILE,'r') as mycafile:
    myCA = mycafile.read()
  print(f'custom CA:\n{myCA}')

  add_to_ca_trust(cafile,myCA)

else:
  print("SKIP cannot find valid env var or file")

print()
print("--------------------------------")
