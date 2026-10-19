"""Silhouettes communes au dessin, aux collisions et à l'aide de visée.

Un composant = UN corps rigide + PLUSIEURS polygones convexes. Pymunk ne sait
pas représenter directement un polygone concave : sa coque convexe remplirait
les espaces entre les pattes. On décompose donc la silhouette en pièces
convexes, attachées au même corps. Les pattes ne sont pas articulées.

Les coordonnées de conception sont des multiples de ``ComponentSpec.size``.
On recentre ensuite tous les sommets autour du centre de masse calculé. Les
densités sont des choix de jeu, pas des mesures de composants électroniques.
"""

from dataclasses import dataclass
from functools import lru_cache
import math

from .config import COMPONENTS

Point = tuple[float, float]
Polygon = tuple[Point, ...]


def bevel_box(x: float, y: float, width: float, height: float,
              bevel: float = 0.0) -> Polygon:
    """Rectangle convexe aux coins coupés ; aucun arrondi invisible ajouté."""
    b = min(bevel, width / 2, height / 2)
    if b <= 0:
        return ((x, y), (x + width, y), (x + width, y + height), (x, y + height))
    return ((x + b, y), (x + width - b, y), (x + width, y + b),
            (x + width, y + height - b), (x + width - b, y + height),
            (x + b, y + height), (x, y + height - b), (x, y + b))


def area_and_centroid(vertices: Polygon) -> tuple[float, Point]:
    """Aire et barycentre par la formule du lacet (sommets dans leur ordre).

    Le signe de l'aire dépend de l'ordre des sommets ; l'aire retournée est
    positive. Exercice NSI : retrouver le résultat sur un rectangle décentré.
    """
    cross_sum = cx = cy = 0.0
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        cross = a[0] * b[1] - b[0] * a[1]
        cross_sum += cross
        cx += (a[0] + b[0]) * cross
        cy += (a[1] + b[1]) * cross
    if abs(cross_sum) < 1e-12:
        raise ValueError("Polygone sans aire")
    return abs(cross_sum) / 2, (cx / (3 * cross_sum), cy / (3 * cross_sum))


def transform(vertices: Polygon, angle: float, position: Point = (0, 0)) -> Polygon:
    """Repère local -> repère du bac (radians, y orienté vers le bas)."""
    c, s = math.cos(angle), math.sin(angle)
    x, y = position
    return tuple((x + c * vx - s * vy, y + s * vx + c * vy) for vx, vy in vertices)


@dataclass(frozen=True)
class Part:
    """Un polygone convexe, son matériau graphique et sa masse relative."""
    vertices: Polygon
    material: str
    mass: float


@dataclass(frozen=True)
class FaceLayout:
    """Zone locale réservée au visage : centre et largeur/hauteur utiles."""
    center: Point
    width: float
    height: float


@dataclass(frozen=True)
class Geometry:
    """Description immuable ; les corps physiques n'appartiennent pas au cache."""
    parts: tuple[Part, ...]
    offset: Point              # centre de masse dans le repère de conception
    face: FaceLayout
    size: float

    @property
    def mass(self) -> float:
        return sum(p.mass for p in self.parts)

    def local(self, x: float, y: float) -> Point:
        """Convertit un point de conception, pour les détails graphiques."""
        return x * self.size - self.offset[0], y * self.size - self.offset[1]

    def bounds(self, angle: float = 0.0) -> tuple[float, float, float, float]:
        """Boîte englobante des sommets tournés : gauche, haut, droite, bas."""
        points = [v for part in self.parts for v in transform(part.vertices, angle)]
        return (min(v[0] for v in points), min(v[1] for v in points),
                max(v[0] for v in points), max(v[1] for v in points))

    @property
    def render_extent(self) -> float:
        """Demi-côté du sprite, pour le dessin seulement (aucun collider)."""
        return max(abs(v) for v in self.bounds()) + 3


