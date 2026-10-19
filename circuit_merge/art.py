"""Composants reconnaissables et personnages, sans image externe.

La silhouette vient de geometry.py : mêmes sommets pour le dessin et les
collisions. Bandes, puces, ventilateurs et visages restent décoratifs. Les
bases sont préparées à résolution double ; seuls les visages sont redessinés.
"""
import math
import pygame
from .config import COMPONENTS
from .faces import Personality, draw_face
from .geometry import geometry_for

INK = (27, 39, 53)
GOLD = (247, 205, 112)
SILVER = (196, 219, 225)
GREEN = (45, 126, 103)


def paint_base(surface: pygame.Surface, level: int, center: tuple[float, float],
               scale: float = 1.0) -> None:
    """Dessine la silhouette partagée, puis les détails internes des boîtiers."""
    geometry = geometry_for(level)
    color = COMPONENTS[level].color
    materials = {"body": color, "silver": SILVER, "gold": GOLD, "board": GREEN,
                 "ink": INK, "rim": tuple(round(c * 0.65) for c in color),
                 "rack": (62, 82, 100)}

    def local_pt(x, y):
        return round(center[0] + x * scale), round(center[1] + y * scale)

    def pt(x, y):
        return local_pt(*geometry.local(x, y))

    def line(col, a, b, width=0.025):
        pygame.draw.line(surface, col, pt(*a), pt(*b), max(1, round(width * geometry.size * scale)))

    def box(col, x, y, w, h, radius=0.035, border=0):
        rect = pygame.Rect(*pt(x, y), max(1, round(w * geometry.size * scale)),
                           max(1, round(h * geometry.size * scale)))
        pygame.draw.rect(surface, col, rect, max(0, round(border * geometry.size * scale)),
                         border_radius=max(0, round(radius * geometry.size * scale)))

    def circle(col, x, y, r, border=0):
        pygame.draw.circle(surface, col, pt(x, y), max(1, round(r * geometry.size * scale)),
                           max(0, round(border * geometry.size * scale)))

    # Les petites parties sont dessinées avant le corps : jointures lisibles.
    for part in geometry.parts:
        points = [local_pt(x, y) for x, y in part.vertices]
        fill = materials[part.material]
        pygame.draw.polygon(surface, fill, points)
        pygame.draw.polygon(surface, (21, 34, 44), points, max(1, round(scale)))
        if part.material not in ("gold", "silver"):
            a, b = points[0], points[1]
            pygame.draw.line(surface, tuple(min(255, c + 30) for c in fill), a, b, max(1, round(scale)))

    if level == 0:
        for x, col in ((-0.7, (109, 63, 43)), (0.61, GOLD)):
            box(col, x, -0.45, 0.1, 0.9, 0.01)
    elif level == 1:
        line((255, 213, 222), (-0.38, -0.38), (-0.38, -0.15), 0.10)
        circle((255, 220, 223), -0.17, -0.63, 0.075)
    elif level == 2:
        box((66, 117, 149), -0.51, -0.86, 1.02, 0.27, 0.08)
        line(SILVER, (-0.34, -0.81), (0.33, -0.65))
        line(SILVER, (-0.34, -0.65), (0.33, -0.81))
        box((188, 226, 242), 0.42, -0.48, 0.10, 1.10, 0.025)
        for y in (-0.31, 0.08, 0.47):
            line((74, 114, 139), (0.435, y), (0.50, y))
    elif level == 3:
        box((66, 69, 88), -0.62, -0.55, 1.24, 0.85, 0.06)
        line((199, 179, 247), (-0.23, -0.63), (0.23, -0.63), 0.04)
    elif level == 4:
        box((52, 81, 81), -0.59, -0.57, 1.18, 1.17, 0.05)
        circle(COMPONENTS[level].color, -0.44, -0.72, 0.065)
        line((94, 129, 120), (-0.22, 0.69), (0.22, 0.69), 0.035)
    elif level == 5:
        for x in (-0.66, -0.4, -0.14, 0.12, 0.38, 0.64):
            circle(GOLD, x, -0.63, 0.045)
            circle(GOLD, x, 0.64, 0.045)
        box(INK, -0.53, -0.43, 1.12, 0.91, 0.08)
        box(SILVER, -0.95, -0.16, 0.2, 0.32)
        circle((113, 248, 181), 0.68, -0.36, 0.055)
        line((110, 197, 156), (0.61, 0.23), (0.72, 0.23))
        line((110, 197, 156), (0.72, 0.23), (0.72, 0.5))
    elif level == 6:
        for x in (-1.21, -0.71, 0.26, 0.76):
            box(INK, x, -0.25, 0.43, 0.43, 0.025)
        box((50, 77, 70), -0.27, -0.28, 0.54, 0.53, 0.025)
        line((117, 216, 162), (-1.27, 0.25), (1.27, 0.25))
        for x in (-1.15, -0.98, -0.81, -0.64, -0.47, -0.3, 0.19, 0.36, 0.53, 0.7, 0.87, 1.04):
            line((122, 93, 44), (x, 0.35), (x, 0.46), 0.014)
    elif level == 7:
        box(SILVER, -0.74, -0.74, 1.48, 1.48, 0.08)
        box((227, 239, 240), -0.63, -0.62, 1.26, 1.24, 0.05)
        line((149, 179, 195), (-0.38, -0.5), (0.38, -0.5))
        line((103, 152, 183), (-0.30, 0.52), (0.30, 0.52))
    elif level == 8:
        box(INK, -1.17, -0.56, 2.34, 1.03, 0.08)
        for x in (-0.76, 0.76):
            circle((77, 93, 111), x, -0.06, 0.37)
            circle((20, 30, 42), x, -0.06, 0.30)
            for a in range(6):
                angle = a * math.tau / 6
                line((157, 174, 192), (x + math.cos(angle) * 0.10, -0.06 + math.sin(angle) * 0.10),
                     (x + math.cos(angle + 0.45) * 0.27, -0.06 + math.sin(angle + 0.45) * 0.27), 0.065)
            circle(color, x, -0.06, 0.075)
        box((67, 52, 85), -0.35, -0.47, 0.70, 0.82, 0.04)
    elif level == 9:
        for a, b in (((-0.66, 0.12), (-0.66, 0.86)), ((-0.66, 0.86), (0.68, 0.86)),
                     ((0.05, 0.23), (0.05, 0.65)), ((0.05, 0.65), (0.66, 0.65))):
            line((129, 205, 166), a, b)
        box(SILVER, -0.75, -0.78, 1.05, 1.06, 0.05)
        box((233, 238, 220), -0.67, -0.69, 0.89, 0.88, 0.04)
        for x in (0.43, 0.65):
            box(INK, x, -0.75, 0.12, 1.03, 0.025)
            box(GOLD, x + 0.03, -0.65, 0.04, 0.81, 0.01)
        for y in (0.48, 0.70):
            box((238, 221, 158), -0.30, y, 0.94, 0.09, 0.025)
        for x, y in ((-0.73, -0.94), (0.74, -0.94), (-0.73, 0.94), (0.74, 0.94)):
            circle(GOLD, x, y, 0.035)
    else:
        for x in (-1.21, -0.35, 0.51):
            box(INK, x + 0.07, -1.0, 0.56, 1.98, 0.03)
            for y in (-0.88, 0.14, 0.38, 0.62, 0.86):
                box((95, 120, 139), x + 0.12, y, 0.46, 0.13, 0.025)
                circle((111, 247, 172), x + 0.50, y + 0.065, 0.019)
            if x != -0.35:
                for y in (-0.60, -0.36, -0.12):
                    box((95, 120, 139), x + 0.12, y, 0.46, 0.13, 0.025)
        for x in (-0.88, 0.85):
            circle(GOLD, x, 0.98, 0.024)


