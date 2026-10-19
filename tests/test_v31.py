"""V3.1 : longueur réelle des missions et assemblage pédagogique complet."""
import os,random,json,tempfile
from pathlib import Path
import unittest
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
import pygame
from circuit_merge.campaign import MissionEngine,MISSIONS,Profile,CampaignStore
from circuit_merge.pc_builder import PCBuild,PARTS
from circuit_merge.pc_view import ZONES
from circuit_merge.pc_layout import PAGES
from circuit_merge.project_app import ProjectApplication

class BalanceTests(unittest.TestCase):
    def test_long_missions_have_real_solutions_without_large_deliveries_or_bonus(self):
        profile=Profile()
        for i,m in enumerate(MISSIONS[:10]):
            with self.subTest(mission=i+1):
                self.assertLessEqual(max(m.sequence),1 if i<6 else 2)
                e=MissionEngine(i); rng=random.Random(1)
                while e.remaining and not e.outcome:
                    x=556
                    if i==9:
                        same=[p for p in e.pieces.values() if p.level==e.current_level]
                        x=min(same,key=lambda p:p.body.position.y).body.position.x if same else rng.choice([450,500,556,610,660])
                    self.assertTrue(e.drop(x))
                    for _ in range(720):e.step()
                    e.events.clear()
                for _ in range(2400):e.step()
                self.assertEqual(e.outcome,'won')
                self.assertGreaterEqual(e.drops,24)
                self.assertLessEqual(e.drops,m.par)
                self.assertFalse(e.used)
                profile.award(e)
        self.assertEqual(profile.completed,10)
        for _ in range(5):self.assertTrue(profile.build())

    def test_legacy_suspended_mission_keeps_rules_new_attempt_uses_new_rules(self):
        e=MissionEngine(4,ruleset=1); data=e.campaign_snapshot(); del data['ruleset']
        r=MissionEngine.restore(json.loads(json.dumps(data)))
        self.assertEqual(r.mission.target,1)
        self.assertEqual(r.current_level,3)
        fresh=MissionEngine(4)
        self.assertEqual(fresh.mission.target,3)
        self.assertLessEqual(fresh.current_level,1)
        self.assertEqual(MissionEngine.restore(fresh.campaign_snapshot()).ruleset,2)

class AssemblyTests(unittest.TestCase):
    def test_dependencies_wrong_order_and_complete_boot(self):
        b=PCBuild()
        self.assertFalse(b.install('cpu')[0]); self.assertFalse(b.boot()[0])
        for key in PARTS:self.assertTrue(b.install(key)[0],key)
        self.assertTrue(b.boot()[0]); self.assertTrue(b.booted)
        self.assertFalse(b.remove('psu')[0]); self.assertFalse(b.remove('board')[0])
        self.assertTrue(b.remove('pcie')[0]); self.assertFalse(b.booted)
        self.assertFalse(b.boot()[0]); self.assertTrue(b.install('pcie')[0]);self.assertTrue(b.boot()[0])

    def test_duplicate_and_unknown_install_do_not_change_state(self):
        b=PCBuild(); b.install('case'); before=b.snapshot()
        self.assertFalse(b.install('case')[0]); self.assertFalse(b.install('mystery')[0])
        self.assertEqual(before,b.snapshot())

    def test_roundtrip_and_invalid_dependencies(self):
        b=PCBuild()
        for key in PARTS:b.install(key)
        b.boot();self.assertEqual(PCBuild.restore(b.snapshot()).snapshot(),b.snapshot())
        with self.assertRaises(ValueError):PCBuild.restore({'installed':['cpu'],'booted':False})
        with self.assertRaises(ValueError):PCBuild.restore({'installed':['unknown'],'booted':False})

    def test_old_profile_migrates_and_new_mount_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'save.json'; store=CampaignStore(path)
            p=Profile(credits=500,stars=[3]+[0]*9); self.assertTrue(store.save(p))
            data=json.loads(path.read_text(encoding='utf8'));del data['pc_build']
            path.write_text(json.dumps(data),encoding='utf8')
            q=store.load();self.assertEqual(q.credits,500);self.assertIsNone(q.pc_build)
            b=PCBuild();b.install('case');b.install('board');q.pc_build=b.snapshot()
            self.assertTrue(store.save(q)); self.assertEqual(store.load().pc_build,b.snapshot())

class AssemblyUITests(unittest.TestCase):
    def tearDown(self):pygame.quit()
    def test_real_clicks_place_parts_and_boot_without_dropping_merge_pieces(self):
        a=ProjectApplication(persist=False,muted=True);a.action('pc');a.draw()
        def click(logical):
            rect=a._viewport(); x,y=logical
            a._press((rect.x+x*rect.width/1120,rect.y+y*rect.height/900));a.draw()
        for k in PARTS:
            a.action('pc:page:'+str(0 if k in PAGES[0] else 1));a.draw()
            rect=a._viewport()
            def native(pos):return (rect.x+pos[0]*rect.width/1120,rect.y+pos[1]*rect.height/900)
            source=native(a.view.pc_cards[k].center);target=native(pygame.Rect(ZONES[k]).center)
            a.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,pos=source,button=1))
            a.handle_event(pygame.event.Event(pygame.MOUSEMOTION,pos=target,rel=(0,0),buttons=(1,0,0)))
            a.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP,pos=target,button=1))
            a.draw();self.assertIn(k,a.pc.installed)
        click(a.view.buttons['pc:boot'].center)
        self.assertTrue(a.pc.booted);self.assertEqual(a.engine.drops,0)
        a.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
        self.assertEqual(a.engine.drops,0)

    def test_wrong_placement_and_reset_confirmation_preserve_campaign(self):
        a=ProjectApplication(persist=False,muted=True);a.profile.credits=123
        a.start(0);a.engine.drop();a.action('hub');attempt=a.profile.active['attempt_id']
        a.action('pc');a.action('pc:select:case');a.draw()
        rect=a._viewport();a._press((rect.x+830*rect.width/1120,rect.y+780*rect.height/900))
        self.assertFalse(a.pc.installed)
        a.pc.install('case');a.action('pc:reset');a.draw();a.action('pc:cancel')
        self.assertIn('case',a.pc.installed)
        a.action('pc:reset');a.action('pc:confirm')
        self.assertFalse(a.pc.installed);self.assertEqual(a.profile.credits,123)
        self.assertEqual(a.profile.active['attempt_id'],attempt)
        a.action('hub');a.action('resume');self.assertEqual(a.engine.drops,1)

if __name__=='__main__':unittest.main()
