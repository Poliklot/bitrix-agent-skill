[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$Repo = 'Poliklot/claude-bitrix-skill'
$Branch = 'master'
$InstallDir = Join-Path (Join-Path (Join-Path $HOME '.claude') 'skills') 'bitrix'
$RemoteVersionUrl = "https://raw.githubusercontent.com/$Repo/$Branch/bitrix/VERSION"
$ZipUrl = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [ok] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [warn] $Message" -ForegroundColor Yellow
}

function Invoke-WebRequestCompat {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [string]$OutFile
    )

    $params = @{ Uri = $Uri }
    if ($PSVersionTable.PSVersion.Major -lt 6) {
        $params.UseBasicParsing = $true
    }
    if ($OutFile) {
        $params.OutFile = $OutFile
    }

    Invoke-WebRequest @params
}

Write-Step 'Checking versions'

$remoteVersion = (Invoke-WebRequestCompat -Uri $RemoteVersionUrl).Content.Trim()
if ([string]::IsNullOrWhiteSpace($remoteVersion)) {
    throw 'Could not fetch remote version.'
}
Write-Ok "Remote version: $remoteVersion"

$localVersionFile = Join-Path $InstallDir 'VERSION'
$localVersion = ''
if (Test-Path -LiteralPath $localVersionFile) {
    $localVersion = (Get-Content -LiteralPath $localVersionFile -Raw).Trim()
    Write-Ok "Installed version: $localVersion"
}
else {
    Write-Warn 'No installed version found.'
}

if (-not $Force -and $localVersion -eq $remoteVersion) {
    Write-Host "`nAlready up to date. ($remoteVersion)" -ForegroundColor Green
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($localVersion) -and $localVersion -ne $remoteVersion) {
    Write-Step "Updating $localVersion -> $remoteVersion"
}
else {
    Write-Step "Installing version $remoteVersion"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("bitrix-skill-" + [guid]::NewGuid().ToString('N'))
$zipPath = Join-Path $tempRoot 'skill.zip'

try {
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Step 'Downloading'
    Invoke-WebRequestCompat -Uri $ZipUrl -OutFile $zipPath | Out-Null
    Write-Ok 'Downloaded'

    Expand-Archive -LiteralPath $zipPath -DestinationPath $tempRoot -Force
    $extractedDir = Get-ChildItem -LiteralPath $tempRoot -Directory |
        Where-Object { $_.Name -like 'claude-bitrix-skill-*' } |
        Select-Object -First 1

    if ($null -eq $extractedDir) {
        throw 'Unexpected zip structure.'
    }

    $skillSource = Join-Path $extractedDir.FullName 'bitrix'
    if (-not (Test-Path -LiteralPath $skillSource)) {
        throw 'Unexpected zip structure: bitrix directory not found.'
    }
    Write-Ok 'Extracted'

    Write-Step "Installing to $InstallDir"
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

    Get-ChildItem -LiteralPath $InstallDir -Force -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force

    Get-ChildItem -LiteralPath $skillSource -Force |
        ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $InstallDir -Recurse -Force
        }
    Write-Ok 'Files copied'

    $installedVersion = (Get-Content -LiteralPath (Join-Path $InstallDir 'VERSION') -Raw).Trim()
    if ($installedVersion -ne $remoteVersion) {
        throw "Version mismatch after install: expected $remoteVersion, got $installedVersion"
    }

    Write-Host "`nSuccess! Bitrix skill $remoteVersion installed at $InstallDir" -ForegroundColor Green
    Write-Host 'Usage: /bitrix <your task>'
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
