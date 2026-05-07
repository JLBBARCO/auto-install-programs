$owner = "JLBBARCO"
$repo = "programs-manager"
# Branch of this script file. Set via AIP_BRANCH when you need to override the current copy.
$ScriptBranch = $env:AIP_BRANCH
if (-not $ScriptBranch) {
    $ScriptBranch = "develop"
}

# Use the current user's profile directory (works on Windows reliably).
$installRoot = Join-Path $env:USERPROFILE ".auto-install-programs"
$expectedExePath = Join-Path $installRoot "Auto Install Programs\Auto Install Programs.exe"

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
    $scriptDir = Split-Path -Parent $PSCommandPath
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
        if ($ScriptBranch -eq 'develop') {
            # Prefer the latest prerelease for develop scripts
            $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -UseBasicParsing
            $pr = $releases | Where-Object { $_.prerelease -eq $true } | Select-Object -First 1
            if ($pr) {
                $asset = $pr.assets | Where-Object { $_.name -eq "Auto-Install-Programs-windows.zip" } | Select-Object -First 1
            }
        }

        if (-not $asset) {
            # Fallback to latest stable release
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
            $asset = $release.assets | Where-Object { $_.name -eq "Auto-Install-Programs-windows.zip" } | Select-Object -First 1
        }

        if (-not $asset) {
            throw "Asset 'Auto-Install-Programs-windows.zip' não encontrado no release."
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
        $scriptDir = Split-Path -Parent $PSCommandPath
        $buildScript = Join-Path $scriptDir "build.bat"
        if (Test-Path $buildScript) {
            Write-Host "[programs-manager] Executando build.bat..."
            & $buildScript
            $exePath = Resolve-LocalBuildPath
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