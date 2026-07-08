param (
    [switch]$Install = $false
)

$Root = Split-Path -Parent $PSCommandPath

if ($Install) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
    Push-Location "$Root\backend"
    pip install -r requirements.txt
    Pop-Location

    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location "$Root\frontend"
    npm install
    Pop-Location

    Write-Host "Installation complete." -ForegroundColor Green
    return
}

# Start backend
Write-Host "Starting backend (FastAPI) on http://localhost:8000 ..." -ForegroundColor Cyan
$job1 = Start-Job -ScriptBlock {
    Set-Location "$using:Root\backend"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Start frontend
Write-Host "Starting frontend (Next.js) on http://localhost:3000 ..." -ForegroundColor Cyan
$job2 = Start-Job -ScriptBlock {
    Set-Location "$using:Root\frontend"
    npm run dev
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  AI Startup Idea Validator"           -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:3000"     -ForegroundColor Yellow
Write-Host "  Backend  : http://localhost:8000"     -ForegroundColor Yellow
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor Gray

try {
    while ($true) {
        Start-Sleep -Seconds 1
        $j1 = Receive-Job -Job $job1 -ErrorAction SilentlyContinue
        $j2 = Receive-Job -Job $job2 -ErrorAction SilentlyContinue
    }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job -Job $job1, $job2 -ErrorAction SilentlyContinue
    Remove-Job -Job $job1, $job2 -ErrorAction SilentlyContinue
}
