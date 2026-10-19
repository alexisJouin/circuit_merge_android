"""Petites fonctions à compléter AVANT de lire les règles du jeu complet.

Ce fichier utilise seulement la bibliothèque standard. Les fonctions sont
indépendantes : partagez le travail, discutez les contrats et les cas limites.
Les exemples sont des spécifications ; proposez vos propres tests en plus.
Ce squelette ne remplace pas automatiquement le moteur du jeu de référence.
"""


def borner_x(x: float, gauche: float, droite: float, rayon: float) -> float:
    """Borne le centre d'un disque entre deux parois (épaisseur ignorée).

    Précondition : rayon >= 0 et droite - gauche >= 2 * rayon.
    Exemples : borner_x(-10, 0, 100, 10) == 10 ; borner_x(50, 0, 100, 10) == 50.
    """
    # TODO : identifier la valeur minimale et la valeur maximale autorisées.
    raise NotImplementedError("À compléter : borner_x")


def fusion_possible(niveau_a: int, niveau_b: int, niveau_max: int) -> bool:
    """Vrai si deux niveaux identiques peuvent créer le niveau suivant.

    Les niveaux vont de 0 à niveau_max inclus. Le cas terminal est exclu de
    cette première version. Exemples : (2,2,10) -> True ; (2,3,10) -> False.
    """
    # TODO : combiner égalité et domaine autorisé avec des expressions booléennes.
    raise NotImplementedError("À compléter : fusion_possible")


def points_creation(niveau: int) -> int:
    """Points de création : 1, 3, 6, 10… pour les niveaux 0, 1, 2, 3…

    Précondition : niveau >= 0. Il s'agit d'un nombre triangulaire.
    Exemple : points_creation(3) == 10.
    """
    # TODO : utiliser une formule ou une boucle, puis comparer leur coût.
    raise NotImplementedError("À compléter : points_creation")


def depasse_limite(y: float, rayon: float, limite: float) -> bool:
    """Vrai si le sommet du disque dépasse la ligne horizontale.

    L'axe y est orienté vers le bas. Exemple : (y=100, rayon=20, limite=90)
    dépasse, car le sommet se trouve à y=80. Toucher exactement ne dépasse pas.
    """
    # TODO : traduire le dessin du repère en comparaison.
    raise NotImplementedError("À compléter : depasse_limite")


def choisir_paires(contacts: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Choisit des paires sans réutiliser d'identifiant.

    Normaliser les paires (petit id, grand id), retirer doublons / auto-contacts,
    trier, puis garder la première paire dont les deux ids sont libres.
    Exemple : [(3,1), (2,1), (2,4), (5,6)] -> [(1,2), (5,6)].
    Ce choix glouton est déterministe ; il n'est pas nécessairement maximal.
    """
    # TODO : un ensemble permet de mémoriser les ids déjà utilisés.
    raise NotImplementedError("À compléter : choisir_paires")
