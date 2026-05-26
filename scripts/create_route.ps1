# PowerShell script to create APISIX route for the blog backend
# Usage: Open PowerShell in repository root and run: .\scripts\create_route.ps1

$adminUrl = 'http://127.0.0.1:9180/apisix/admin/routes/1'
$apiKey = 'edd1c9f034335f136f87ad84b625c8f1'
$body = '{"uri":"/posts*","upstream":{"type":"roundrobin","nodes":{"blog-service:5000":1}}}'

Write-Host "Creating APISIX route at $adminUrl ..."

try {
    Invoke-RestMethod -Uri $adminUrl -Method Put -Headers @{ 'X-API-KEY' = $apiKey; 'Content-Type' = 'application/json' } -Body $body
    Write-Host 'Route created (or updated) successfully.' -ForegroundColor Green
} catch {
    Write-Host 'Failed to create route:' -ForegroundColor Red
    Write-Host $_.Exception.Message
}
