# CNB Notepad by Clark & Burke, LLC

- **Version**: v1.0.1
- **Date**: 10.18.2024 @ 2:30 PM PST
- **Written by**: Geoff Clark of Clark & Burke, LLC

- **README.md Last Updated**: 10.18.2024

CNB Notepad is a lightweight, cross-platform text editor built with Python and PyQt6. It provides essential text editing features and a user-friendly interface for both casual and power users. The notepad supports multiple tabs, dark mode, word wrap, and more.

## Getting Started

These instructions will help you set up and run CNB Notepad on your local machine.

## Prerequisites

- Python 3.11 or higher (Python 3.11.8 recommended)

Note: The required Python packages (including PyQt6) will be automatically installed in a virtual environment during the setup process. You don't need to install them separately.

## Installation

Clone the repository and run the setup script for your operating system:

```bash
git clone https://github.com/AznIronMan/CNB_Notepad
cd CNB_Notepad
```

(Automated) - Creates a virtual environment, installs required packages, and sets up the application:

```bash
# For Windows:
./setup_cnb_notepad.bat

# For Linux/macOS:
./setup_cnb_notepad.sh
```

This setup script will:

- Create a virtual environment named `.venv-HOSTNAME`
- Install all required dependencies
- Generate a launcher script (CNB_Notepad.bat/.vbs for Windows, CNB_Notepad.sh for Linux/macOS)
- Create a desktop shortcut for easier access

(Manual) - Installs the required packages if Python 3.11+ is already installed:

```bash
pip install -r requirements.txt
```

## Usage

After installation, you can run CNB Notepad by launching the appropriate script or using the desktop shortcut:

```bash
# For Windows:
./CNB_Notepad.bat

# For Linux/macOS:
./CNB_Notepad.sh
```

The virtual environment is tied to your machine's hostname, allowing for different configurations across synced devices.

## Features

- Multi-tab interface for editing multiple text files
- Open, save, and manage text files with ease
- Basic text editing features: cut, copy, paste, undo/redo
- Find and replace text functionality
- Word wrap toggle
- Dark mode for comfortable viewing in low-light environments
- Recent files list and quick access
- Drag and drop to open files
- Word and character count display
- File status indicator (Modified/Saved/Read-Only)
- **New**: Improved database-driven settings for enhanced performance and reliability
- **New**: About dialog added for version information

## Settings

The app saves user preferences in a local database, tied to your machine's hostname. This includes:

- Last opened file
- Word wrap settings
- Recent files list
- Maximum number of recent files
- Dark mode preference
- Debug mode toggle (added in version 1.0.1)

Settings are automatically loaded on startup and saved after each session.

## Future Features

- Syntax highlighting for code files
- Plugin system for adding custom functionality
- Cloud syncing for files and preferences
- Improved file format support (Markdown, HTML, etc.)
- Collaborative editing with real-time updates

## Update Notes

### Version 1.0.1 - 10.18.2024 @ 2:30 PM PST

- **Improved**: Settings are now stored in a more efficient database format, replacing the JSON-based settings file for better performance and scalability.
- **Added**: About dialog box showing version and release date information.
- **Added**: Command-line arguments to enable or disable debug mode (`--enabledebug` / `--disabledebug`).
- **Fixed**: Multiple minor bug fixes and performance improvements.
- **Updated**: Refined the menu state logic for better handling of active/inactive options based on the current editing context.

### Version 1.0.0 - 10.17.2024 @ 12:30 PM PST

- Initial release of CNB Notepad with core functionality.
- Multi-tab support, dark mode, word wrap toggle, and file status indicators.
- Settings are stored per machine using a local database after first launch.

## Author Information

- **Author**: [Geoff Clark of Clark & Burke, LLC](https://www.cnb.llc)
- **Email**: [geoff@cnb.llc](mailto:geoff@cnb.llc)
- **Socials**:
  [GitHub @aznironman](https://github.com/aznironman)
  [IG: @cnbllc](https://instagram.com/cnbllc)
  [X: @clarkandburke](https://www.x.com/clarkandburke)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Attribution

If you use this software as a base for your own projects or fork it, we kindly request that you give credit to Clark & Burke, LLC. While not required by the license, it is appreciated and helps support the ongoing development of this project.

## Third-Party Notices

All rights reserved by their respective owners. Users must comply with the licenses and terms of service of the software being installed.