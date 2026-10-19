"""Tests de comportement du jeu ; aucun affichage ni accès réseau nécessaire.

Ces tests ciblent des erreurs difficiles à voir à l'œil : double consommation
au contact, chronomètre de défaite partagé, prochain objet incohérent ou perte
des tirages après une sauvegarde. Exécution : python -m unittest discover -s tests -v
"""

import json
import math
import random
import unittest

from circuit_merge import config as C
from circuit_merge.engine import GameEngine
from circuit_merge.model import RoundState


def advance(engine: GameEngine, seconds: float) -> None:
    for _ in range(math.ceil(seconds / C.FIXED_DT)):
        engine.step()


class PhysicsTests(unittest.TestCase):
    def test_real_contact_merges_equal_pieces(self):
        engine = GameEngine(3)
        engine.add_piece(0, (480, 680))
        engine.add_piece(0, (511, 680))
        advance(engine, 0.8)
        self.assertEqual([p.level for p in engine.pieces.values()], [1])
        self.assertEqual(engine.score, C.COMPONENTS[1].points)

    def test_different_pieces_collide_without_merging(self):
        engine = GameEngine(3)
        engine.add_piece(0, (480, 680))
        engine.add_piece(1, (516, 680))
        advance(engine, 1.8)
        self.assertEqual(sorted(p.level for p in engine.pieces.values()), [0, 1])
        self.assertEqual(engine.score, 0)
        a, b = engine.pieces.values()
        # Les contacts se font sur les polygones, avec une petite tolérance
        # numérique. Un test de distance entre centres serait faux en V2.
        for shape in a.shapes:
            for contact in engine.space.shape_query(shape):
                if contact.shape in b.shapes:
                    self.assertTrue(all(p.distance >= -0.8 for p in contact.contact_point_set.points))

    def test_three_simultaneous_contacts_consume_each_piece_once(self):
        engine = GameEngine(3)
        for x in (440, 471, 502):
            engine.add_piece(0, (x, 680))
        advance(engine, 1.0)
        self.assertEqual(sorted(p.level for p in engine.pieces.values()), [0, 1])
        self.assertEqual(engine.merge_count, 1)
        self.assertEqual(engine.score, C.COMPONENTS[1].points)

    def test_new_piece_can_chain_merge_with_an_existing_piece(self):
        engine = GameEngine(3)
        engine.add_piece(0, (495, 740))
        engine.add_piece(0, (525, 740))
        advance(engine, 0.4)
        result = next(iter(engine.pieces.values()))
        engine.add_piece(1, (result.body.position.x, result.body.position.y - 45))
        advance(engine, 1.1)
        self.assertEqual([p.level for p in engine.pieces.values()], [2])
        self.assertEqual(engine.score, C.COMPONENTS[1].points + C.COMPONENTS[2].points)

    def test_terminal_pair_clears_and_does_not_index_past_catalogue(self):
        engine = GameEngine(3)
        engine.space.gravity = (0, 0)
        final = len(C.COMPONENTS) - 1
        engine.add_piece(final, (556, 470))
        engine.add_piece(final, (556, 715))
        advance(engine, 0.3)
        self.assertEqual(len(engine.pieces), 0)
        self.assertEqual(engine.completed_circuits, 1)
        self.assertEqual(engine.score, 2 * C.COMPONENTS[-1].points)

    def test_drop_preview_bounds_and_cooldown(self):
        engine = GameEngine(8)
        expected_next = engine.next_level
        self.assertTrue(engine.drop(-5000))
        piece = next(iter(engine.pieces.values()))
        self.assertGreaterEqual(piece.bounds.left,
                                C.LEFT + C.WALL_THICKNESS)
        self.assertEqual(engine.current_level, expected_next)
        self.assertFalse(engine.drop())
        advance(engine, C.DROP_INTERVAL)
        self.assertTrue(engine.drop(5000))
        latest = list(engine.pieces.values())[-1]
        self.assertLessEqual(latest.bounds.right,
                             C.RIGHT - C.WALL_THICKNESS)

    def test_floor_stops_fall_and_body_settles(self):
        engine = GameEngine(1)
        piece = engine.add_piece(4, (600, 300))
        advance(engine, 6)
        self.assertAlmostEqual(piece.bounds.top,
                               C.FLOOR - C.WALL_THICKNESS, delta=1)
        self.assertLess(piece.body.velocity.length, 2)
        self.assertIs(engine.state, RoundState.PLAYING)

    def test_stress_multiple_seeded_rounds_remain_finite_and_in_bounds(self):
        for seed in range(4):
            with self.subTest(seed=seed):
                engine = GameEngine(seed)
                positions = random.Random(seed + 100)
                for _ in range(100):
                    engine.drop(positions.uniform(C.LEFT, C.RIGHT))
                    advance(engine, 0.75)
                    for p in engine.pieces.values():
                        self.assertTrue(math.isfinite(p.body.position.x))
                        self.assertTrue(math.isfinite(p.body.position.y))
                        self.assertLessEqual(p.bounds.top,
                                             C.FLOOR - C.WALL_THICKNESS + 4)
                    if engine.state is RoundState.GAME_OVER:
                        break
                self.assertGreater(engine.merge_count, 0)


class OverflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(1)
        self.engine.space.gravity = (0, 0)

    def test_newly_dropped_piece_gets_a_grace_period(self):
        self.engine.add_piece(0, (500, C.DANGER_Y - 30))
        advance(self.engine, C.DROP_GRACE - C.FIXED_DT * 2)
        self.assertEqual(self.engine.danger_ratio, 0)
        self.assertIs(self.engine.state, RoundState.PLAYING)

    def test_one_continuous_overflow_ends_round_and_freezes_time(self):
        self.engine.add_piece(0, (500, C.DANGER_Y - 30), born_at=-2)
        advance(self.engine, C.OVERFLOW_DELAY + C.FIXED_DT * 2)
        self.assertIs(self.engine.state, RoundState.GAME_OVER)
        t = self.engine.time
        self.engine.step()
        self.assertEqual(self.engine.time, t)
        self.assertFalse(self.engine.drop())

    def test_different_short_overflows_do_not_share_one_timer(self):
        a = self.engine.add_piece(0, (460, C.DANGER_Y - 30), born_at=-2)
        b = self.engine.add_piece(1, (650, 500), born_at=-2)
        advance(self.engine, C.OVERFLOW_DELAY * 0.65)
        a.body.position = (460, 500)
        b.body.position = (650, C.DANGER_Y - 30)
        # Réindexation nécessaire après déplacement direct d'un corps endormi,
        # uniquement dans cette expérience ; le jeu n'impose pas ces positions.
        a.body.activate()
        b.body.activate()
        self.engine.space.reindex_shapes_for_body(a.body)
        self.engine.space.reindex_shapes_for_body(b.body)
        advance(self.engine, C.OVERFLOW_DELAY * 0.65)
        self.assertIs(self.engine.state, RoundState.PLAYING)
        self.assertEqual(a.overflow_time, 0)
        self.assertGreater(b.overflow_time, 0)


class SnapshotTests(unittest.TestCase):
    def test_json_round_trip_preserves_round_and_future_draws(self):
        original = GameEngine(42)
        original.drop(490)
        advance(original, 1.0)
        loaded = GameEngine.from_snapshot(json.loads(json.dumps(original.snapshot())))
        self.assertEqual(original.snapshot(), loaded.snapshot())
        for x in (610, 520, 720, 420):
            original.drop(x)
            loaded.drop(x)
            self.assertEqual((original.current_level, original.next_level),
                             (loaded.current_level, loaded.next_level))
            advance(original, 0.5)
            advance(loaded, 0.5)

    def test_non_finite_or_invalid_state_is_rejected(self):
        engine = GameEngine(1)
        engine.add_piece(0, (500, 500))
        data = engine.snapshot()
        data["pieces"][0]["position"][0] = float("nan")
        with self.assertRaises(ValueError):
            GameEngine.from_snapshot(data)


if __name__ == "__main__":
    unittest.main()
