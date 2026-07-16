$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

if (-not (Test-Path '.env')) {
    Write-Host '.env not found. Copy .env.example to .env and fill in your values first.'
    exit 1
}

docker compose up --build -d

Write-Host 'Deployment started.'
Write-Host 'Backend: http://localhost:8000/health'
Write-Host 'Frontend: http://localhost:5173'
