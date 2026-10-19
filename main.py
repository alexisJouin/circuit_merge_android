"""Point d'entrée : lancer ``python main.py`` depuis le dossier du projet.

La bibliothèque standard analyse les options avant de charger les dépendances.
Le jeu est documenté dans README.md et docs/GUIDE_NSI.md.
"""

import argparse
import os
from pathlib import Path
import sys


def main() -> None:
    """Lit les options, explique une dépendance manquante, puis lance le jeu."""
    parser = argparse.ArgumentParser(description="Circuit Merge — Jeu de fusion électronique")
    parser.add_argument("--classic", action="store_true", help="ouvrir directement l’atelier V2")
    parser.add_argument("--seed", type=int, help="graine du générateur pour les expériences NSI")
    parser.add_argument("--fresh", action="store_true", help="ignorer la partie interrompue")
    parser.add_argument("--mute", action="store_true", help="démarrer sans son")
    parser.add_argument("--demo", action="store_true", help="montage de démonstration, non sauvegardé")
    parser.add_argument("--save-file", type=Path, help="chemin de sauvegarde personnalisé")
    parser.add_argument("--screenshot", type=Path, help="exporter une image et quitter")
    parser.add_argument("--smoke-test", type=int, metavar="FRAMES", help="lancer sans écran pendant N images")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("Python 3.10 minimum requis ; Python 3.12 est conseillé.")
    if args.smoke_test is not None and args.smoke_test < 1:
        parser.error("Le nombre d'images de test doit être positif.")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    try:
        from circuit_merge.app import launch
    except ModuleNotFoundError as error:
        if error.name in ("pygame", "pymunk", "cffi", "_cffi_backend"):
            print("Dépendance manquante. Dans ce dossier, exécutez :")
            print("  python -m pip install -r requirements.txt")
            print("Puis : python main.py")
            raise SystemExit(1) from None
        raise
    if not args.classic and not args.demo:
        from circuit_merge.project_app import launch_project
        launch_project(save_path=args.save_file, muted=args.mute, screenshot=args.screenshot, smoke_test=args.smoke_test)
        return
    launch(seed=args.seed, fresh=args.fresh, muted=args.mute, demo=args.demo,
           save_path=args.save_file, screenshot=args.screenshot, smoke_test=args.smoke_test)


if __name__ == "__main__":
    if os.environ.get("ANDROID_ARGUMENT"):
        from circuit_merge.android_app import launch_android
        launch_android()
    else:
        main()
