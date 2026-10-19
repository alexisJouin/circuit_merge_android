"""Solutions physiques aux 10 missions, économie, sauvegarde et navigation."""
import json
import os
from pathlib import Path
import tempfile
import unittest
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
import pygame
from circuit_merge.campaign import MissionEngine as NewMissionEngine,Profile,CampaignStore,LEGACY_MISSIONS as MISSIONS,BUILDINGS

def MissionEngine(index): return NewMissionEngine(index,ruleset=1)
MissionEngine.restore=NewMissionEngine.restore
from circuit_merge.project_app import ProjectApplication
from circuit_merge.engine import GameEngine

def advance(e,seconds=3):
    for _ in range(round(seconds*240)): e.step()

def solve(index):
    e=MissionEngine(index)
    while e.remaining and not e.outcome:
        x=e.pieces[next(iter(e.marked))].body.position.x if index==5 and e.marked else 556
        assert e.drop(x)
        advance(e)
    advance(e,9)
    return e

class CampaignTests(unittest.TestCase):
    def test_all_ten_missions_winnable_without_tools_and_fund_all_buildings(self):
        p=Profile()
        for i in range(10):
            with self.subTest(mission=i+1):
                self.assertTrue(p.available(i)); e=solve(i)
                self.assertEqual(e.outcome,'won'); self.assertLessEqual(e.drops,MISSIONS[i].par)
                self.assertEqual(e.used,set()); self.assertGreater(p.award(e),0)
                self.assertEqual(p.award(e),0); self.assertEqual(p.stars[i],3)
        earned=p.credits
        for _ in BUILDINGS[:5]: self.assertTrue(p.build())
        self.assertFalse(p.build()); self.assertEqual(p.credits,earned-sum(b[1] for b in BUILDINGS[:5]))
        self.assertTrue(25<=p.award(solve(0))<=40)
    def test_last_drop_has_time_to_resolve(self):
        e=MissionEngine(0); e.drops=e.mission.budget-2; e.created[1]=2
        self.assertTrue(e.drop(556)); advance(e); self.assertTrue(e.drop(556))
        self.assertEqual(e.remaining,0); self.assertIsNone(e.outcome); self.assertFalse(e.drop())
        advance(e,9); self.assertEqual(e.outcome,'won')
    def test_unmet_objective_loses_after_resolution(self):
        e=MissionEngine(0); e.drops=e.mission.budget-1; e.drop(); advance(e,9)
        self.assertEqual(e.outcome,'lost'); t=e.time; advance(e); self.assertEqual(t,e.time)
        self.assertEqual(Profile().award(e),0)
    def test_tools_charge_only_success_and_two_families(self):
        p=Profile(credits=1000,stars=[1]*5+[0]*5)
        for tool in ('remove','swap','extra'): self.assertTrue(p.buy(tool))
        self.assertEqual(p.credits,760)
        e=MissionEngine(5); uid=next(iter(e.marked))
        self.assertFalse(p.use(e,'remove',uid)); self.assertEqual(p.inventory['remove'],1)
        self.assertEqual(e.marked_done,0)
        self.assertTrue(p.use(e,'swap')); self.assertTrue(p.use(e,'extra'))
        target=e.add_piece(2,(500,600)); self.assertFalse(p.use(e,'remove',target.uid))
        self.assertEqual(p.inventory['remove'],1); self.assertEqual(e.remaining,e.mission.budget+3)
        self.assertFalse(Profile().buy('remove')); self.assertFalse(Profile(credits=1000).build())
    def test_identical_queue_exchange_is_noop(self):
        p=Profile(inventory={'remove':0,'swap':1,'extra':0}); e=MissionEngine(0)
        before=e.campaign_snapshot(); self.assertFalse(p.use(e,'swap'))
        self.assertEqual(before,e.campaign_snapshot()); self.assertEqual(p.inventory['swap'],1)
    def test_resume_preserves_marked_pieces_queue_and_physics(self):
        e=MissionEngine(5); e.drop(430); advance(e); e.bonus('extra'); e.drop(680); advance(e,.15)
        r=MissionEngine.restore(json.loads(json.dumps(e.campaign_snapshot())))
        self.assertEqual(r.marked_done,e.marked_done); self.assertEqual(r.remaining,e.remaining)
        self.assertEqual(r.attempt_id,e.attempt_id); self.assertEqual(r.current_level,e.current_level)
        self.assertEqual(r.left,e.left)
        for a,b in zip(e.pieces.values(),r.pieces.values()):
            self.assertLess((a.body.position-b.body.position).length,.001); self.assertEqual(a.body.angle,b.body.angle)
        advance(r); self.assertEqual(r.outcome,'won')
    def test_arenas_do_not_mutate_free_workshop(self):
        free=GameEngine(); e=MissionEngine(8)
        self.assertLess(e.right-e.left,free.right-free.left); e.set_aim(-1000)
        self.assertGreater(e.aim_x,e.left); self.assertEqual(GameEngine().left,free.left)
    def test_profile_roundtrip_and_corrupt_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            s=CampaignStore(Path(folder)/'save.json'); p=Profile(credits=420,stars=[3]+[0]*9)
            p.active=MissionEngine(1).campaign_snapshot(); p.free_round=GameEngine().snapshot()
            self.assertTrue(s.save(p)); q=s.load()
            self.assertEqual(json.loads(json.dumps(vars(p))),vars(q))
            s.path.write_text('{broken',encoding='utf8'); self.assertEqual(s.load().credits,0)
            self.assertEqual(len(list(Path(folder).glob('*corrompu*'))),1); self.assertTrue(s.save(Profile()))

class ProjectUITests(unittest.TestCase):
    def tearDown(self): pygame.quit()
    def test_hub_inputs_resume_and_free_preserve_campaign(self):
        app=ProjectApplication(persist=False,muted=True)
        app.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
        self.assertEqual(app.engine.drops,0); app.start(0); app.engine.drop(); app.action('hub')
        attempt=app.profile.active['attempt_id']
        app.action('free'); app.engine.drop(); app.action('hub')
        self.assertEqual(app.profile.active['attempt_id'],attempt); self.assertEqual(app.profile.free_round['drops'],1)
        app.action('resume'); self.assertEqual(app.mode,'pause'); self.assertEqual(app.engine.drops,1)
        app.action('pause'); self.assertTrue(app.active); app.draw()
    def test_result_credits_once_and_every_screen_renders(self):
        app=ProjectApplication(persist=False,muted=True); app.engine=solve(0); app.page='play'; app.update(.016)
        self.assertEqual(app.page,'result'); credits=app.profile.credits
        app.update(.016); self.assertEqual(app.profile.credits,credits)
        for page in ('result','shop','briefing','confirm','hub'): app.page=page; app.draw()
        app.profile.stars=[3]*10+[0]*10; app.profile.buildings=5; app.draw(); app.start(5); app.draw()
        app.action('new'); app.draw()
    def test_purchase_and_partial_mission_survive_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'v3.json'; app=ProjectApplication(save_path=path,muted=True)
            app.profile.stars=[3]*5+[0]*15; app.profile.credits=500
            app.action('buy:extra'); app.start(5); app.action('use:extra'); app.engine.drop(430); app.action('hub')
            r=ProjectApplication(save_path=path,muted=True)
            self.assertEqual(r.profile.credits,400); self.assertEqual(r.profile.inventory['extra'],0)
            r.action('resume'); self.assertEqual(r.engine.extra,3); self.assertEqual(r.engine.drops,1)

if __name__=='__main__': unittest.main()
