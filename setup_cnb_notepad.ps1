# setup_cnb_notepad.ps1

$ErrorActionPreference = "Stop"

function Check-PythonVersion {
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonInstalled) {
        Write-Host "Error: Python is not installed or not in PATH."
        Write-Host "Please install Python 3 (3.11.8 recommended)."
        exit 1
    }

    $versionOutput = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $versionParts = $versionOutput -split '\.'
    $pythonMajor = [int]$versionParts[0]
    $pythonMinor = [int]$versionParts[1]

    if ($pythonMajor -lt 3 -or ($pythonMajor -eq 3 -and $pythonMinor -lt 11)) {
        Write-Host "Error: Python 3.11 or higher is required."
        Write-Host "Please install Python 3 (3.11.8 recommended)."
        exit 1
    }
}

function Create-VirtualEnv {
    if (Test-Path $VENV_PATH) {
        if (-not $FORCE) {
            $REBUILD = Read-Host "Virtual environment already exists. Rebuild? (y/n)"
            if ($REBUILD -eq "y") {
                Remove-Item -Recurse -Force $VENV_PATH
                python -m venv $VENV_PATH
                & "$VENV_PYTHON" -m pip install -r requirements.txt
            } else {
                Write-Host "Skipping virtual environment setup."
            }
        } else {
            Remove-Item -Recurse -Force $VENV_PATH
            python -m venv $VENV_PATH
            & "$VENV_PYTHON" -m pip install -r requirements.txt
        }
    } else {
        python -m venv $VENV_PATH
        & "$VENV_PYTHON" -m pip install -r requirements.txt
    }
}

function Create-LauncherScript {
    $launcherScriptContent = @"
`$ErrorActionPreference = 'Stop'
cd `"$PSScriptRoot`"
& `"$VENV_PYTHON`" app.py
"@

    if (Test-Path "CNB_Notepad.ps1") {
        if (-not $FORCE) {
            $REBUILD_LAUNCHER = Read-Host "Launcher script already exists. Rebuild? (y/n)"
            if ($REBUILD_LAUNCHER -eq "y") {
                Set-Content -Path "CNB_Notepad.ps1" -Value $launcherScriptContent
            } else {
                Write-Host "Skipping launcher script creation."
            }
        } else {
            Set-Content -Path "CNB_Notepad.ps1" -Value $launcherScriptContent
        }
    } else {
        Set-Content -Path "CNB_Notepad.ps1" -Value $launcherScriptContent
    }
}

# Main script starts here
Check-PythonVersion

# Get the hostname
$HOSTNAME = (hostname).Split('.')[0]

$VENV_PATH = ".venv-$HOSTNAME"
$VENV_PYTHON = Join-Path -Path $VENV_PATH -ChildPath "Scripts\python.exe"
$FORCE = $false

if ($args.Length -gt 0 -and $args[0] -eq "-f") {
    $FORCE = $true
}

Create-VirtualEnv
Create-LauncherScript

Write-Host "Setup complete. To launch the app, run: .\CNB_Notepad.ps1"
