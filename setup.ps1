# =====================================
# GRC-FORGE COMPLIANCE PIPELINE SETUP
# Supports: Docker or Local VirtualEnv
# =====================================

Clear-Host
Write-Host "==============================="
Write-Host "     GRC-FORGE SETUP SCRIPT"
Write-Host "===============================" -ForegroundColor Cyan

# Ask user choice
$choice = Read-Host "`nDo you want to run GRC-FORGE via Docker? (Y/N)"

if ($choice -eq 'Y' -or $choice -eq 'y') {
    # ========== DOCKER MODE ==========
    Write-Host "`n==> Building Docker Image: grc-forge-auto" -ForegroundColor Cyan
    docker build -t grc-forge-auto .

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed." -ForegroundColor Red
        exit 1
    }

    Write-Host "`n==> Running Docker Container..." -ForegroundColor Cyan
    $envVars = Get-Content .env | ForEach-Object {
        $parts = $_ -split "="
        "-e $($parts[0])=$($parts[1])"
    } -join " "

    $dockerRunCmd = "docker run -it --rm -v `"$($PWD.Path):/app`" $envVars --network=host grc-forge-auto"
    Invoke-Expression $dockerRunCmd

    Write-Host "`nDocker execution complete. Pipeline finished." -ForegroundColor Green
    exit 0
}
else {
    # ========== LOCAL VENV MODE ==========
    Write-Host "`n==> Creating Virtual Environment..." -ForegroundColor Cyan
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

    Write-Host "==> Pulling LLM model (mistral:instruct) via Ollama..." -ForegroundColor Cyan
    ollama pull mistral:instruct

    Write-Host "==> Pulling LLM model (deepseek:latest) via Ollama..." -ForegroundColor Cyan
    ollama pull deepseek:latest

    Write-Host "==> Starting Ollama Service (background)..." -ForegroundColor Cyan
    Start-Process -NoNewWindow -FilePath "ollama" -ArgumentList "serve"

    # Run each phase
    $scripts = @("Phase1.py", "Phase2.py", "Phase3_Convertor.py", "Phase3_Graph.py", "Phase4.py")

    foreach ($script in $scripts) {
        Write-Host "`n==> Running $script ..." -ForegroundColor Cyan
        python $script
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error occurred in $script. Stopping pipeline." -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "`nLocal execution complete. Pipeline finished." -ForegroundColor Green
}
