#!/bin/bash
#
# Uses Authorization and Bearer token to call Resource Server with JWT token
#
# Requires that you export 'JWT' environment variable
#

# defaults to localhost:8081 unless overridden on command line
resource_server="${1:-http://localhost:8081}"
echo "Resource server: $resource_server"

# curl 'User Agent'
ua="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"

# make sure 'JWT' environment variable set
[[ -n "$JWT" ]] || { echo "ERROR need 'JWT' defined as environment variable"; exit 1; }
auth_header="Authorization: Bearer ${JWT}"

echo ""
echo "===== GET to /api should return api results  ====="
curl -X GET -k -A "$ua" "$resource_server/api" -H "$auth_header"

options='--fail --connect-timeout 3 --retry 0 -s -o /dev/null -w %{http_code}'

echo ""
echo ""
echo "===== GET to /api/managers should return list of managers, IFF callee in group 'managers' ====="
outstr=$(curl -A "$ua" $options "$resource_server/api/managers" -H "$auth_header")
retVal=$?
if [[ $retVal -eq 0 ]]; then
  curl -X GET -k -A "$ua" "$resource_server/api/managers" -H "$auth_header"
else
  echo "ERROR $retVal trying to GET /api/managers.  Are you in group 'managers'?"
fi

echo ""
echo ""
