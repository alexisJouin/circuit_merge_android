#!/usr/bin/env sh
# Lance le jeu depuis son dossier, même si le répertoire courant est différent.
cd "$(dirname "$0")" || exit 1
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python main.py "$@"
fi
exec python3 main.py "$@"
