"""Vrais événements SDL : dépose, annulation, redimensionnement et toucher."""
import os,tempfile
from pathlib import Path
import unittest
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from circuit_merge.project_app import ProjectApplication
from circuit_merge.pc_layout import ZONES,PAGES

class DragTests(unittest.TestCase):
    def setUp(self):
        self.a=ProjectApplication(persist=False,muted=True)
        self.a.action('pc');self.a.draw()
    def tearDown(self):pygame.quit()
    def native(self,pos):
        r=self.a._viewport();return (r.x+pos[0]*r.width/1120,r.y+pos[1]*r.height/900)
    def event(self,kind,**kw):self.a.handle_event(pygame.event.Event(kind,**kw))
    def take(self,key):
        self.a.action('pc:page:'+str(0 if key in PAGES[0] else 1));self.a.draw()
        self.event(pygame.MOUSEBUTTONDOWN,pos=self.native(self.a.view.pc_cards[key].center),button=1)
    def release(self,key=None,pos=None):
        p=self.native(pos if pos is not None else pygame.Rect(ZONES[key]).center)
        self.event(pygame.MOUSEMOTION,pos=p,rel=(0,0),buttons=(1,0,0))
        self.event(pygame.MOUSEBUTTONUP,pos=p,button=1)
    def base(self):
        for key in ('case','board'):self.take(key);self.release(key)
    def test_click_selects_but_only_release_after_drag_installs(self):
        self.take('case');self.assertNotIn('case',self.a.pc.installed)
        pos=self.a.view.pc_cards['case'].center;self.release(pos=pos)
        self.assertNotIn('case',self.a.pc.installed)
        self.take('case');self.release('case')
        self.assertIn('case',self.a.pc.installed);self.assertIsNone(self.a.pc_drag)
        before=self.a.pc.snapshot();self.release('case');self.assertEqual(before,self.a.pc.snapshot())
    def test_wrong_socket_and_unmet_dependencies_do_not_install(self):
        self.take('cpu');self.release('cpu');self.assertNotIn('cpu',self.a.pc.installed)
        self.base();self.take('cpu');self.release('ram')
        self.assertNotIn('cpu',self.a.pc.installed);self.assertIsNone(self.a.pc_drag)
        self.take('cpu');self.release('cpu');self.assertIn('cpu',self.a.pc.installed)
    def test_release_outside_canvas_returns_to_stock(self):
        self.take('case');self.event(pygame.MOUSEBUTTONUP,pos=(-50,-50),button=1)
        self.assertFalse(self.a.pc.installed);self.assertIsNone(self.a.pc_drag)
    def test_escape_focus_loss_and_resize_cancel_without_installing(self):
        for event in (pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),
                      pygame.event.Event(pygame.WINDOWFOCUSLOST),
                      pygame.event.Event(pygame.VIDEORESIZE,w=640,h=520)):
            self.take('case');self.a.handle_event(event);self.release('case')
            self.assertEqual(self.a.page,'pc');self.assertIsNone(self.a.pc_drag)
            self.assertFalse(self.a.pc.installed)
    def test_scaled_window_and_narrow_connector(self):
        self.a.screen=pygame.display.set_mode((650,510));self.a.draw()
        self.base();self.take('psu');self.release('psu')
        self.take('atx');self.release('atx')
        self.assertIn('atx',self.a.pc.installed)
        self.assertEqual(self.a.engine.drops,0)
    def test_touch_ignores_synthetic_mouse_and_other_fingers(self):
        def finger(kind,logical,fid=10):
            x,y=self.native(logical);w,h=self.a.screen.get_size()
            self.event(kind,x=x/w,y=y/h,finger_id=fid,touch_id=1)
        source=self.a.view.pc_cards['case'].center;target=pygame.Rect(ZONES['case']).center
        finger(pygame.FINGERDOWN,source)
        self.event(pygame.MOUSEBUTTONUP,pos=self.native(target),button=1,touch=True)
        finger(pygame.FINGERUP,target,11)
        self.assertNotIn('case',self.a.pc.installed)
        finger(pygame.FINGERMOTION,target);finger(pygame.FINGERUP,target)
        self.assertIn('case',self.a.pc.installed);self.assertIsNone(self.a.pc_drag)
    def test_no_target_highlight_without_guide(self):
        self.base();self.assertFalse(self.a.pc_guide)
        self.a.pc_selected='cpu';self.a.draw()
        before=pygame.image.tobytes(self.a.view.canvas.subsurface((304,143,510,620)),'RGB')
        self.a.pc_selected='ram';self.a.draw()
        after=pygame.image.tobytes(self.a.view.canvas.subsurface((304,143,510,620)),'RGB')
        self.assertEqual(before,after)
    def test_incomplete_drag_is_not_saved_but_successful_drop_is(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'save.json'
            self.a.project_persist=True;self.a.campaign_store.path=path
            self.take('case');self.a.save()
            from circuit_merge.campaign import CampaignStore
            self.assertEqual(CampaignStore(path).load().pc_build['installed'],[])
            self.release('case')
            self.assertEqual(CampaignStore(path).load().pc_build['installed'],['case'])

if __name__=='__main__':unittest.main()
