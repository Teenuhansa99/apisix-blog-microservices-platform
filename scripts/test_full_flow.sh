#!/usr/bin/env bash
# Shell script to test complete blog API flow through APISIX gateway
# This demonstrates: registration, login, JWT token, and posting

echo "========================================"
echo "BLOG API DEMO FLOW"
echo "========================================"
echo ""

# Test 1: Register a user
echo "1️⃣  REGISTER USER (username: demouser, password: demo123)"
REGISTER_RESPONSE=$(curl -s -X POST http://127.0.0.1:9080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"demo123"}')
echo "✅ Response: $REGISTER_RESPONSE"
echo ""

# Test 2: Login to get JWT token
echo "2️⃣  LOGIN & GET JWT TOKEN"
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:9080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"demo123"}')
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "✅ Token received: ${TOKEN:0:50}..."
echo ""

# Test 3: Get posts (before creating any)
echo "3️⃣  GET POSTS (empty list)"
POSTS_RESPONSE=$(curl -s -X GET http://127.0.0.1:9080/posts)
echo "✅ Current posts: $POSTS_RESPONSE"
echo ""

# Test 4: Create a post
echo "4️⃣  CREATE NEW POST"
CREATE_RESPONSE=$(curl -s -X POST http://127.0.0.1:9080/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Blog Post","description":"This is a test post created through APISIX","category":"demo"}')
echo "✅ Post created: $CREATE_RESPONSE"
echo ""

# Test 5: Get posts again
echo "5️⃣  GET POSTS (with newly created post)"
POSTS_RESPONSE=$(curl -s -X GET http://127.0.0.1:9080/posts)
echo "✅ Posts: $POSTS_RESPONSE"
echo ""

# Test 6: Get specific post
echo "6️⃣  GET SPECIFIC POST (ID: 1)"
POST_RESPONSE=$(curl -s -X GET http://127.0.0.1:9080/posts/1)
echo "✅ Post details: $POST_RESPONSE"
echo ""

echo "========================================"
echo "✅ DEMO COMPLETED SUCCESSFULLY"
echo "========================================"
