$envPath = Join-Path $PSScriptRoot "..\.env"

if (Test-Path $envPath) {
  Write-Output "using existing $envPath"
  exit 0
}

@"
# Local Docker Compose overrides for Project-Porter
NGINX_PORT=81
"@ | Set-Content -NoNewline $envPath

Write-Output "created $envPath with NGINX_PORT=81"
