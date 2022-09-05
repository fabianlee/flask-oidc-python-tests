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

if [[ 1 -eq 0 ]]; then
echo ""
echo "===== OPTIONS to /infojson (unprotected) should return CORS headers  ====="
curl -X OPTIONS -kIv -A "$ua" "$resource_server/infojson" 2>/dev/null | grep -E "^Access-Control|^HTTP"
echo ""
echo "===== GET to /infojson (unprotected) should return CORS headers  ====="
curl -X GET -kIv -A "$ua" "$resource_server/infojson" 2>/dev/null | grep -E "^Access-Control|^HTTP"


echo ""
echo "===== OPTIONS to /api/user/me (unprotected) should return CORS headers  ====="
curl -X OPTIONS -kIv -A "$ua" "$resource_server/api/user/me" 2>/dev/null | grep -E "^Access-Control|^HTTP"

fi

echo ""
echo "===== GET to /api should return api results  ====="
curl -X GET -k -A "$ua" "$resource_server/api" -H "$auth_header"
exit 0

echo ""
echo ""
echo "===== GET to /api/user should return list of users, IFF callee in group 'Domain Users'  ====="
curl -X GET -k -A "$ua" "$resource_server/api/user" -H "$auth_header"

options='--fail --connect-timeout 3 --retry 0 -s -o /dev/null -w %{http_code}'

echo ""
echo ""
echo "===== DELETE to /api/user should delete last user, IFF callee in group 'managers' and 'api_delete' scope  ====="
outstr=$(curl -X DELETE -A "$ua" $options "$resource_server/api/user" -H "$auth_header")
retVal=$?
if [[ $retVal -eq 0 ]]; then
  echo "outstr: $outstr"
  curl -X GET -k -A "$ua" "$resource_server/api/user" -H "$auth_header"
else
  echo "ERROR $retVal trying to DELETE /api/user/engineer.  Are you in group 'managers' and 'api_delete' scope?"
fi

echo ""
echo ""
echo "===== GET to /api/user/engineer should return list of engineers, IFF callee in group 'engineers' or 'managers' ====="
outstr=$(curl -A "$ua" $options "$resource_server/api/user/engineer" -H "$auth_header")
retVal=$?
if [[ $retVal -eq 0 ]]; then
  curl -X GET -k -A "$ua" "$resource_server/api/user/engineer" -H "$auth_header"
else
  echo "ERROR $retVal trying to GET /api/user/engineer.  Are you in group 'engineers' or 'managers'?"
fi

echo ""
echo ""
echo "===== GET to /api/user/manager should return list of managers, IFF callee in group 'managers' ====="
outstr=$(curl -A "$ua" $options "$resource_server/api/user/manager" -H "$auth_header")
retVal=$?
if [[ $retVal -eq 0 ]]; then
  curl -X GET -k -A "$ua" "$resource_server/api/user/manager" -H "$auth_header"
else
  echo "ERROR $retVal trying to GET /api/user/manager.  Are you in group 'managers'?"
fi

echo ""
echo ""