class SpriteCache:
    """Bases doubles mises en cache ; assemblage de la face à chaque image."""
    def __init__(self) -> None:
        self.bases: dict[int, pygame.Surface] = {}
        self.icons: dict[tuple[int, int], pygame.Surface] = {}
        self.neutral = Personality(0)

    def base(self, level: int) -> pygame.Surface:
        """Surface centrée exactement sur l'origine mécanique du composant."""
        if level not in self.bases:
            extent = math.ceil(geometry_for(level).render_extent)
            side = extent * 4  # côté pair : origine au centre, même après réduction
            surface = pygame.Surface((side, side), pygame.SRCALPHA)
            paint_base(surface, level, (side / 2, side / 2), 2)
            self.bases[level] = surface
        return self.bases[level]

    def character(self, level: int, personality: Personality | None = None,
                  expression: str = "idle", gaze=(0, 0)) -> pygame.Surface:
        """Sprite à taille physique : 1 pixel logique = 1 unité Pymunk."""
        surface = self.base(level).copy()
        center = surface.get_width() / 2, surface.get_height() / 2
        draw_face(surface, geometry_for(level).face, center, personality or self.neutral,
                  expression, gaze, 2)
        return pygame.transform.smoothscale(surface, (surface.get_width() // 2, surface.get_height() // 2))

    def get(self, level: int, half_side: int | None = None) -> pygame.Surface:
        """Icône statique ; ``half_side`` est ici un demi-côté D'AFFICHAGE seulement.

        Sans paramètre, renvoie un personnage à taille réelle. Ce réglage
        concerne uniquement les miniatures ; aucune collision circulaire.
        """
        if half_side is None:
            return self.character(level)
        key = level, half_side
        if key not in self.icons:
            surface = self.character(level)
            surface = surface.subsurface(surface.get_bounding_rect()).copy()
            factor = 2 * half_side / max(surface.get_size())
            self.icons[key] = pygame.transform.smoothscale(surface,
                (max(1, round(surface.get_width() * factor)), max(1, round(surface.get_height() * factor))))
        return self.icons[key]


def draw_component(surface: pygame.Surface, level: int, center: tuple[int, int], size: int) -> None:
    """Illustration statique du titre et du menu d'accueil."""
    sprite = _title_cache.get(level, size // 2)
    surface.blit(sprite, sprite.get_rect(center=center))


_title_cache = SpriteCache()
