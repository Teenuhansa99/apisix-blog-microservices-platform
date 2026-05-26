#!/usr/bin/env bash
# Shell script to create APISIX auth route (Linux/macOS). Make executable: chmod +x scripts/create_auth_route.sh

ADMIN_URL='http://127.0.0.1:9180/apisix/admin/routes/2'
API_KEY='edd1c9f034335f136f87ad84b625c8f1'
DATA='{"uri":"/auth/*","methods":["POST","GET"],"plugins":{"proxy-rewrite":{"regex_uri":["^/auth/(.*)$","/$1"]}},"upstream":{"type":"roundrobin","nodes":{"auth-service:5001":1}}}'

echo "Creating APISIX auth route at $ADMIN_URL ..."

curl -s -o /dev/null -w "%{http_code}\n" -X PUT "$ADMIN_URL" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$DATA"

if [ $? -eq 0 ]; then
  echo "Done."
else
  echo "Failed to create auth route."
fi
