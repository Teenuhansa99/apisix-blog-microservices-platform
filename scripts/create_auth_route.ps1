# PowerShell script to create APISIX auth route
# Usage: Open PowerShell in repository root and run: .\scripts\create_auth_route.ps1

$adminUrl = 'http://127.0.0.1:9180/apisix/admin/routes/2'
$apiKey = 'edd1c9f034335f136f87ad84b625c8f1'
$body = '{"uri":"/auth/*","methods":["POST","GET"],"plugins":{"proxy-rewrite":{"regex_uri":["^/auth/(.*)$","/$1"]}},"upstream":{"type":"roundrobin","nodes":{"auth-service:5001":1}}}'

Write-Host "Creating APISIX auth route at $adminUrl ..."

try {
    Invoke-RestMethod -Uri $adminUrl -Method Put -Headers @{ 'X-API-KEY' = $apiKey; 'Content-Type' = 'application/json' } -Body $body
    Write-Host 'Auth route created (or updated) successfully.' -ForegroundColor Green
} catch {
    Write-Host 'Failed to create auth route:' -ForegroundColor Red
    Write-Host $_.Exception.Message
}
