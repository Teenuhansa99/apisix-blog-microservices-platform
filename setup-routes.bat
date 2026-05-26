@echo off
REM Create upstream for auth service
curl -X PUT "http://127.0.0.1:9180/apisix/admin/upstreams/auth-upstream" ^
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" ^
  -H "Content-Type: application/json" ^
  -d "{\"nodes\":{\"auth-service:5001\":1},\"type\":\"roundrobin\"}"

REM Create upstream for blog service
curl -X PUT "http://127.0.0.1:9180/apisix/admin/upstreams/blog-upstream" ^
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" ^
  -H "Content-Type: application/json" ^
  -d "{\"nodes\":{\"blog-service:5000\":1},\"type\":\"roundrobin\"}"

REM Create route for /auth/login to auth service
curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/1" ^
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" ^
  -H "Content-Type: application/json" ^
  -d "{\"uri\":\"/auth/*\",\"upstream_id\":\"auth-upstream\",\"methods\":[\"POST\",\"GET\"]}"

REM Create route for /posts to blog service
curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/2" ^
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" ^
  -H "Content-Type: application/json" ^
  -d "{\"uri\":\"/posts*\",\"upstream_id\":\"blog-upstream\",\"methods\":[\"GET\",\"POST\",\"PUT\",\"DELETE\"]}"

echo Routes configured!
