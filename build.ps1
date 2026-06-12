# Build script — genere MediaConverter_Setup.exe
# Usage : clic droit > "Executer avec PowerShell"

Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# 1. Dependances Python
Step "Installation des dependances Python..."
pip install -r requirements.txt

# 2. PyInstaller
Step "Construction de MediaConverter.exe..."
python -m PyInstaller MediaConverter.spec --noconfirm

if (-not (Test-Path "dist\MediaConverter.exe")) {
    Write-Host "ERREUR : dist\MediaConverter.exe introuvable apres PyInstaller." -ForegroundColor Red
    exit 1
}

# 3. Inno Setup
$iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    Write-Host "Inno Setup introuvable. Installation..." -ForegroundColor Yellow
    winget install JRSoftware.InnoSetup --source winget --accept-package-agreements --accept-source-agreements
    $iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
}

Step "Compilation de l'installeur..."
New-Item -ItemType Directory -Force -Path installer | Out-Null
& $iscc installer.iss

$setup = "installer\MediaConverter_Setup_v1.2.0.exe"
if (Test-Path $setup) {
    $size = [math]::Round((Get-Item $setup).Length / 1MB, 1)
    Write-Host "`nSUCCES : $setup ($size MB)" -ForegroundColor Green
} else {
    Write-Host "ERREUR : le setup n'a pas ete genere." -ForegroundColor Red
    exit 1
}
