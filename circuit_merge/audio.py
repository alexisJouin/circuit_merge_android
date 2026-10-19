"""Sons de synthèse : aucune ressource audio à télécharger.

La sinusoïde est un exemple de fonction mathématique échantillonnée. Le jeu
reste jouable lorsque l'ordinateur n'a pas de périphérique audio disponible.
"""

from array import array
import math

import pygame


class Audio:
    """Petit synthétiseur avec volume limité pour un usage en salle de cours."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.available = False
        self.notes: list[pygame.mixer.Sound] = []
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.notes = [self._tone(220 * 2 ** (level / 12), 0.14) for level in range(22)]
            self.drop_sound = self._tone(170, 0.045)
            self.impact_sound = self._tone(95, 0.028)
            self.end_sound = self._tone(90, 0.45)
            self.available = True
        except pygame.error:
            pass

    @staticmethod
    def _tone(frequency: float, duration: float) -> pygame.mixer.Sound:
        """Construit un signal PCM signé 16 bits avec attaque et décroissance."""
        sample_rate = 22050
        samples = array("h")
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            envelope = min(1, t / 0.008) * (1 - t / duration) ** 2
            value = math.sin(2 * math.pi * frequency * t)
            value += 0.2 * math.sin(2 * math.pi * frequency * 2 * t)
            samples.append(int(3600 * envelope * value))
        return pygame.mixer.Sound(buffer=samples)

    def play(self, kind: str, level: int = 0) -> None:
        """Joue une note montante pour une fusion, si le son est disponible."""
        if not self.enabled or not self.available:
            return
        sound = {"drop": self.drop_sound, "impact": self.impact_sound,
                 "game_over": self.end_sound}.get(kind)
        if kind == "merge":
            sound = self.notes[min(len(self.notes) - 1, level * 2)]
        if sound is not None:
            sound.play()
