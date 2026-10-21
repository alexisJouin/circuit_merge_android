"""Music lifecycle and high-resolution source regressions (headless SDL)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import wave
import pygame
from circuit_merge.audio import Audio
from circuit_merge.art import SpriteCache

class MusicTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.track = Path(self.folder.name) / "test.wav"
        with wave.open(str(self.track), "wb") as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(22050)
            stream.writeframes(b"\x00\x00" * 22050)
        self.audio = Audio()
        self.assertTrue(self.audio.available)

    def tearDown(self):
        self.audio.close()
        pygame.quit()
        self.folder.cleanup()

    def test_real_stream_load_and_cleanup(self):
        self.audio.start_music(self.track)
        self.assertTrue(self.audio.music_loaded)
        self.assertTrue(pygame.mixer.music.get_busy())
        self.audio.enabled = False
        self.assertFalse(pygame.mixer.music.get_busy())
        self.audio.enabled = True
        self.assertTrue(pygame.mixer.music.get_busy())
        self.audio.close()
        self.assertFalse(self.audio.music_loaded)

    def test_mute_background_and_resume_do_not_restart_track(self):
        with patch("pygame.mixer.music.play") as play, \
             patch("pygame.mixer.music.unpause") as unpause:
            self.audio.start_music(self.track)
            self.audio.suspend()
            self.audio.enabled = False
            self.audio.resume()
            unpause.assert_not_called()
            self.audio.enabled = True
            unpause.assert_called_once()
            self.audio.start_music(self.track)
            play.assert_called_once_with(-1, fade_ms=500)

    def test_muted_start_defers_play_until_enabled(self):
        self.audio.enabled = False
        self.audio.start_music(self.track)
        self.assertTrue(self.audio.music_loaded)
        self.assertFalse(self.audio.music_started)
        self.audio.enabled = True
        self.assertTrue(self.audio.music_started)

    def test_missing_file_keeps_effects_available(self):
        self.audio.start_music(Path(self.folder.name) / "absent.mp3")
        self.assertFalse(self.audio.music_loaded)
        self.assertTrue(self.audio.available)
        self.audio.play("drop")

    def test_no_audio_device_is_nonfatal(self):
        with patch("pygame.mixer.init", side_effect=pygame.error("no device")):
            silent = Audio()
        silent.start_music(self.track)
        silent.enabled = False
        silent.suspend()
        silent.resume()
        silent.close()
        self.assertFalse(silent.available)

class ArtworkTests(unittest.TestCase):
    def test_hd_source_preserves_center_and_alpha_for_all_components(self):
        sprites = SpriteCache()
        for level in range(11):
            regular = sprites.character(level)
            hd = sprites.character(level, high_resolution=True)
            self.assertEqual(hd.get_size(), tuple(n * 2 for n in regular.get_size()))
            self.assertTrue(hd.get_flags() & pygame.SRCALPHA)
            self.assertGreater(pygame.mask.from_surface(hd).count(), 0)

if __name__ == "__main__":
    unittest.main()
