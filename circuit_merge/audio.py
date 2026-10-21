"""Effets synthétiques et musique locale lue en streaming.

La sinusoïde est un exemple de fonction mathématique échantillonnée. Le jeu
reste jouable lorsque l'ordinateur n'a pas de périphérique audio disponible.
"""

from array import array
import math
from pathlib import Path

import pygame


class Audio:
    """Petit synthétiseur avec volume limité pour un usage en salle de cours."""

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled
        self.suspended = False
        self.music_loaded = False
        self.music_started = False
        self.music_error = ""
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
        if not self.enabled or not self.available or self.suspended:
            return
        sound = {"drop": self.drop_sound, "impact": self.impact_sound,
                 "game_over": self.end_sound}.get(kind)
        if kind == "merge":
            sound = self.notes[min(len(self.notes) - 1, level * 2)]
        if sound is not None:
            sound.play()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)
        self._sync_music()

    def start_music(self, path: Path | None = None) -> None:
        """Stream a replaceable local track; never decode the whole song to RAM."""
        if not self.available or self.music_loaded:
            return
        folder = Path(__file__).resolve().parent / "assets" / "audio"
        if path is None:
            path = next((folder / name for name in ("main_theme.ogg", "main_theme.mp3")
                         if (folder / name).is_file()), None)
        if path is None:
            self.music_error = "Musique absente."
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.35)
            self.music_loaded = True
            self.music_error = ""
            self._sync_music()
        except (pygame.error, OSError) as exc:
            self.music_error = str(exc)
            self.music_loaded = False

    def _sync_music(self) -> None:
        if not self.available or not self.music_loaded:
            return
        try:
            if self.enabled and not self.suspended:
                if not self.music_started:
                    pygame.mixer.music.play(-1, fade_ms=500)
                    self.music_started = True
                else:
                    pygame.mixer.music.unpause()
            elif self.music_started:
                pygame.mixer.music.pause()
        except pygame.error as exc:
            self.music_error = str(exc)

    def suspend(self) -> None:
        self.suspended = True
        if self.available:
            pygame.mixer.stop()
        self._sync_music()

    def resume(self) -> None:
        self.suspended = False
        self._sync_music()

    def close(self) -> None:
        if self.available:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.music_loaded = self.music_started = False
