# Repository info
$owner = "JLBBARCO"
$repo = "programs-manager"

# Set this script's branch. When this file is fetched from:
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1  -> set to 'main'
#  - https://raw.githubusercontent.com/JLBBARCO/programs-manager/beta/run.ps1 -> set to 'beta'
# The branch controls whether the script downloads the latest stable release (main)
# or the most-recent prerelease (beta).
$ScriptBranch = 'beta'
# Use the current user's profile directory (works on Windows reliably).
$installRoot = Join-Path $env:USERPROFILE ".auto-install-programs"
$expectedExePath = Join-Path $installRoot "Programs Manager\Programs Manager.exe"

Write-Host "[programs-manager] Script em execução: $PSCommandPath"

function Resolve-ExePath {
    param(
        [string]$Root,
        [string]$ExpectedPath
    )

    if (Test-Path $ExpectedPath) {
        return $ExpectedPath
    }

    $foundExe = Get-ChildItem -Path $Root -Filter "Auto Install Programs.exe" -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($foundExe) {
        return $foundExe.FullName
    }

    return $null
}

function Resolve-LocalBuildPath {
    # Try to find the local build from the project directory
    # When script is executed via iex, $PSCommandPath may be null; use $MyInvocation as fallback
    $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
    
    if (-not $scriptPath) {
        # Script location unknown (likely executed via iex from web), skip local build check
        return $null
    }
    
    $scriptDir = Split-Path -Parent $scriptPath
    $buildDir = Join-Path $scriptDir "build"
    
    if (Test-Path $buildDir) {
        $foundExe = Get-ChildItem -Path $buildDir -Filter "Auto Install Programs.exe" -Recurse -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        
        if ($foundExe) {
            return $foundExe.FullName
        }
    }
    
    return $null
}

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

# 1. Try local build first
$exePath = Resolve-LocalBuildPath
if ($exePath) {
    Write-Host "[programs-manager] Build local encontrado: $exePath"
}

# 2. If no local build, try installed version
if (-not $exePath) {
    $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
}

# 3. If still not found, try to download
if (-not $exePath) {
    Write-Host "[programs-manager] Tentando baixar versão compilada para Windows..."

    try {
        # Decide which release to fetch based on the script branch.
        if ($ScriptBranch -eq 'beta') {
            # Find the most recent prerelease
            $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -UseBasicParsing
            $prerelease = $releases | Where-Object { $_.prerelease } | Sort-Object -Property published_at -Descending | Select-Object -First 1
            if (-not $prerelease) { throw "No prerelease found." }
            $asset = $prerelease.assets | Where-Object { $_.name -eq "Auto-Install-Programs-windows.zip" } | Select-Object -First 1
        } else {
            # Stable channel: use latest stable release endpoint
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
            $asset = $release.assets | Where-Object { $_.name -eq "Auto-Install-Programs-windows.zip" } | Select-Object -First 1
        }

        if (-not $asset) {
            throw "Asset 'Auto-Install-Programs-windows.zip' não encontrado na release escolhida." 
        }

        $zipTemp = Join-Path $env:TEMP "aip_win.zip"
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp -UseBasicParsing

        Expand-Archive -Path $zipTemp -DestinationPath $installRoot -Force
        Remove-Item $zipTemp -Force

        $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
    } catch {
        Write-Host "[programs-manager] Erro ao baixar: $_" -ForegroundColor Yellow
        Write-Host "[programs-manager] Tentando compilar localmente..." -ForegroundColor Yellow

        # Try to compile locally as last resort
        $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
        if ($scriptPath) {
            $scriptDir = Split-Path -Parent $scriptPath
            $buildScript = Join-Path $scriptDir "build.bat"
            if (Test-Path $buildScript) {
                Write-Host "[programs-manager] Executando build.bat..."
                & $buildScript
                $exePath = Resolve-LocalBuildPath
            }
        }
    }
}

# Final check
if (-not $exePath -or -not (Test-Path $exePath)) {
    throw "Executável não encontrado. Tente executar: python main.py ou .\build.bat"
}

# 2. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[programs-manager] Iniciando..."
Write-Host "[programs-manager] Executável: $exePath"
Start-Process -FilePath $exePath