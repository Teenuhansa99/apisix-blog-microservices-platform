# PowerShell script to test complete blog API flow through APISIX gateway
# This demonstrates: registration, login, JWT token, and posting

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BLOG API DEMO FLOW" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Register a user
Write-Host "1️⃣  REGISTER USER (username: demouser, password: demo123)" -ForegroundColor Yellow
$registerBody = @{username="demouser"; password="demo123"} | ConvertTo-Json
$registerResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/auth/register -Method Post -ContentType 'application/json' -Body $registerBody
Write-Host "✅ Response: $($registerResponse.message)`n" -ForegroundColor Green

# Test 2: Login to get JWT token
Write-Host "2️⃣  LOGIN & GET JWT TOKEN" -ForegroundColor Yellow
$loginBody = @{username="demouser"; password="demo123"} | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/auth/login -Method Post -ContentType 'application/json' -Body $loginBody
$token = $loginResponse.token
Write-Host "✅ Token received: $($token.Substring(0, 50))...`n" -ForegroundColor Green

# Test 3: Get posts (before creating any)
Write-Host "3️⃣  GET POSTS (empty list)" -ForegroundColor Yellow
$postsResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/posts -Method Get
Write-Host "✅ Current posts: $($postsResponse | ConvertTo-Json -Compress)`n" -ForegroundColor Green

# Test 4: Create a post
Write-Host "4️⃣  CREATE NEW POST" -ForegroundColor Yellow
$postBody = @{
    title="My First Blog Post"
    description="This is a test post created through APISIX"
    category="demo"
} | ConvertTo-Json
$createResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/posts -Method Post -ContentType 'application/json' -Body $postBody
Write-Host "✅ Post created: $($createResponse.post | ConvertTo-Json -Compress)`n" -ForegroundColor Green

# Test 5: Get posts again (after creating)
Write-Host "5️⃣  GET POSTS (with newly created post)" -ForegroundColor Yellow
$postsResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/posts -Method Get
Write-Host "✅ Posts count: $($postsResponse.Count)" -ForegroundColor Green
$postsResponse | Format-Table -AutoSize

# Test 6: Get specific post
Write-Host "`n6️⃣  GET SPECIFIC POST (ID: 1)" -ForegroundColor Yellow
$postResponse = Invoke-RestMethod -Uri http://127.0.0.1:9080/posts/1 -Method Get
Write-Host "✅ Post details:" -ForegroundColor Green
$postResponse | ConvertTo-Json | Write-Host

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ DEMO COMPLETED SUCCESSFULLY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
