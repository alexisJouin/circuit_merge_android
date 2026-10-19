"""Cas spécifiques V2 : occupation réelle, formes composées et personnalités.

Les tests traversent les vrais contacts Pymunk, et vérifient des comportements
observables : un espace entre les pattes doit rester sélectionnable comme vide,
une RAM verticale n'occupe pas la place d'une RAM horizontale, plusieurs
contacts d'un même corps ne donnent pas plusieurs fusions.
"""
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
import pymunk

from circuit_merge import config as C
from circuit_merge.app import Application
from circuit_merge.art import SpriteCache
from circuit_merge.engine import GameEngine
from circuit_merge.faces import Personality
from circuit_merge.geometry import (area_and_centroid, bevel_box, geometry_for,
                                    landing_y, vertical_contact)
from circuit_merge.model import RoundState
from circuit_merge.storage import SaveStore


def advance(engine, seconds):
    for _ in range(math.ceil(seconds / C.FIXED_DT)):
        engine.step()


class SilhouetteTests(unittest.TestCase):
    def test_every_component_uses_convex_parts_and_centered_mass(self):
        engine = GameEngine(1)
        for level in range(len(C.COMPONENTS)):
            with self.subTest(level=level):
                piece = engine.add_piece(level, (550, 500))
                geometry = geometry_for(level)
                self.assertEqual(len(piece.shapes), len(geometry.parts))
                cx = cy = 0.0
                for shape, part in zip(piece.shapes, geometry.parts):
                    self.assertIsInstance(shape, pymunk.Poly)
                    self.assertEqual({tuple(v) for v in shape.get_vertices()}, set(part.vertices))
                    _, center = area_and_centroid(part.vertices)
                    cx += part.mass * center[0]
                    cy += part.mass * center[1]
                self.assertAlmostEqual(cx / geometry.mass, 0, places=8)
                self.assertAlmostEqual(cy / geometry.mass, 0, places=8)
                self.assertGreater(piece.body.moment, 0)

    def test_ram_footprint_rotates_with_body(self):
        engine = GameEngine(1)
        piece = engine.add_piece(6, (550, 500))
        bb = piece.bounds
        width, height = bb.right - bb.left, bb.top - bb.bottom
        self.assertGreater(width, 3 * height)
        piece.body.angle = math.pi / 2
        rotated = piece.bounds
        self.assertAlmostEqual(rotated.right - rotated.left, height)
        self.assertAlmostEqual(rotated.top - rotated.bottom, width)

    def test_gaps_between_transistor_legs_and_racks_remain_empty(self):
        engine = GameEngine(1)
        for level, design_point in ((3, (0.24, 0.9)), (10, (-0.43, 0.0))):
            piece = engine.add_piece(level, (550, 500), angle=0.4)
            gap = piece.body.local_to_world(piece.geometry.local(*design_point))
            self.assertIsNone(engine.piece_at(*gap))
            body_point = piece.body.local_to_world(piece.geometry.face.center)
            self.assertIs(engine.piece_at(*body_point), piece)
            engine._remove_piece(piece)
        self.assertEqual(engine._by_shape, {})

    def test_each_shape_settles_on_floor_at_several_orientations(self):
        for level in range(len(C.COMPONENTS)):
            for angle in (0, 0.5, math.pi / 2):
                with self.subTest(level=level, angle=angle):
                    engine = GameEngine(1)
                    piece = engine.add_piece(level, (550, 450), angle=angle)
                    advance(engine, 8)  # les boîtiers à pattes peuvent longtemps basculer
                    self.assertIs(engine.state, RoundState.PLAYING)
                    self.assertAlmostEqual(piece.bounds.top, C.FLOOR - C.WALL_THICKNESS, delta=1)
                    self.assertLess(piece.body.velocity.length, 2)

    def test_multi_part_contacts_merge_once_and_clean_all_indexes(self):
        engine = GameEngine(1)
        engine.space.gravity = (0, 0)
        a = engine.add_piece(4, (510, 600), born_at=-1)
        b = engine.add_piece(4, (575, 600), born_at=-1)
        consumed = set(a.shapes + b.shapes)
        advance(engine, 0.2)
        self.assertEqual(engine.merge_count, 1)
        self.assertEqual([p.level for p in engine.pieces.values()], [5])
        self.assertFalse(consumed & set(engine.space.shapes))
        self.assertFalse(consumed & set(engine._by_shape))
        self.assertEqual(len(engine._by_shape), sum(len(p.shapes) for p in engine.pieces.values()))

    def test_rotated_preview_stays_inside_both_walls(self):
        engine = GameEngine(1)
        for level in range(len(C.DROP_WEIGHTS)):
            engine.current_level = level
            for _ in range(24):
                engine.rotate_aim()
                for x in (-10000, 10000):
                    engine.set_aim(x)
                    lo, _, hi, _ = geometry_for(level).bounds(engine.aim_angle)
                    self.assertGreaterEqual(engine.aim_x + lo, C.LEFT + C.WALL_THICKNESS)
                    self.assertLessEqual(engine.aim_x + hi, C.RIGHT - C.WALL_THICKNESS)

    def test_rotated_actual_top_controls_overflow(self):
        engine = GameEngine(1)
        engine.space.gravity = (0, 0)
        piece = engine.add_piece(6, (550, 340), born_at=-3)
        advance(engine, 0.4)  # RAM horizontale sous la limite
        self.assertEqual(piece.overflow_time, 0)
        piece.body.angle = math.pi / 2  # même centre, extrémité maintenant au-dessus
        engine.space.reindex_shapes_for_body(piece.body)
        advance(engine, C.OVERFLOW_DELAY + C.FIXED_DT)
        self.assertIs(engine.state, RoundState.GAME_OVER)


