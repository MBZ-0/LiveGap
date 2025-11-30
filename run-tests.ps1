# Quick Test Runner Script
# This script runs tests for both backend and frontend

Write-Host "`n=== LiveGap CI Test Runner ===" -ForegroundColor Cyan
Write-Host "Running tests with coverage...`n" -ForegroundColor Cyan

# Backend Tests
Write-Host "[1/2] Running Backend Tests (Python)..." -ForegroundColor Yellow
Push-Location "livegap-mini\backend"

# Check if pytest is installed
try {
    python -m pytest --version | Out-Null
    Write-Host "✓ pytest found" -ForegroundColor Green
} catch {
    Write-Host "✗ pytest not found, installing..." -ForegroundColor Red
    python -m pip install pytest pytest-cov pytest-asyncio -q
}

# Run tests
Write-Host "`nRunning backend tests..." -ForegroundColor Cyan
python -m pytest tests/ --cov=app --cov-report=term --cov-report=html -v

$backendExitCode = $LASTEXITCODE
Pop-Location

Write-Host "`n" -NoNewline

# Frontend Tests
Write-Host "[2/2] Running Frontend Tests (Node.js)..." -ForegroundColor Yellow
Push-Location "livegap-mini\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "✗ node_modules not found, installing dependencies..." -ForegroundColor Red
    npm install
} else {
    Write-Host "✓ node_modules found" -ForegroundColor Green
}

# Run tests
Write-Host "`nRunning frontend tests..." -ForegroundColor Cyan
npm run test:coverage

$frontendExitCode = $LASTEXITCODE
Pop-Location

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
if ($backendExitCode -eq 0) {
    Write-Host "✓ Backend Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Backend Tests: FAILED (Exit Code: $backendExitCode)" -ForegroundColor Red
}

if ($frontendExitCode -eq 0) {
    Write-Host "✓ Frontend Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend Tests: FAILED (Exit Code: $frontendExitCode)" -ForegroundColor Red
}

Write-Host "`nCoverage reports:" -ForegroundColor Cyan
Write-Host "  Backend:  livegap-mini\backend\htmlcov\index.html" -ForegroundColor Gray
Write-Host "  Frontend: livegap-mini\frontend\coverage\lcov-report\index.html" -ForegroundColor Gray

if ($backendExitCode -eq 0 -and $frontendExitCode -eq 0) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ Some tests failed. Check output above." -ForegroundColor Red
    exit 1
}
