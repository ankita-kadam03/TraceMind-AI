# VoiceEmotionRAG Frontend + Backend Quick Start
# Run this script in PowerShell to set up everything

Write-Host "🚀 VoiceEmotionRAG Frontend Setup" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js/npm not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
npm --version
Write-Host ""

# Install frontend dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend install failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "✅ Frontend dependencies installed`n" -ForegroundColor Green

# Install API dependencies
Write-Host "📦 Installing API dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn python-multipart
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ API dependencies install failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ API dependencies installed`n" -ForegroundColor Green

Write-Host "✅ Setup complete!`n" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure Ollama is running (ollama serve)" -ForegroundColor White
Write-Host "2. In one terminal, run: python api.py" -ForegroundColor White
Write-Host "3. In another terminal, run: cd frontend; npm run dev" -ForegroundColor White
Write-Host "4. Open http://localhost:5173 in your browser" -ForegroundColor White
