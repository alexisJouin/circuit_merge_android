"""Scénarios d'interface et de sauvegarde en mode SDL sans écran."""

import json
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from circuit_merge import config as C
from circuit_merge.app import Application
from circuit_merge.storage import SaveStore


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = Application(seed=42, persist=False, muted=True)
        self.app.action("close")
        self.app.draw()

    def tearDown(self):
        pygame.quit()

    def pixel_position(self, logical):
        rect = self.app._viewport()
        return (rect.x + logical[0] * rect.width / C.WIDTH,
                rect.y + logical[1] * rect.height / C.HEIGHT)

    def test_pause_really_freezes_simulation_and_preserves_next(self):
        self.app.engine.drop()
        self.app.update(0.1)
        self.app.action("pause")
        before = self.app.engine.snapshot()
        for _ in range(40):
            self.app.update(0.1)
        self.assertEqual(before, self.app.engine.snapshot())
        self.app.action("close")
        self.app.update(0.1)
        self.assertGreater(self.app.engine.time, before["time"])

    def test_mouse_release_drops_once_and_sidebar_does_not_drop(self):
        point = self.pixel_position((520, 400))
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=1))
        self.assertEqual(self.app.engine.drops, 0)
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=point, button=1))
        self.assertEqual(self.app.engine.drops, 1)
        sidebar = self.pixel_position((150, 790))  # bouton « Nouvelle partie »
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=sidebar, button=1))
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=sidebar, button=1))
        self.assertEqual(self.app.engine.drops, 1)
        self.assertEqual(self.app.mode, "restart")

    def test_keyboard_drop_debug_and_slow_motion(self):
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.assertEqual(self.app.engine.drops, 1)
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
        self.assertTrue(self.app.debug)
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2))
        self.app.update(0.1)
        # Le temps restant dans l'accumulateur fait partie du temps à simuler.
        self.assertAlmostEqual(self.app.engine.time + self.app.accumulator, 0.025)

    def test_focus_loss_pauses_and_coordinate_mapping_survives_resize(self):
        self.app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertEqual(self.app.mode, "pause")
        self.app.handle_event(pygame.event.Event(pygame.VIDEORESIZE, w=1500, h=740))
        for point in ((32, 32), (556, 400), (1080, 860)):
            mapped = self.app.logical_position(self.pixel_position(point))
            self.assertAlmostEqual(mapped[0], point[0])
            self.assertAlmostEqual(mapped[1], point[1])
        self.assertEqual(self.app.logical_position((0, 0)), (-1, -1))


class SaveTests(unittest.TestCase):
    def test_save_and_load_record_round_and_sound(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SaveStore(Path(directory) / "subfolder" / "save.json")
            self.assertTrue(store.save(100, False, {"example": 1}))
            self.assertEqual(store.load(), {"version": 2, "best": 100, "sound": False,
                                           "round": {"example": 1}})
            self.assertFalse(store.path.with_suffix(".tmp").exists())

    def test_corrupt_save_is_kept_and_defaults_are_returned(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            path.write_text("{incomplete", encoding="utf-8")
            store = SaveStore(path)
            self.assertEqual(store.load()["best"], 0)
            self.assertTrue(store.error)
            backups = list(Path(directory).glob("save_corrompue_*.json"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "{incomplete")

    def test_persisted_application_restores_interrupted_round(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            app = Application(seed=5, save_path=path, muted=True)
            app.action("close")
            app.engine.drop(510)
            app.update(0.1)
            app.save()
            saved = json.loads(path.read_text(encoding="utf-8"))
            restored = Application(save_path=path, muted=True)
            self.assertEqual(restored.mode, "pause")
            self.assertEqual(json.loads(json.dumps(restored.engine.snapshot())), saved["round"])
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