@lru_cache(maxsize=len(COMPONENTS))
def geometry_for(level: int) -> Geometry:
    """Catalogue des onze silhouettes, recalculé seulement au premier accès.

    Les pattes ont une épaisseur minimale lisible et stable en simulation.
    Les détails imprimés, les ventilateurs et les visages restent décoratifs.
    """
    size = COMPONENTS[level].size
    raw: list[tuple[Polygon, str, float]] = []

    def poly(vertices: Polygon, material: str = "body", density: float = 1.0):
        raw.append((tuple((x * size, y * size) for x, y in vertices), material, density))

    def box(x, y, w, h, material="body", bevel=0.04, density=1.0):
        poly(bevel_box(x, y, w, h, bevel), material, density)

    if level == 0:  # résistance : boîtier horizontal, deux fils
        box(-1.35, -0.125, 0.45, 0.25, "silver", 0.03, 1.4)
        box(0.9, -0.125, 0.45, 0.25, "silver", 0.03, 1.4)
        box(-0.9, -0.55, 1.8, 1.1, bevel=0.17)
        face = (0, -0.03, 1.05, 0.8)
    elif level == 1:  # LED : dôme polygonal et deux pattes de longueur différente
        for x, length in ((-0.30, 0.78), (0.13, 0.62)):
            box(x, 0.47, 0.17, length, "silver", 0.03, 1.4)
        dome = tuple((0.65 * math.cos(math.pi + i * math.pi / 8),
                      -0.25 + 0.65 * math.sin(math.pi + i * math.pi / 8))
                     for i in range(9))
        poly(dome + ((0.65, 0.4), (-0.65, 0.4)))
        box(-0.74, 0.4, 1.48, 0.14, "rim")
        face = (0, -0.05, 0.98, 0.78)
    elif level == 2:  # condensateur : cylindre vu de face, haut chanfreiné
        for x, length in ((-0.34, 0.55), (0.2, 0.44)):
            box(x, 0.82, 0.14, length, "silver", 0.03, 1.4)
        box(-0.62, -1.0, 1.24, 1.82, bevel=0.15)
        face = (-0.05, -0.08, 0.90, 0.92)
    elif level == 3:  # transistor : boîtier aplati et trois pattes
        for x, length in ((-0.54, 0.58), (-0.065, 0.72), (0.41, 0.58)):
            box(x, 0.45, 0.13, length, "silver", 0.035, 1.4)
        poly(((-0.78, 0.45), (-0.78, -0.25), (-0.56, -0.72),
              (-0.25, -0.91), (0.25, -0.91), (0.56, -0.72),
              (0.78, -0.25), (0.78, 0.45)), "ink")
        face = (0, -0.18, 1.16, 0.85)
    elif level == 4:  # puce DIP : quatre broches de chaque côté
        for y in (-0.62, -0.26, 0.1, 0.46):
            box(-1.02, y, 0.3, 0.14, "gold", density=1.3)
            box(0.72, y, 0.3, 0.14, "gold", density=1.3)
        box(-0.72, -0.88, 1.44, 1.76, "ink", 0.10)
        face = (0, 0.06, 1.03, 1.0)
    elif level == 5:  # carte à microcontrôleur et prise USB
        box(-0.86, -0.8, 1.72, 1.6, "board", 0.12)
        box(-1.03, -0.21, 0.17, 0.47, "silver", density=1.4)
        face = (0.03, 0.02, 0.95, 0.82)
    elif level == 6:  # RAM : longue et plate, encoche dans les contacts
        box(-1.4, -0.36, 2.8, 0.69, "board", 0.06)
        box(-1.27, 0.33, 1.15, 0.15, "gold", 0.015, 1.3)
        box(0.12, 0.33, 1.15, 0.15, "gold", 0.015, 1.3)
        face = (0, -0.015, 0.90, 0.50)
    elif level == 7:  # CPU : substrat carré et broches sur quatre côtés
        for t in (-0.62, -0.12, 0.38):
            box(t, -1.04, 0.20, 0.14, "gold", density=1.3)
            box(t, 0.9, 0.20, 0.14, "gold", density=1.3)
            box(-1.04, t, 0.14, 0.20, "gold", density=1.3)
            box(0.9, t, 0.14, 0.20, "gold", density=1.3)
        box(-0.9, -0.9, 1.8, 1.8, "board", 0.10)
        face = (0, 0.02, 1.05, 0.93)
    elif level == 8:  # GPU : plaque rectangulaire, équerre et connecteur
        box(-1.25, -0.63, 2.5, 1.18, "board", 0.1)
        box(-1.37, -0.73, 0.12, 1.47, "silver", density=1.4)
        box(-0.97, 0.55, 1.6, 0.14, "gold", 0.02, 1.3)
        face = (0, -0.02, 0.67, 0.67)
    elif level == 9:  # carte mère et trois prises à gauche
        box(-0.85, -1.05, 1.7, 2.1, "board", 0.08)
        for y in (-0.78, -0.3, 0.18):
            box(-1.05, y, 0.20, 0.29, "silver", density=1.4)
        face = (-0.22, -0.25, 0.95, 0.85)
    else:  # trois baies reliées par un socle fin ; les deux fentes restent vides
        for x in (-1.21, -0.35, 0.51):
            box(x, -1.1, 0.7, 2.2, "rack", 0.05)
        box(-0.86, 1.1, 1.72, 0.08, "gold", 0.02, 1.3)
        face = (0, -0.32, 0.56, 0.76)

    masses, centers = [], []
    for vertices, _material, density in raw:
        area, center = area_and_centroid(vertices)
        masses.append(area * density / 500)  # unité de masse arbitraire de jeu
        centers.append(center)
    total = sum(masses)
    ox = sum(m * c[0] for m, c in zip(masses, centers)) / total
    oy = sum(m * c[1] for m, c in zip(masses, centers)) / total
    parts = tuple(Part(tuple((x - ox, y - oy) for x, y in v), material, mass)
                  for (v, material, _), mass in zip(raw, masses))
    fx, fy, fw, fh = face
    return Geometry(parts, (ox, oy), FaceLayout((fx * size - ox, fy * size - oy),
                                               fw * size, fh * size), size)


