# =====================================
# Compliance Pipeline Full Setup Script
# Includes: VirtualEnv, Folders, .env, Requirements, Ollama
# =====================================

Write-Host "==> Creating Virtual Environment..." -ForegroundColor Cyan
python -m venv venv

Write-Host "==> Activating Virtual Environment..." -ForegroundColor Cyan
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "Error: Could not activate virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "==> Installing Python Requirements..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "==> Creating Required Folders..." -ForegroundColor Cyan
$folders = @("data", "dataset", "vectorstore", "vectorstore2")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder | Out-Null
        Write-Host "Created folder: $folder"
    }
}

Write-Host "==> Creating .env File (if missing)..." -ForegroundColor Cyan
$envFilePath = ".env"
if (-not (Test-Path $envFilePath)) {
    Set-Content -Path $envFilePath -Value "HF_TOKEN=your_huggingface_token_here"
    Add-Content -Path $envFilePath -Value "COHERE_API_KEY=your_cohere_api_key_here"
    Write-Host ".env created. Please update it with your actual API keys." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists. Skipping." -ForegroundColor Green
}

Write-Host "==> Checking Ollama Installation..." -ForegroundColor Cyan
$ollama = Get-Command "ollama" -ErrorAction SilentlyContinue
if ($null -eq $ollama) {
    Write-Host "Ollama is not installed. Please install it from https://ollama.com" -ForegroundColor Red
    exit 1
}

Write-Host "==> Pulling LLM model (mistral) via Ollama..." -ForegroundColor Cyan
ollama pull mistral

Write-Host "==> Pulling LLM model (deepseek:latest) via Ollama..." -ForegroundColor Cyan
ollama pull deepseek:latest

Write-Host "==> Starting Ollama Service (background)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "ollama" -ArgumentList "serve"

Write-Host "`n Full Setup Complete. Your environment and Ollama are ready." -ForegroundColor Green
