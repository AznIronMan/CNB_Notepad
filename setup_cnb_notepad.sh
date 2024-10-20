#!/bin/bash
check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [ "$(printf '%s\n' "3.11" "$python_version" | sort -V | head -n1)" = "3.11" ]; then
            return 0
        fi
    fi
    echo "Error: Python 3.11 or higher is required. Please install Python 3 (3.11.8 recommended)."
    exit 1
}
check_python_version
HOSTNAME=$(hostname -s)
VENV_PATH=".venv-$HOSTNAME"
FORCE=false
if [ "$1" = "-f" ]; then
    FORCE=true
fi
if [ -d "$VENV_PATH" ] && [ "$FORCE" = false ]; then
    read -p "Virtual environment already exists. Rebuild? (y/n): " REBUILD
    if [ "$REBUILD" != "y" ]; then
        echo "Skipping virtual environment setup."
    else
        rm -rf "$VENV_PATH"
        python3 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        pip install -r requirements.txt
        deactivate
    fi
elif [ ! -d "$VENV_PATH" ] || [ "$FORCE" = true ]; then
    [ -d "$VENV_PATH" ] && rm -rf "$VENV_PATH"
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install -r requirements.txt
    deactivate
fi
LAUNCHER_SH=$(sqlite3 CNB_Notepad.resources "SELECT value FROM resources WHERE key='launcher_sh'" | sed "s/{HOSTNAME}/$HOSTNAME/g")
if [ -f "CNB_Notepad.sh" ] && [ "$FORCE" = false ]; then
    read -p "Launcher script already exists. Rebuild? (y/n): " REBUILD_LAUNCHER
    if [ "$REBUILD_LAUNCHER" != "y" ]; then
        echo "Skipping launcher script creation."
    else
        echo "$LAUNCHER_SH" >CNB_Notepad.sh
        chmod +x CNB_Notepad.sh
    fi
elif [ ! -f "CNB_Notepad.sh" ] || [ "$FORCE" = true ]; then
    echo "$LAUNCHER_SH" >CNB_Notepad.sh
    chmod +x CNB_Notepad.sh
fi
echo "Setup complete. To launch the app, run: ./CNB_Notepad.sh"

# Determine the OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    # Create the shell script content
    SHELL_SCRIPT_CONTENT=$(
        cat <<EOF
#!/bin/bash
cd "$PWD"
source ".venv-$HOSTNAME/bin/activate"
python app.py
deactivate
EOF
    )

    # Create the shell script file
    echo "$SHELL_SCRIPT_CONTENT" >"run_app.sh"
    chmod +x "run_app.sh"

    # Create the AppleScript content
    APPLESCRIPT_CONTENT=$(
        cat <<EOF
on run
    do shell script "bash '$PWD/run_app.sh'"
end run
EOF
    )

    # Save the AppleScript to a file
    echo "$APPLESCRIPT_CONTENT" >"CNB_Notepad.applescript"

    # Compile the AppleScript into an app
    osacompile -o "CNB Notepad.app" "CNB_Notepad.applescript"

    # Clean up temporary files
    rm "CNB_Notepad.applescript"

    if [ -d "CNB Notepad.app" ]; then
        echo "macOS application created: CNB Notepad.app"
    else
        echo "Error: Failed to create macOS application"
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    # Create .desktop file
    DESKTOP_ENTRY=$(sqlite3 CNB_Notepad.resources "SELECT value FROM resources WHERE key='linux_desktop'" | sed "s/{HOSTNAME}/$HOSTNAME/g" | sed "s|{ICON_PATH}|$PWD/icon.png|g")
    echo "$DESKTOP_ENTRY" >"$HOME/.local/share/applications/cnb-notepad.desktop"
    chmod +x "$HOME/.local/share/applications/cnb-notepad.desktop"
    echo "Linux .desktop file created: $HOME/.local/share/applications/cnb-notepad.desktop"
fi
