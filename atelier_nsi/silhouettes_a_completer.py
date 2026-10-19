"""Atelier V2 sans Pygame : compléter les quatre fonctions.

Angles en radians, coordonnées écran. Les exemples sont les résultats attendus.
Les NotImplementedError sont intentionnelles : ceci est le squelette élèves.
"""
from math import cos, sin


def tourner(point, angle):
    """(1, 0) tourné de pi/2 donne approximativement (0, 1)."""
    # TODO : appliquer la matrice de rotation.
    raise NotImplementedError


def limites(sommets):
    """[(1, 2), (4, 2), (4, 6)] -> (1, 2, 4, 6). Liste non vide."""
    # TODO : calculer min_x, min_y, max_x, max_y.
    raise NotImplementedError


def borner_visee(x, gauche_locale, droite_locale, gauche_bac, droite_bac):
    """Borner x pour que x+gauche_locale et x+droite_locale restent dans le bac."""
    # TODO : déterminer l'intervalle autorisé pour le centre.
    raise NotImplementedError


def choisir_expression(choc, fusion, vitesse):
    """Priorités : fusion -> joie, choc -> grimace, vitesse>200 -> surprise, repos."""
    # TODO : conditions ordonnées.
    raise NotImplementedError
