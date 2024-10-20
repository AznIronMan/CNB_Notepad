# In Progress - Version: 1.0.2

## Completed Changes

- Replaced .bat and .vbs setup files with a more efficient PowerShell (.ps1) setup script
- Resolved issue with phantom find and replace fields appearing on the startup screen in the Windows version
- Corrected functionality of the "Reopen Last" feature to ensure proper behavior

## Bugs to Fix

- Resolve issue with single replace functionality
- Investigate and fix application freezing on Windows when opening from recent files
- Fix crash of find and find/replace window on macOS

## Feature Improvements in Progress

- Ensure "reopen last" feature is working correctly
- Implement SQLite temporary cache for "untitled" files and unsaved changes
  - Add periodic snapshot functionality for unsaved work
  - Design and implement cache structure for efficient retrieval
  - Ensure proper cleanup of temporary cache files

## To Report Bugs or Request Features

To report other bugs or request features, please email the developer as mentioned in the [README.md](README.md).
