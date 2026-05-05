$owner = "JLBBARCO"
$repo = "programs-manager"
# Branch of this script file. Set to 'main' in the main branch copy, 'develop' in develop.
$ScriptBranch = "develop"

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

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
$exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
# 1. Verifica se já existe, se não, busca na API do GitHub
$shouldDownload = $false
if (-not $exePath) {
    $shouldDownload = $true
} else {
    try {
        if (-not (Test-Path $exePath)) { $shouldDownload = $true }
    } catch {
        $shouldDownload = $true
    }
}

if ($shouldDownload) {
    Write-Host "[programs-manager] Baixando versão compilada para Windows..."

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
        throw "Nenhum asset '*windows.zip' foi encontrado no release apropriado."
    }

    $zipTemp = Join-Path $env:TEMP "aip_win.zip"
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp -UseBasicParsing

    Expand-Archive -Path $zipTemp -DestinationPath $installRoot -Force
    Remove-Item $zipTemp -Force

    $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
    if (-not $exePath -or -not (Test-Path $exePath)) {
        throw "Executável não encontrado após extração em $installRoot"
    }
}

# 2. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[programs-manager] Iniciando..."
if (-not $exePath) {
    throw "Executável não encontrado. Caminho está vazio."
}

Write-Host "[programs-manager] Executável: $exePath"
Start-Process -FilePath $exePath