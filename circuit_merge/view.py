"""Affichage et animations ; aucune règle de fusion dans ce module.

Le rendu lit l'état du moteur. Les particules sont décoratives et ne deviennent
jamais des corps physiques. Le canevas logique est ensuite adapté à la fenêtre.
"""

from dataclasses import dataclass
import math
import random

import pygame

from . import config as C
from .art import SpriteCache, draw_component
from .engine import GameEngine
from .model import GameEvent, RoundState
from .faces import Personality
from .geometry import geometry_for, landing_y


@dataclass
class Effect:
    """Animation de fusion, décrite par son âge et sa position."""
    x: float
    y: float
    level: int
    points: int
    age: float = 0.0


@dataclass
class Particle:
    """Point décoratif avec une vitesse, sans collisions."""
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    life: float


class View:
    """Dessine l'interface et les menus ; expose les rectangles cliquables."""

    def __init__(self) -> None:
        pygame.font.init()
        self.canvas = pygame.Surface((C.WIDTH, C.HEIGHT))
        self.sprites = SpriteCache()
        # La police par défaut est distribuée avec Pygame : aucun accès réseau.
        self.fonts = {size: pygame.font.Font(None, size)
                      for size in (16, 18, 20, 22, 24, 26, 28, 32, 36, 44, 58, 70)}
        self.effects: list[Effect] = []
        self.particles: list[Particle] = []
        self.visual_rng = random.Random(42)  # indépendant des tirages de la partie
        self.goal_time = 0.0
        self.goal_label = ""
        self.personalities: dict[int, Personality] = {}
        self.preview_face = Personality(-1)
        self._projection_key = None
        self._projection_y = C.FLOOR
        self.toast = ""
        self.toast_time = 0.0
        self.buttons: dict[str, pygame.Rect] = {}
        self.background = self._make_background()

    def _make_background(self) -> pygame.Surface:
        """Circuit de fond discret, préparé une seule fois."""
        surface = pygame.Surface((C.WIDTH, C.HEIGHT))
        surface.fill(C.BG)
        for x in range(16, C.WIDTH, 28):
            for y in range(14, C.HEIGHT, 28):
                pygame.draw.circle(surface, (25, 42, 52), (x, y), 1)
        for x, y, length in ((25, 834, 110), (946, 811, 90), (200, 65, 48),
                             (922, 78, 75), (30, 458, 45)):
            points = ((x, y), (x + length, y), (x + length + 22, y - 22), (x + length + 22, y - 48))
            pygame.draw.lines(surface, (30, 61, 64), False, points, 2)
            pygame.draw.circle(surface, (37, 83, 77), points[-1], 4, 1)
        return surface

    def text(self, value: str, position: tuple[float, float], size: int = 24,
             color=C.TEXT, center: bool = False) -> pygame.Rect:
        """Affiche du texte ; renvoie son rectangle pour composer l'interface."""
        label = self.fonts[size].render(str(value), True, color)
        rect = label.get_rect(center=position) if center else label.get_rect(topleft=position)
        self.canvas.blit(label, rect)
        return rect

    def wrapped(self, value: str, x: int, y: int, width: int,
                size: int = 22, color=C.MUTED, leading: int = 25) -> int:
        """Retour automatique à la ligne, sans couper les mots."""
        words, row = value.split(), ""
        for word in words:
            candidate = (row + " " + word).strip()
            if row and self.fonts[size].size(candidate)[0] > width:
                self.text(row, (x, y), size, color)
                y += leading
                row = word
            else:
                row = candidate
        if row:
            self.text(row, (x, y), size, color)
            y += leading
        return y

    def panel(self, rect: tuple[int, int, int, int], accent=None) -> None:
        """Carte arrondie avec un fin contour."""
        pygame.draw.rect(self.canvas, C.PANEL, rect, border_radius=16)
        pygame.draw.rect(self.canvas, C.LINE, rect, 1, border_radius=16)
        if accent:
            pygame.draw.line(self.canvas, accent, (rect[0] + 20, rect[1]),
                             (rect[0] + 75, rect[1]), 3)

    def button(self, name: str, label: str, rect: tuple[int, int, int, int],
               mouse: tuple[float, float], primary: bool = False) -> None:
        """Enregistre la zone ; l'application transforme ensuite le clic en action."""
        bounds = pygame.Rect(rect)
        self.buttons[name] = bounds
        hover = bounds.collidepoint(mouse)
        color = C.TEAL if primary else ((40, 67, 78) if hover else C.PANEL_LIGHT)
        pygame.draw.rect(self.canvas, color, bounds, border_radius=10)
        if not primary:
            pygame.draw.rect(self.canvas, C.LINE, bounds, 1, border_radius=10)
        self.text(label, bounds.center, 22, C.BG if primary else C.TEXT, True)

    def notify(self, message: str, seconds: float = 3) -> None:
        self.toast, self.toast_time = message, seconds

    def consume(self, events: list[GameEvent]) -> None:
        """Convertit les événements métier en effets visuels."""
        for event in events:
            if event.kind == "merge":
                if event.uid is not None:
                    self.face_for(event.uid).react("joy", 1.2)
                self.effects.append(Effect(event.x, event.y, event.level, event.points))
                for _ in range(12):
                    angle = self.visual_rng.uniform(0, math.tau)
                    speed = self.visual_rng.uniform(65, 180)
                    self.particles.append(Particle(event.x, event.y, math.cos(angle) * speed,
                                                   math.sin(angle) * speed,
                                                   C.COMPONENTS[event.level].color,
                                                   self.visual_rng.uniform(0.35, 0.65)))
            elif event.kind in ("goal", "circuit"):
                self.goal_time = 4.0
                self.goal_label = ("SUPERCALCULATEUR ASSEMBLÉ !" if event.kind == "goal"
                                   else "CIRCUIT TERMINÉ  ·  BRAVO !")
            elif event.kind == "ouch" and event.uid is not None:
                self.face_for(event.uid).react("ouch", 0.35 + min(0.3, event.strength / 1500))

    def face_for(self, uid: int) -> Personality:
        """Crée un état visuel seulement au premier accès à cette instance."""
        if uid not in self.personalities:
            self.personalities[uid] = Personality(uid)
        return self.personalities[uid]

    def animate(self, dt: float, engine: GameEngine) -> None:
        """Vie des décorations. L'application suspend ceci pendant la pause."""
        for effect in self.effects:
            effect.age += dt
        self.effects = [e for e in self.effects if e.age < 0.8]
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 180 * dt
            p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        self.goal_time = max(0.0, self.goal_time - dt)
        self.toast_time = max(0.0, self.toast_time - dt)
        # Supprime les visages consommés par fusion, sans garder les anciens corps.
        self.personalities = {uid: face for uid, face in self.personalities.items()
                              if uid in engine.pieces}
        for uid in engine.pieces:
            self.face_for(uid).advance(dt)
        self.preview_face.advance(dt)

    def component(self, level: int, x: float, y: float, icon_half_size: int | None = None,
               angle: float = 0, alpha: int = 255,
               personality: Personality | None = None, expression: str = "idle",
               gaze=(0, 0)) -> None:
        """Dessine la silhouette et sa face ; aucune modification de la physique."""
        sprite = (self.sprites.character(level, personality, expression, gaze)
                  if icon_half_size is None else self.sprites.get(level, icon_half_size))
        if abs(angle) > 0.01:
            sprite = pygame.transform.rotozoom(sprite, -math.degrees(angle) % 360, 1)
        if alpha != 255:
            sprite = sprite.copy()
            sprite.set_alpha(alpha)
        self.canvas.blit(sprite, sprite.get_rect(center=(round(x), round(y))))

    def render(self, engine: GameEngine, best: int, mouse: tuple[float, float],
               *, mode: str | None = None, debug: bool = False,
               muted: bool = False, fps: float = 0, slow: bool = False,
               inspect_uid: int | None = None) -> pygame.Surface:
        """Compose une image complète à partir d'un état en lecture seule."""
        self.buttons.clear()
        self.canvas.blit(self.background, (0, 0))
        draw_component(self.canvas, 5, (48, 48), 39)
        self.text("CIRCUIT", (78, 26), 36)
        self.text("MERGE", (200, 26), 36, C.TEAL)
        self.text(getattr(self, "subtitle", "V2 · Des composants qui prennent vie."), (79, 66), 20, C.MUTED)
        self.button("sound", "Muet" if muted else "Son", (846, 28, 72, 40), mouse)
        self.button("pause", "Pause", (928, 28, 91, 40), mouse)
        self.button("help", "?", (1029, 28, 58, 40), mouse)
        self._left_panel(engine, best, mouse, debug, fps, slow)
        self._bucket(engine, debug, mode is None, mouse)
        self._right_panel(engine, mouse, debug, inspect_uid)
        self._effects()

        # Pied de bac avec état de disponibilité.
        self.text("ATELIER DE FUSION", (556, 823), 20, C.TEAL, True)
        instruction = "ESPACE : lâcher  ·  E / molette : tourner"
        if not engine.can_drop and engine.state is RoundState.PLAYING:
            instruction = "Composant en cours de lâcher…"
        if debug:
            instruction = "Clic droit : inspecter  ·  F2 : ralenti"
        self.text(instruction, (556, 853), 20, C.MUTED, True)
        if self.goal_time > 0:
            self.panel((333, 112, 446, 49), C.ORANGE)
            self.text(self.goal_label, (556, 137), 26, C.ORANGE, True)
        elif engine.recent_combo > 1:
            self.text(f"FUSIONS EN CHAÎNE  ·  {engine.recent_combo}", (556, 121), 22, C.ORANGE, True)
        if self.toast_time > 0:
            label = self.fonts[20].render(self.toast, True, C.TEXT)
            rect = label.get_rect(midbottom=(560, 887)).inflate(26, 16)
            pygame.draw.rect(self.canvas, (35, 56, 67), rect, border_radius=8)
            self.canvas.blit(label, label.get_rect(center=rect.center))

        if engine.state is RoundState.GAME_OVER and mode is None:
            mode = "game_over"
        if mode is not None:
            self._modal(mode, engine, best, mouse)
        return self.canvas

    def _left_panel(self, engine, best, mouse, debug, fps, slow):
        self.panel((32, 112, 244, 188), C.TEAL)
        self.text("VOTRE SCORE", (53, 134), 20, C.MUTED)
        score = f"{engine.score:,}".replace(",", " ")
        self.text(score, (51, 166), 58 if len(score) < 9 else 36)
        pygame.draw.line(self.canvas, C.LINE, (54, 235), (254, 235))
        self.text("Record", (54, 260), 22, C.MUTED)
        self.text(str(max(best, engine.score)), (185, 257), 26, C.ORANGE)

        self.panel((32, 320, 244, 170))
        self.text("VOTRE MONTAGE", (53, 340), 20, C.MUTED)
        for label, value, y in (("Composants lâchés", engine.drops, 378),
                                ("Fusions", engine.merge_count, 412),
                                ("Circuits terminés", engine.completed_circuits, 446)):
            self.text(label, (53, y), 22)
            self.text(str(value), (240, y + 8), 22, C.TEAL, True)

        self.panel((32, 510, 244, 253))
        self.text("COMMENT JOUER", (53, 532), 20, C.MUTED)
        for n, title, detail, y in (("1", "Placez", "Souris : viser. E / molette : tourner.", 570),
                                   ("2", "Lâchez", "Relâchez le clic ou appuyez sur Espace.", 633),
                                   ("3", "Fusionnez", "Deux niveaux identiques donnent le suivant.", 696)):
            pygame.draw.circle(self.canvas, C.PANEL_LIGHT, (65, y + 10), 14)
            self.text(n, (65, y + 10), 20, C.TEAL, True)
            self.text(title, (91, y - 1), 24)
            self.wrapped(detail, 91, y + 23, 164, 18, leading=19)

        self.button("new", "Nouvelle partie", (32, 785, 244, 44), mouse)
        self.button("debug", "Mode NSI : " + ("ON" if debug else "OFF"),
                    (32, 840, 244, 35), mouse)
        if debug:
            self.text(f"{fps:.0f} FPS  |  {len(engine.pieces)} corps  |  " + ("×0,25" if slow else "×1"),
                      (33, 884), 16, C.MUTED)

    def _bucket(self, engine, debug, aiming, mouse):
        inside = pygame.Rect(int(C.LEFT), int(C.WALL_TOP), int(C.RIGHT - C.LEFT), int(C.FLOOR - C.WALL_TOP))
        pygame.draw.rect(self.canvas, (15, 30, 39), inside, border_radius=12)
        for x in range(int(C.LEFT) + 20, int(C.RIGHT), 28):
            for y in range(int(C.WALL_TOP) + 20, int(C.FLOOR), 28):
                pygame.draw.circle(self.canvas, (26, 47, 55), (x, y), 1)

        danger_color = C.RED if engine.danger_ratio > 0 else (116, 91, 84)
        for x in range(int(C.LEFT) + 9, int(C.RIGHT) - 8, 17):
            pygame.draw.line(self.canvas, danger_color, (x, C.DANGER_Y), (x + 8, C.DANGER_Y), 2)
        self.text("LIMITE DE SÉCURITÉ", (C.LEFT + 14, C.DANGER_Y - 23), 16, danger_color)
        if engine.danger_ratio > 0:
            width = int((C.RIGHT - C.LEFT - 28) * engine.danger_ratio)
            pygame.draw.rect(self.canvas, C.RED, (C.LEFT + 14, C.DANGER_Y + 8, width, 3), border_radius=1)

        # Une paroi épaisse représente le diamètre des segments physiques.
        wall_points = ((C.LEFT, C.WALL_TOP), (C.LEFT, C.FLOOR),
                       (C.RIGHT, C.FLOOR), (C.RIGHT, C.WALL_TOP))
        pygame.draw.lines(self.canvas, (44, 73, 81), False, wall_points, 12)
        pygame.draw.lines(self.canvas, (102, 162, 162), False, wall_points, 2)
        for x in (C.LEFT, C.RIGHT):
            pygame.draw.circle(self.canvas, C.TEAL, (int(x), int(C.WALL_TOP)), 5)

        if aiming and engine.state is RoundState.PLAYING:
            geometry = geometry_for(engine.current_level)
            _, top, _, bottom = geometry.bounds(engine.aim_angle)
            # SAT sur les vrais polygones. Actualisation à 12 Hz pour conserver
            # de bonnes performances lorsque le bac contient beaucoup de pièces.
            key = (round(engine.aim_x), engine.aim_angle, engine.current_level,
                   int(engine.time * 12), len(engine.pieces))
            if key != self._projection_key:
                self._projection_y = landing_y(engine.current_level, engine.aim_x,
                    engine.aim_angle, engine.pieces.values(), C.DROP_Y,
                    C.FLOOR - C.WALL_THICKNESS)
                self._projection_key = key
            for y in range(round(C.DROP_Y + bottom + 8), round(self._projection_y), 15):
                pygame.draw.circle(self.canvas, (72, 115, 116), (round(engine.aim_x), y), 2)
            self.component(engine.current_level, engine.aim_x, self._projection_y,
                        angle=engine.aim_angle, alpha=48)
            self.component(engine.current_level, engine.aim_x, C.DROP_Y,
                        angle=engine.aim_angle, alpha=255 if engine.can_drop else 95,
                        personality=self.preview_face)
            self.text(C.COMPONENTS[engine.current_level].name,
                      (engine.aim_x, C.DROP_Y + top - 20), 20, C.TEXT, True)
            self.text(f"{math.degrees(engine.aim_angle):.0f}°", (engine.aim_x, C.DROP_Y + bottom + 13),
                      16, C.TEAL, True)

        for piece in engine.pieces.values():
            x, y = piece.body.position
            personality = self.face_for(piece.uid)
            expression = personality.expression(piece.body.velocity.y, piece.body.angular_velocity,
                                                  piece.overflow_time)
            # La souris en coordonnées locales : les pupilles tournent avec la tête.
            target = piece.body.world_to_local(mouse) if mouse != (-1, -1) else (0, 0)
            gaze = (max(-1, min(1, target[0] / 130)), max(-1, min(1, target[1] / 130)))
            self.component(piece.level, x, y, angle=piece.body.angle, personality=personality,
                        expression=expression, gaze=gaze)
            if debug:
                for shape in piece.shapes:
                    points = [piece.body.local_to_world(v) for v in shape.get_vertices()]
                    pygame.draw.polygon(self.canvas, (235, 250, 250), points, 1)
                pygame.draw.line(self.canvas, C.TEAL, (x - 3, y), (x + 3, y), 1)
                pygame.draw.line(self.canvas, C.TEAL, (x, y - 3), (x, y + 3), 1)
                end = (round(x + piece.body.velocity.x * 0.12), round(y + piece.body.velocity.y * 0.12))
                pygame.draw.line(self.canvas, C.RED, (round(x), round(y)), end, 2)
                self.text(f"#{piece.uid}", (x, y + 7), 16, C.TEAL, True)

    def _right_panel(self, engine, mouse, debug, inspect_uid):
        self.panel((836, 112, 252, 133), C.ORANGE)
        self.text("SUIVANT", (856, 132), 20, C.MUTED)
        self.component(engine.next_level, 878, 196, 29)
        self.wrapped(C.COMPONENTS[engine.next_level].name, 922, 176, 146, 24, C.TEXT, 26)
        self.text("Anticipez le placement", (922, 215), 16, C.MUTED)

        self.panel((836, 264, 252, 472))
        self.text("CHAÎNE D'ÉVOLUTION", (856, 286), 20, C.MUTED)
        for level, spec in enumerate(C.COMPONENTS):
            y = 333 + level * 35
            active = level <= engine.highest_level
            if level == engine.highest_level:
                pygame.draw.rect(self.canvas, C.PANEL_LIGHT, (848, y - 16, 228, 33), border_radius=7)
            self.component(level, 870, y, 13, alpha=255 if active else 80)
            self.text(f"{level + 1:02d}", (891, y - 8), 18, spec.color if active else C.MUTED)
            self.text(spec.name, (918, y - 9), 20, C.TEXT if active else (112, 136, 150))

        self.panel((836, 756, 252, 119), C.TEAL)
        piece = (engine.pieces.get(inspect_uid) or engine.piece_at(*mouse)) if debug else None
        level = piece.level if piece else engine.highest_level
        spec = C.COMPONENTS[level]
        self.text("LE SAVIEZ-VOUS ?" if not piece else f"PIÈCE #{piece.uid}  ·  NIVEAU {level + 1}",
                  (855, 772), 18, C.TEAL)
        if piece:
            self.text(f"{C.NICKNAMES[level]} · {spec.short}", (855, 796), 22)
            self.text(f"{len(piece.shapes)} polygones  |  m = {piece.body.mass:.2f}", (855, 822), 18, C.MUTED)
            self.text(f"v = {piece.body.velocity.length:.1f} px/s", (855, 846), 18, C.MUTED)
        else:
            self.wrapped(spec.role, 855, 799, 213, 20, leading=22)

    def _effects(self):
        for effect in self.effects:
            color = C.COMPONENTS[effect.level].color
            if effect.age < 0.45:
                radius = int(C.COMPONENTS[effect.level].size * (0.6 + effect.age * 1.5))
                pygame.draw.circle(self.canvas, color, (round(effect.x), round(effect.y)), max(1, radius), 2)
            self.text(f"+{effect.points}", (effect.x, effect.y - 25 - effect.age * 62), 28, C.TEXT, True)
        for p in self.particles:
            pygame.draw.circle(self.canvas, p.color, (round(p.x), round(p.y)), max(1, round(p.life * 5)))

    def _modal(self, mode, engine, best, mouse):
        shade = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        shade.fill((3, 11, 20, 210))
        self.canvas.blit(shade, (0, 0))
        self.buttons.clear()  # un menu bloque les contrôles situés derrière
        self.panel((302, 231, 516, 436), C.TEAL)

        if mode == "help":
            self.text("L'atelier Circuit Merge", (560, 276), 36, C.TEXT, True)
            self.wrapped("Lâchez les composants dans le bac. Deux composants du même niveau fusionnent dès qu'ils se touchent.",
                         339, 316, 442, 24, C.TEXT, 27)
            self.wrapped("Évitez de dépasser la limite pendant 2 secondes. Les nouveaux composants ont un court délai de tolérance.",
                         339, 398, 442, 22, C.MUTED, 25)
            self.text("Gauche / droite : viser    Espace : lâcher", (339, 470), 22)
            self.text("E / haut / molette : tourner    Bas : sens inverse", (339, 500), 22)
            self.text("P / Échap : pause    M : son    R : recommencer", (339, 530), 22)
            self.text("F1 : polygones    F2 : ralenti    F11 : plein écran", (339, 560), 22, C.TEAL)
            self.button("close", "C'est parti", (421, 601, 278, 44), mouse, True)
        elif mode == "restart":
            self.text("Nouvelle partie ?", (560, 299), 36, C.TEXT, True)
            self.wrapped("Votre record est conservé. Le montage en cours sera remplacé par un bac vide.",
                         353, 361, 414, 26, C.MUTED, 31)
            self.button("confirm_new", "Recommencer", (351, 544, 199, 49), mouse, True)
            self.button("close", "Continuer", (567, 544, 199, 49), mouse)
        elif mode == "game_over":
            self.text("Circuit saturé !", (560, 284), 44, C.ORANGE, True)
            self.text("Le bac a dépassé sa capacité.", (560, 336), 24, C.MUTED, True)
            self.text(str(engine.score), (560, 410), 70, C.TEXT, True)
            self.text(f"Record : {max(best, engine.score)}  ·  {engine.merge_count} fusions",
                      (560, 471), 24, C.MUTED, True)
            self.button("confirm_new", "Réassembler", (367, 537, 386, 49), mouse, True)
            self.text("R ou Entrée pour rejouer", (560, 623), 20, C.MUTED, True)
        elif mode == "welcome":
            draw_component(self.canvas, 7, (560, 317), 83)
            self.text("Assemblez l'informatique", (560, 399), 36, C.TEXT, True)
            self.wrapped("De la résistance au supercalculateur : visez, lâchez et faites fusionner les composants.",
                         351, 445, 418, 24, C.MUTED, 28)
            self.button("close", "Ouvrir l'atelier", (366, 547, 388, 49), mouse, True)
            self.text("Un jeu de physique à explorer en NSI", (560, 629), 20, C.TEAL, True)
        else:  # pause
            self.text("Atelier en pause", (560, 321), 44, C.TEXT, True)
            self.text("Votre montage vous attend.", (560, 389), 26, C.MUTED, True)
            self.button("close", "Reprendre", (372, 469, 376, 49), mouse, True)
            self.button("new", "Nouvelle partie", (372, 535, 376, 44), mouse)
            self.text("P ou Échap pour reprendre", (560, 623), 20, C.MUTED, True)
