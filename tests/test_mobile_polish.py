"""Mobile polish regressions: bounded effects, skippable intro, cached art."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import patch
import pygame
from circuit_merge.mobile_app import AndroidApplication
from circuit_merge.model import GameEvent

class PolishTests(unittest.TestCase):
    def setUp(self):
        self.app = AndroidApplication(persist=False,muted=True)
    def tearDown(self):
        pygame.quit()
    def test_effect_budget_and_expiration(self):
        view = self.app.view
        view.consume([GameEvent('merge',500,500,1,uid=i) for i in range(100)])
        self.assertEqual(len(view.effects),8)
        view.animate(.5,self.app.engine)
        self.assertEqual(view.effects,[])
    def test_intro_skip_does_not_activate_home_button(self):
        a = self.app
        a.intro_remaining=1.2
        a.draw()
        rect=a._viewport()
        pos=(rect.x+300*rect.w/600,rect.y+700*rect.h/1080)
        a.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,pos=pos,button=1))
        a.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP,pos=pos,button=1))
        self.assertEqual(a.intro_remaining,0)
        self.assertEqual(a.page,'home')
    def test_intro_finishes_without_input_and_freezes_in_background(self):
        a=self.app
        a.intro_remaining=1.2
        a.suspended=True
        a.update(.1)
        self.assertEqual(a.intro_remaining,1.2)
        a.suspended=False
        for _ in range(13): a.update(.1)
        self.assertEqual(a.intro_remaining,0)
    def test_polished_frames_do_not_mutate_physics(self):
        a=self.app
        a.start(0)
        piece=a.engine.add_piece(1,(500,500))
        pos=tuple(piece.body.position)
        a.view.consume([GameEvent('merge',500,500,1,uid=piece.uid)])
        a.view.animate(.1,a.engine)
        with patch('pygame.display.flip') as flip:
            a.draw()
            flip.assert_called_once()
        self.assertEqual(tuple(piece.body.position),pos)
    def test_result_timer_and_all_pages_render(self):
        a=self.app
        a.start(0); a.engine.outcome='won'; a.update(0)
        self.assertEqual(a.view.result_age,0)
        for _ in range(10): a.update(.1)
        self.assertGreater(a.view.result_age,.8)
        for page in ('home','map','briefing','confirm','result'):
            a.page=page; a.draw()
        a.intro_remaining=1.2; a.draw()
    def test_sprite_cache_stays_reusable(self):
        a=self.app; a.start(0); a.draw()
        with patch.object(a.view.sprites,'character',side_effect=AssertionError('rebuilt')):
            a.draw()
        self.assertLessEqual(a.view.cache_bytes,16*1024*1024)

if __name__=='__main__': unittest.main()
