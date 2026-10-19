"""Personnalités animées : machine à états sans effet sur la physique.

Le moteur émet ``ouch`` et ``merge`` ; la vue choisit une expression et dessine
dans le repère LOCAL du composant. Le sprite entier tourne ensuite. Chaque
clignement utilise un générateur indépendant des tirages de la partie.
"""

from dataclasses import dataclass, field
import math
import random

import pygame

from .geometry import FaceLayout

INK = (22, 31, 42)
WHITE = (250, 254, 250)
CHEEK = (255, 132, 143)


@dataclass
class Personality:
    """État d'une instance : calendrier des yeux et réaction temporaire.

    Priorités : fusion > choc > dépassement > rotation > chute > repos.
    Les grimaces spontanées sont rares ; chaque identifiant a son calendrier.
    Le temps visuel avance seulement lorsque l'application est active.
    """
    uid: int
    time: float = 0.0
    reaction: str = ""
    reaction_until: float = 0.0
    blink_at: float = field(init=False)
    playful_at: float = field(init=False)
    rng: random.Random = field(init=False, repr=False)
    BLINK_DURATION = 0.17

    def __post_init__(self) -> None:
        self.rng = random.Random(9137 + self.uid * 7919)
        self.blink_at = self.rng.uniform(0.6, 3.7)
        self.playful_at = self.rng.uniform(7.0, 14.0)

    def advance(self, dt: float) -> None:
        """Avance sur demande de l'application, jamais pendant le dessin."""
        self.time += dt
        while self.time >= self.blink_at + self.BLINK_DURATION:
            self.blink_at += self.rng.uniform(2.2, 5.3)
        if self.time >= self.playful_at:
            self.react("playful", 0.65)
            self.playful_at = self.time + self.rng.uniform(9.0, 17.0)

    def react(self, expression: str, duration: float) -> None:
        """Protège le sourire de fusion contre les chocs juste après création."""
        if self.reaction == "joy" and self.time < self.reaction_until and expression != "joy":
            return
        if expression == "playful" and self.time < self.reaction_until:
            return
        self.reaction, self.reaction_until = expression, self.time + duration

    @property
    def eye_open(self) -> float:
        """1 = ouverts ; 0 = fermés au milieu du clignement."""
        t = self.time - self.blink_at
        if not 0 <= t <= self.BLINK_DURATION:
            return 1.0
        return abs(2 * t / self.BLINK_DURATION - 1)

    def expression(self, speed_y: float = 0, spin: float = 0, overflow: float = 0) -> str:
        """État visible dérivé du mouvement, avec réactions prioritaires."""
        if self.time < self.reaction_until:
            if self.reaction != "playful" or (speed_y < 160 and abs(spin) < 2 and overflow == 0):
                return self.reaction
        if overflow > 0:
            return "worried"
        if abs(spin) > 2.8:
            return "dizzy"
        if speed_y > 200:
            return "surprised"
        return "idle"


