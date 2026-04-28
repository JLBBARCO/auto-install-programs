$owner = "JLBBARCO"
$repo = "programs-manager"
$installRoot = Join-Path $HOME ".auto-install-programs"
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
if (!(Test-Path $exePath)) {
    Write-Host "[programs-manager] Baixando versão compilada para Windows..."
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/latest" -UseBasicParsing
    $asset = $release.assets | Where-Object { $_.name -eq "Auto-Install-Programs-windows.zip" } | Select-Object -First 1

    if (!$asset) {
        throw "Nenhum asset '*windows.zip' foi encontrado no release mais recente."
    }
    
    $zipTemp = Join-Path $env:TEMP "aip_win.zip"
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipTemp -UseBasicParsing
    
    Expand-Archive -Path $zipTemp -DestinationPath $installRoot -Force
    Remove-Item $zipTemp -Force

    $exePath = Resolve-ExePath -Root $installRoot -ExpectedPath $expectedExePath
    if (!(Test-Path $exePath)) {
        throw "Executável não encontrado após extração em $installRoot"
    }
}

# 2. Executa o binário diretamente (Sem Python, sem VENV)
Write-Host "[programs-manager] Iniciando..."
Start-Process -FilePath $exePath