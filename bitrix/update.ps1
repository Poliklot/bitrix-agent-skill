[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Check
)

$ErrorActionPreference = 'Stop'

$Repo = 'Poliklot/claude-bitrix-skill'
$Branch = 'master'
$InstallScriptUrl = "https://raw.githubusercontent.com/$Repo/$Branch/install.ps1"
$RemoteVersionUrl = "https://raw.githubusercontent.com/$Repo/$Branch/bitrix/VERSION"
$LocalVersionFile = Join-Path $PSScriptRoot 'VERSION'

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

function Get-LocalVersion {
    if (Test-Path -LiteralPath $LocalVersionFile) {
        return (Get-Content -LiteralPath $LocalVersionFile -Raw).Trim()
    }

    return ''
}

function Get-RemoteVersion {
    return (Invoke-WebRequestCompat -Uri $RemoteVersionUrl).Content.Trim()
}

function Convert-ToComparableVersion {
    param([string]$Version)

    if ([string]::IsNullOrWhiteSpace($Version)) {
        return [version]'0.0.0.0'
    }

    $parts = $Version.Trim().TrimStart('v').Split('.')
    while ($parts.Count -lt 4) {
        $parts += '0'
    }

    return [version]::new(
        [int]$parts[0],
        [int]$parts[1],
        [int]$parts[2],
        [int]$parts[3]
    )
}

function Test-VersionGreater {
    param(
        [string]$Left,
        [string]$Right
    )

    return (Convert-ToComparableVersion $Left) -gt (Convert-ToComparableVersion $Right)
}

function Invoke-CheckMode {
    $localVersion = Get-LocalVersion
    $remoteVersion = ''

    try {
        $remoteVersion = Get-RemoteVersion
    }
    catch {
        Write-Output 'CHECK_FAILED reason=remote_version_unavailable'
        return
    }

    if ([string]::IsNullOrWhiteSpace($localVersion)) {
        Write-Output "UPDATE_AVAILABLE local=none remote=$remoteVersion"
        return
    }

    if (Test-VersionGreater -Left $remoteVersion -Right $localVersion) {
        Write-Output "UPDATE_AVAILABLE local=$localVersion remote=$remoteVersion"
        return
    }

    Write-Output "UP_TO_DATE version=$localVersion"
}

if ($Check) {
    Invoke-CheckMode
    exit 0
}

Write-Host 'Checking versions'

$remoteVersion = Get-RemoteVersion
if ([string]::IsNullOrWhiteSpace($remoteVersion)) {
    throw 'Could not fetch remote version.'
}

$localVersion = Get-LocalVersion

if (-not $Force) {
    if (-not [string]::IsNullOrWhiteSpace($localVersion) -and $localVersion -eq $remoteVersion) {
        Write-Host "Already up to date ($localVersion)"
        exit 0
    }

    if (-not [string]::IsNullOrWhiteSpace($localVersion) -and (Test-VersionGreater -Left $localVersion -Right $remoteVersion)) {
        Write-Host "Installed version ($localVersion) is newer than remote ($remoteVersion)"
        exit 0
    }
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("bitrix-skill-update-" + [guid]::NewGuid().ToString('N'))
$tempScriptPath = Join-Path $tempRoot 'install.ps1'

try {
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Host 'Fetching latest installer from GitHub...'
    Invoke-WebRequestCompat -Uri $InstallScriptUrl -OutFile $tempScriptPath | Out-Null

    $installScript = [scriptblock]::Create((Get-Content -LiteralPath $tempScriptPath -Raw))

    if ($Force) {
        & $installScript -Force
    }
    else {
        & $installScript
    }
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
