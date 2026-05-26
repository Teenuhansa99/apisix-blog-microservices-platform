#!/usr/bin/env bash
# Shell script to create APISIX route (Linux/macOS). Make executable: chmod +x scripts/create_route.sh

ADMIN_URL='http://127.0.0.1:9180/apisix/admin/routes/1'
API_KEY='edd1c9f034335f136f87ad84b625c8f1'
DATA='{"uri":"/posts*","upstream":{"type":"roundrobin","nodes":{"blog-service:5000":1}}}'

echo "Creating APISIX route at $ADMIN_URL ..."

curl -s -o /dev/null -w "%{http_code}\n" -X PUT "$ADMIN_URL" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$DATA"

if [ $? -eq 0 ]; then
  echo "Done."
else
  echo "Failed to create route."
fi
