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
        self.assertEqual(self.app.page, 'hub')

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

    def test_toolbar_stays_outside_game_viewport(self):
        self.assertLessEqual(self.app._viewport().bottom, self.app._toolbar()[0].top)

if __name__ == '__main__':
    unittest.main()