def vertical_contact(moving: Polygon, fixed: Polygon) -> float | None:
    """Distance du premier contact si ``moving`` descend sans tourner (SAT).

    Sur chaque normale d'arête, les projections doivent se recouvrir. La
    projection mobile évolue de ``distance * normale.y``. On intersecte les
    intervalles de distances autorisées pour toutes les normales. Le plus
    grand instant d'entrée est le premier contact, si l'intersection existe.
    None signifie que les deux polygones ne se rencontreront jamais.
    Ce calcul ne prédit ni rebond, ni rotation, ni déplacement des voisins.
    """
    entry, leave = 0.0, math.inf
    for vertices in (moving, fixed):
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            nx, ny = -(b[1] - a[1]), b[0] - a[0]
            av = [x * nx + y * ny for x, y in moving]
            bv = [x * nx + y * ny for x, y in fixed]
            amin, amax, bmin, bmax = min(av), max(av), min(bv), max(bv)
            if abs(ny) < 1e-10:
                if amax < bmin or bmax < amin:
                    return None
                continue
            t1, t2 = (bmin - amax) / ny, (bmax - amin) / ny
            entry, leave = max(entry, min(t1, t2)), min(leave, max(t1, t2))
            if entry > leave + 1e-8:
                return None
    return entry if leave >= 0 else None


def landing_y(level: int, x: float, angle: float, pieces, start_y: float,
              floor_y: float) -> float:
    """Position verticale d'un fantôme ayant exactement la silhouette physique.

    Un test de boîtes horizontales écarte les voisins éloignés avant le SAT.
    ``pieces`` est un itérable de Piece ; pas de dépendance au moteur ici.
    """
    geometry = geometry_for(level)
    xmin, _ymin, xmax, ymax = geometry.bounds(angle)
    distance = max(0.0, floor_y - start_y - ymax)
    polygons = [transform(p.vertices, angle, (x, start_y)) for p in geometry.parts]
    for piece in pieces:
        bb = piece.bounds
        if x + xmax < bb.left or x + xmin > bb.right:
            continue
        for fixed_shape in piece.shapes:
            fixed = tuple(tuple(piece.body.local_to_world(v)) for v in fixed_shape.get_vertices())
            for moving in polygons:
                contact = vertical_contact(moving, fixed)
                if contact is not None:
                    distance = min(distance, contact)
    return start_y + distance