def draw_face(surface: pygame.Surface, layout: FaceLayout, origin: tuple[float, float],
              personality: Personality, expression: str = "idle",
              gaze: tuple[float, float] = (0, 0), scale: float = 1.0) -> None:
    """Yeux, sourcils, bouche et joues en dessin vectoriel.

    ``gaze`` est un vecteur normalisé local (par exemple vers la souris).
    Cette fonction lit l'état : elle n'avance ni le temps ni les générateurs.
    ``scale`` sert au dessin à résolution double et aux miniatures.
    """
    cx = origin[0] + layout.center[0] * scale
    cy = origin[1] + layout.center[1] * scale
    w, h = layout.width * scale, layout.height * scale
    eye_r = max(2 * scale, min(w * 0.15, h * 0.23))
    eye_dx = w * 0.255
    eye_y, mouth_y = cy - h * 0.16, cy + h * 0.25
    thick = max(1, round(1.25 * scale if w < 45 * scale else 1.8 * scale))

    def line(points, color=INK, width=thick):
        pygame.draw.lines(surface, color, False, [(round(x), round(y)) for x, y in points], width)

    if expression in ("idle", "joy", "playful"):
        for sign in (-1, 1):
            rect = pygame.Rect(0, 0, max(2, round(w * 0.13)), max(2, round(h * 0.09)))
            rect.center = round(cx + sign * w * 0.37), round(cy + h * 0.08)
            pygame.draw.ellipse(surface, CHEEK, rect)

    for side in (-1, 1):
        ex = cx + side * eye_dx
        if expression == "dizzy":
            points = []
            for i in range(25):
                a = i * math.tau / 12
                r = eye_r * (0.17 + i / 31)
                points.append((ex + math.cos(a) * r, eye_y + math.sin(a) * r))
            line(points, WHITE, thick + 1)
            line(points)
        elif expression == "ouch":
            line(((ex - side * eye_r, eye_y - eye_r * 0.6),
                  (ex + side * eye_r * 0.25, eye_y),
                  (ex - side * eye_r, eye_y + eye_r * 0.6)))
        elif expression == "joy":
            line(((ex - eye_r, eye_y + eye_r * 0.3), (ex, eye_y - eye_r * 0.55),
                  (ex + eye_r, eye_y + eye_r * 0.3)))
        elif expression == "playful" and side == 1:
            line(((ex - eye_r, eye_y), (ex, eye_y + eye_r * 0.15), (ex + eye_r, eye_y - eye_r * 0.2)))
        elif personality.eye_open < 0.18:
            line(((ex - eye_r, eye_y), (ex + eye_r, eye_y)))
        else:
            opened = max(0.18, personality.eye_open)
            eye = pygame.Rect(0, 0, round(eye_r * 2), max(thick, round(eye_r * 2.15 * opened)))
            eye.center = round(ex), round(eye_y)
            pygame.draw.ellipse(surface, INK, eye.inflate(thick * 2, thick * 2))
            pygame.draw.ellipse(surface, WHITE, eye)
            pupil = max(1, round(eye_r * 0.43))
            px = round(ex + max(-1, min(1, gaze[0])) * eye_r * 0.28)
            py = round(eye_y + max(-1, min(1, gaze[1])) * eye_r * 0.24 * opened)
            if opened > 0.45:
                pygame.draw.circle(surface, INK, (px, py), pupil)
                pygame.draw.circle(surface, WHITE, (px - max(1, pupil // 3), py - max(1, pupil // 3)),
                                   max(1, pupil // 3))
        if expression == "worried":
            line(((ex - eye_r, eye_y - eye_r * (1.6 if side == -1 else 1.2)),
                  (ex + eye_r, eye_y - eye_r * (1.2 if side == -1 else 1.6))))
        elif expression == "surprised":
            line(((ex - eye_r * 0.8, eye_y - eye_r * 1.6),
                  (ex, eye_y - eye_r * 1.85), (ex + eye_r * 0.8, eye_y - eye_r * 1.6)))

    mw = w * 0.23
    if expression == "surprised":
        rect = pygame.Rect(0, 0, max(3, round(mw)), max(4, round(h * 0.26)))
        rect.center = round(cx), round(mouth_y)
        pygame.draw.ellipse(surface, INK, rect)
        pygame.draw.ellipse(surface, (244, 132, 148), rect.inflate(-max(1, round(mw * 0.4)), -max(1, round(h * 0.14))))
    elif expression == "joy":
        rect = pygame.Rect(0, 0, max(3, round(mw * 2)), max(4, round(h * 0.24)))
        rect.center = round(cx), round(mouth_y)
        pygame.draw.ellipse(surface, INK, rect)
        pygame.draw.line(surface, WHITE, (rect.left + thick, rect.top + thick),
                         (rect.right - thick, rect.top + thick), thick)
        pygame.draw.ellipse(surface, CHEEK, (rect.centerx - mw * 0.5, rect.centery, mw, max(2, h * 0.10)))
    elif expression == "ouch":
        line(((cx - mw, mouth_y), (cx - mw * 0.5, mouth_y - h * 0.08),
              (cx, mouth_y + h * 0.03), (cx + mw * 0.5, mouth_y - h * 0.08), (cx + mw, mouth_y)))
    elif expression in ("worried", "dizzy"):
        line(((cx - mw, mouth_y + h * 0.07), (cx, mouth_y - h * 0.07), (cx + mw, mouth_y + h * 0.07)))
    else:
        line(((cx - mw, mouth_y - h * 0.035), (cx - mw * 0.5, mouth_y + h * 0.06),
              (cx, mouth_y + h * 0.08), (cx + mw * 0.5, mouth_y + h * 0.06), (cx + mw, mouth_y - h * 0.035)))
        if expression == "playful":
            pygame.draw.ellipse(surface, CHEEK, (cx, mouth_y + h * 0.04, mw * 0.7, h * 0.13))