class ProjectionTests(unittest.TestCase):
    def test_vertical_sat_rectangles_and_non_overlap(self):
        moving = bevel_box(0, 0, 10, 10)
        self.assertEqual(vertical_contact(moving, bevel_box(2, 30, 5, 10)), 20)
        self.assertIsNone(vertical_contact(moving, bevel_box(20, 30, 5, 10)))
        self.assertEqual(vertical_contact(moving, bevel_box(2, 5, 5, 10)), 0)
        self.assertIsNone(vertical_contact(moving, bevel_box(2, -30, 5, 10)))

    def test_preview_uses_rotated_polygon_height_and_platform(self):
        geometry = geometry_for(6)
        flat = landing_y(6, 550, 0, [], C.DROP_Y, C.FLOOR - C.WALL_THICKNESS)
        upright = landing_y(6, 550, math.pi / 2, [], C.DROP_Y, C.FLOOR - C.WALL_THICKNESS)
        self.assertGreater(flat, upright + 60)
        engine = GameEngine(1)
        base = engine.add_piece(7, (550, 600))
        projected = landing_y(6, 550, 0, engine.pieces.values(), C.DROP_Y,
                              C.FLOOR - C.WALL_THICKNESS)
        self.assertAlmostEqual(projected + geometry.bounds()[3], base.bounds.bottom, delta=0.01)


class PersonalityTests(unittest.TestCase):
    def test_blinks_are_staggered_and_reopen(self):
        faces = [Personality(uid) for uid in range(8)]
        self.assertEqual(len({f.blink_at for f in faces}), len(faces))
        face = faces[0]
        face.advance(face.blink_at + face.BLINK_DURATION / 2)
        self.assertAlmostEqual(face.eye_open, 0)
        face.advance(face.BLINK_DURATION)
        self.assertEqual(face.eye_open, 1)

    def test_priority_of_reactions_and_movement(self):
        face = Personality(7)
        self.assertEqual(face.expression(400), "surprised")
        self.assertEqual(face.expression(400, 4), "dizzy")
        self.assertEqual(face.expression(400, 4, 0.1), "worried")
        face.react("ouch", 0.5)
        self.assertEqual(face.expression(400, 4, 0.1), "ouch")
        face.react("joy", 1)
        face.react("ouch", 0.5)
        self.assertEqual(face.expression(), "joy")
        face.advance(1.1)
        self.assertEqual(face.expression(), "idle")

    def test_true_floor_impact_emits_targeted_reaction(self):
        engine = GameEngine(1)
        piece = engine.add_piece(2, (550, 350))
        advance(engine, 1.2)
        impacts = [e for e in engine.take_events() if e.kind == "ouch"]
        self.assertTrue(any(e.uid == piece.uid and e.strength > 75 for e in impacts))
        self.assertLess(len(impacts), 6)  # les deux pattes ne doivent pas saturer les événements

    def test_sprite_drawing_has_no_effect_on_timers_or_gameplay_rng(self):
        engine = GameEngine(42)
        before = engine.snapshot()
        face = Personality(3)
        blink_at = face.blink_at
        state = face.rng.getstate()
        sprites = SpriteCache()
        for expression in ("idle", "joy", "ouch", "dizzy", "surprised", "worried", "playful"):
            for level in range(len(C.COMPONENTS)):
                sprites.character(level, face, expression)
        self.assertEqual(engine.snapshot(), before)
        self.assertEqual(face.rng.getstate(), state)
        self.assertEqual(face.blink_at, blink_at)
        self.assertEqual(face.time, 0)


