<#
.SYNOPSIS
  AgentPlatform environment verification.

.DESCRIPTION
  Run after Docker Desktop install, before "docker compose up --build".
  No admin privilege required.
#>

$ErrorActionPreference = 'Continue'

function Check($label, [scriptblock]$test) {
  Write-Host -NoNewline ("{0,-32}" -f $label)
  try {
    $result = & $test
    if ($result) {
      Write-Host "  OK    $result" -ForegroundColor Green
      return $true
    } else {
      Write-Host "  FAIL" -ForegroundColor Red
      return $false
    }
  } catch {
    Write-Host "  FAIL  $_" -ForegroundColor Red
    return $false
  }
}

Write-Host "=== AgentPlatform environment check ===" -ForegroundColor Cyan

$ok = $true
$ok = (Check "docker CLI"      { (docker --version) 2>$null }) -and $ok
$ok = (Check "docker compose"  { (docker compose version --short 2>$null) }) -and $ok
$ok = (Check "docker daemon"   {
  $info = docker info --format '{{.OperatingSystem}}' 2>$null
  if ($LASTEXITCODE -eq 0) { $info } else { $null }
}) -and $ok
$ok = (Check ".env file"       {
  if (Test-Path .env) {
    $line = Select-String -Path .env -Pattern 'ANTHROPIC_API_KEY=' | Select-Object -First 1
    if ($line.Line -match 'ANTHROPIC_API_KEY=sk-ant-xxx') { 'placeholder (fallback mode)' }
    elseif ($line.Line -match 'ANTHROPIC_API_KEY=.{5,}')  { 'present' }
    else { 'present but empty' }
  } else { $null }
}) -and $ok

foreach ($port in 3000, 8000, 5432) {
  $ok = (Check "port $port free" {
    $taken = Test-NetConnection localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $taken) { 'free' } else { $null }
  }) -and $ok
}

Write-Host ""
if ($ok) {
  Write-Host "Ready. Run: docker compose up --build" -ForegroundColor Green
} else {
  Write-Host "Some checks FAILED -- resolve them before running docker compose up." -ForegroundColor Yellow
}
