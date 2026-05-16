$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --windowed `
    --name Cucumber `
    --icon assets\cucumber.ico `
    --add-data "assets;assets" `
    --collect-binaries imageio_ffmpeg `
    --copy-metadata imageio `
    cucumber_desktop.py

Write-Host "Built dist\Cucumber\Cucumber.exe"
