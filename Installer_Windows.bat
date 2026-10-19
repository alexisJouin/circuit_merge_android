@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo Installation de Circuit Merge dans un environnement local...

rem Reutiliser l'environnement du projet s'il fonctionne deja.
if exist ".venv\Scripts\python.exe" goto install

rem Le lanceur py est prioritaire ; python permet une installation sans lanceur.
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,15) else 1)"
if errorlevel 1 goto unsupported
py -3 -m venv .venv
if errorlevel 1 goto failure
goto install

:python_fallback
where python >nul 2>nul
if errorlevel 1 goto unsupported
python -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,15) else 1)"
if errorlevel 1 goto unsupported
python -m venv .venv
if errorlevel 1 goto failure

:install
".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,15) else 1)"
if errorlevel 1 goto unsupported
".venv\Scripts\python.exe" --version
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failure

rem pygame et pygame-ce partagent le module pygame : eviter leur coexistence.
rem La suppression concerne uniquement l'environnement local de ce projet.
".venv\Scripts\python.exe" -m pip uninstall -y pygame
if errorlevel 1 goto failure
".venv\Scripts\python.exe" -m pip install --only-binary=:all: --force-reinstall -r requirements.txt
if errorlevel 1 goto failure
".venv\Scripts\python.exe" -c "import pygame, pymunk; assert getattr(pygame, 'IS_CE', False); print('Dependances verifiees.')"
if errorlevel 1 goto failure
echo Installation terminee. Lancez Lancer_Windows.bat.
pause
exit /b 0

:unsupported
echo Python 3.10 a 3.14 est requis pour cette version. Python 3.12 est conseille.
echo Pour changer d'interpreteur, extraire le jeu dans un nouveau dossier.
echo Consultez README.md pour choisir une version de Python explicitement.
pause
exit /b 1

:failure
echo Installation impossible. Consultez README.md pour les commandes manuelles.
echo Le programme utilise des paquets precompiles : aucun compilateur C n'est requis.
pause
exit /b 1
