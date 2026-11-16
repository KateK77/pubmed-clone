param(
    [ValidateSet('setup', 'backend', 'frontend')]
    [string]$Service = 'setup'
)

$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    $projectPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
    if ($Service -eq 'setup') {
        if (-not (Test-Path -LiteralPath $projectPython)) {
            python -m venv .venv
            if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 or newer, then retry setup.' }
        }
        & $projectPython -m pip install -r backend/requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
        if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
        & $projectPython backend/manage.py migrate --noinput
        if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
        & $projectPython backend/manage.py create_demo
        if ($LASTEXITCODE -ne 0) { throw 'Local demo account setup failed.' }
        if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 22.12 or newer with npm, open a new PowerShell, and rerun setup.' }
        npm.cmd --prefix frontend ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
        Write-Output 'Setup complete. Run start.ps1 -Service backend and start.ps1 -Service frontend in separate terminals.'
    } elseif ($Service -eq 'backend') {
        if (-not (Test-Path -LiteralPath $projectPython)) { throw 'Run start.ps1 -Service setup first.' }
        & $projectPython backend/manage.py runserver 127.0.0.1:8014
    } else {
        npm.cmd --prefix frontend run dev
    }
} finally {
    Pop-Location
}
