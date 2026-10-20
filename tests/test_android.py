import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import Mock
import pygame
from circuit_merge.android_app import AndroidApplication


class AndroidTests(unittest.TestCase):
    def setUp(self):
        self.app = AndroidApplication(persist=False, muted=True)

    def tearDown(self):
        pygame.quit()

    def test_background_saves_and_cancels_drag(self):
        self.app.start(0)
        self.app.dragging = True
        self.app.save = Mock()
        self.app.handle_event(pygame.event.Event(pygame.APP_WILLENTERBACKGROUND))
        self.assertFalse(self.app.active)
        self.assertFalse(self.app.dragging)
        self.app.save.assert_called()

    def test_back_pauses_then_returns_home(self):
        self.app.start(0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_AC_BACK)
        self.app.handle_event(event)
        self.assertEqual(self.app.mode, 'pause')
        self.app.handle_event(event)
        self.assertEqual(self.app.page, 'home')

    def test_second_finger_does_not_release_piece(self):
        self.app.start(0)
        self.app.finger = 10
        self.app.dragging = True
        self.app.handle_event(pygame.event.Event(pygame.FINGERUP, finger_id=11, x=.5, y=.5))
        self.assertTrue(self.app.dragging)
        self.assertEqual(self.app.engine.drops, 0)

    def test_synthetic_touch_mouse_is_ignored_in_hub(self):
        self.app._press = Mock()
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 50), button=1, touch=True))
        self.app._press.assert_not_called()

    def test_draw_presents_one_complete_frame(self):
        from unittest.mock import patch
        with patch('pygame.display.flip') as flip:
            self.app.draw()
            flip.assert_called_once()

    def native(self, x, y):
        rect = self.app._viewport()
        return rect.x+x*rect.w/600, rect.y+y*rect.h/1080

    def tap(self, name):
        self.app.draw()
        pos = self.native(*self.app.view.buttons[name].center)
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.app.handle_event(pygame.event.Event(kind, pos=pos, button=1))

    def test_home_map_briefing_play_flow_and_locked_level(self):
        self.tap('adventure')
        self.assertEqual(self.app.page, 'map')
        self.app.draw()
        self.assertNotIn('mission:1', self.app.view.buttons)
        self.tap('mission:0')
        self.assertEqual(self.app.page, 'briefing')
        self.tap('start')
        self.assertTrue(self.app.active)
        self.assertEqual(self.app.engine.drops, 0)

    def test_drag_release_and_rotation_do_not_double_drop(self):
        self.app.start(0)
        self.app.draw()
        pos = self.native(300, 500)
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.assertTrue(self.app.dragging)
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))
        self.assertEqual(self.app.engine.drops, 1)
        self.tap('rotate_right')
        self.assertEqual(self.app.engine.drops, 1)

    def test_next_level_after_win_and_single_reward(self):
        self.app.start(0)
        self.app.engine.outcome = 'won'
        self.app.update(0)
        credits = self.app.profile.credits
        self.app.update(0)
        self.assertEqual(credits, self.app.profile.credits)
        self.tap('next_level')
        self.assertEqual(self.app.engine.index, 1)
        self.assertTrue(self.app.active)

    def test_free_mode_keeps_suspended_campaign(self):
        self.app.start(0)
        self.app.engine.drop()
        self.app.action('home')
        attempt = self.app.profile.active['attempt_id']
        self.tap('free')
        self.app.engine.drop()
        self.app.action('home')
        self.assertEqual(self.app.profile.active['attempt_id'], attempt)
        self.assertEqual(self.app.profile.free_round['drops'], 1)
        self.app.action('resume')
        self.assertEqual(self.app.engine.drops, 1)
        self.assertEqual(self.app.mode, 'pause')

    def test_background_freezes_physics_and_foreground_stays_paused(self):
        self.app.start(0)
        self.app.handle_event(pygame.event.Event(pygame.APP_WILLENTERBACKGROUND))
        before = self.app.engine.time
        self.app.update(.1)
        self.assertEqual(self.app.engine.time, before)
        self.app.handle_event(pygame.event.Event(pygame.APP_DIDENTERFOREGROUND))
        self.assertEqual(self.app.mode, 'pause')
        self.assertFalse(self.app.suspended)

    def test_viewport_inverse_on_phone_and_tablet(self):
        for size in ((360,800),(1080,2400),(1600,900)):
            self.app.screen = pygame.display.set_mode(size)
            result = self.app.logical_position(self.native(300,500))
            self.assertAlmostEqual(result[0],300)
            self.assertAlmostEqual(result[1],500)

    def test_static_frame_reuses_sprites(self):
        from unittest.mock import patch
        self.app.start(0)
        self.app.draw()
        with patch.object(self.app.view.sprites,'character',side_effect=AssertionError('sprite rebuilt')):
            self.app.draw()
        self.assertLessEqual(self.app.view.cache_bytes,16*1024*1024)


if __name__ == '__main__':
    unittest.main()
