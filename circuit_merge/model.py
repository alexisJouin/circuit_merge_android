"""Structures de données partagées ; pas de fenêtre ni de son dans ce module."""

from dataclasses import dataclass
from enum import Enum, auto

import pymunk

from .geometry import Geometry, geometry_for


class RoundState(Enum):
    """Deux états métier. La pause et les menus appartiennent à l'interface."""

    PLAYING = auto()
    GAME_OVER = auto()


@dataclass
class Piece:
    """Un composant dans le bac.

    ``uid`` identifie UNE instance, ``level`` son type (indice commençant à 0).
    Deux pièces de même niveau ont donc des identifiants différents.
    ``born_at`` et ``overflow_time`` utilisent le temps de simulation.
    """

    uid: int
    level: int
    body: pymunk.Body
    shapes: tuple[pymunk.Poly, ...]
    born_at: float
    overflow_time: float = 0.0

    @property
    def geometry(self) -> Geometry:
        """Tous les exemplaires d'un niveau partagent la même description."""
        return geometry_for(self.level)

    @property
    def bounds(self) -> pymunk.BB:
        """Union des boîtes des polygones tournés, actualisée même hors step."""
        boxes = [shape.cache_bb() for shape in self.shapes]
        return pymunk.BB(min(b.left for b in boxes), min(b.bottom for b in boxes),
                         max(b.right for b in boxes), max(b.top for b in boxes))


@dataclass(frozen=True)
class GameEvent:
    """Message du moteur vers l'affichage / le son, sans dépendance à Pygame.

    Exemples : ``merge`` crée un anneau et joue une note ; ``impact`` permet
    un bruit discret. L'interface consomme ces événements à chaque image.
    """

    kind: str
    x: float = 0.0
    y: float = 0.0
    level: int = 0
    points: int = 0
    combo: int = 0
    uid: int | None = None      # destinataire d'une expression, si applicable
    strength: float = 0.0       # choc exprimé comme variation de vitesse