class V2IntegrationTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_keys_and_wheel_rotate_actual_dropped_body(self):
        app = Application(seed=42, persist=False, muted=True)
        app.action("close")
        app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        app.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=1))
        self.assertAlmostEqual(math.degrees(app.engine.aim_angle), 30)
        app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        piece = next(iter(app.engine.pieces.values()))
        self.assertAlmostEqual(piece.body.angle, math.radians(30))

    def test_pause_freezes_faces_and_merge_sets_joy(self):
        app = Application(seed=1, persist=False, muted=True)
        app.action("close")
        app.engine.add_piece(0, (500, 680), born_at=-2)
        app.engine.add_piece(0, (525, 680), born_at=-2)
        app.update(0.1)
        piece = next(iter(app.engine.pieces.values()))
        self.assertEqual(piece.level, 1)
        face = app.view.face_for(piece.uid)
        self.assertEqual(face.expression(), "joy")
        app.action("pause")
        before = face.time, face.blink_at, face.reaction_until
        for _ in range(20):
            app.update(0.1)
            app.draw()
        self.assertEqual((face.time, face.blink_at, face.reaction_until), before)

    def test_v2_snapshot_preserves_aim_angle_and_shape_reconstruction(self):
        engine = GameEngine(1)
        engine.rotate_aim(45)
        piece = engine.add_piece(8, (550, 550), angle=0.5)
        restored = GameEngine.from_snapshot(json.loads(json.dumps(engine.snapshot())))
        other = next(iter(restored.pieces.values()))
        self.assertEqual(engine.snapshot(), restored.snapshot())
        self.assertEqual(piece.bounds, other.bounds)
        self.assertEqual(len(piece.shapes), len(other.shapes))

    def test_v1_import_preserves_original_file_and_gives_new_grace(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"LOCALAPPDATA": folder}):
            old = Path(folder) / "CircuitMerge" / "save.json"
            old.parent.mkdir()
            engine = GameEngine(9)
            piece = engine.add_piece(6, (550, 730), born_at=-3)
            legacy = engine.snapshot()
            legacy["version"] = 1
            legacy.pop("aim_angle")
            content = json.dumps({"version": 1, "best": 120, "sound": False, "round": legacy})
            old.write_text(content, encoding="utf-8")
            app = Application(muted=True)
            self.assertEqual(app.best, 120)
            self.assertEqual(app.mode, "pause")
            converted = next(iter(app.engine.pieces.values()))
            self.assertEqual(converted.born_at, app.engine.time)
            self.assertEqual(converted.overflow_time, 0)
            app.save()
            self.assertEqual(old.read_text(encoding="utf-8"), content)
            self.assertTrue(old.with_name("save_v2.json").exists())

    def test_corrupt_v1_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"LOCALAPPDATA": folder}):
            old = Path(folder) / "CircuitMerge" / "save.json"
            old.parent.mkdir()
            old.write_text("{broken", encoding="utf-8")
            store = SaveStore()
            self.assertEqual(store.load()["best"], 0)
            self.assertEqual(old.read_text(encoding="utf-8"), "{broken")
            self.assertFalse(store.migrated)


if __name__ == "__main__":
    unittest.main()
