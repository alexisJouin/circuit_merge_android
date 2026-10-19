@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" main.py
) else (
  echo L'environnement du jeu est absent. Lancez Installer_Windows.bat.
  pause
  exit /b 1
)
if errorlevel 1 pause
