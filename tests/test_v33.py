"""Chapitre 2 : parcours physique, migration et navigation réelle."""
import json
import os
import tempfile
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from circuit_merge.campaign import Profile, CampaignStore, MissionEngine, MISSIONS, BUILDINGS
from circuit_merge.project_app import ProjectApplication
from circuit_merge.pc_builder import PCBuild
from probe_chapter2 import solve

class ChapterTwoTests(unittest.TestCase):
    def test_physical_campaign_without_bonus_funds_construction(self):
        p=Profile(stars=[1]*10,buildings=5)
        for i in range(10,20):
            with self.subTest(mission=i+1):
                self.assertTrue(p.available(i))
                self.assertLessEqual(max(MISSIONS[i].sequence),2)
                e=solve(i)
                self.assertEqual(e.outcome,'won')
                self.assertGreaterEqual(e.drops,50)
                self.assertLessEqual(e.drops,e.mission.par)
                self.assertFalse(e.used)
                reward=p.award(e)
                self.assertGreater(reward,0)
                self.assertEqual(p.award(e),0)
                if i<19:self.assertTrue(p.available(i+1))
        for _ in range(5):self.assertTrue(p.build())
        self.assertEqual(p.buildings,10)
        self.assertFalse(p.build())
        self.assertGreaterEqual(p.credits,0)

    def test_v32_save_migrates_with_active_attempt_and_pc(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'profile.json'
            pc=PCBuild();pc.install('case');pc.install('board')
            old=dict(version=3,**vars(Profile(credits=789,stars=[3]*10,buildings=5)))
            old['stars']=old['stars'][:10];old['scores']=[321]*10
            old['pc_build']=pc.snapshot()
            old['active']=MissionEngine(9).campaign_snapshot()
            path.write_text(json.dumps(old),encoding='utf8')
            store=CampaignStore(path);p=store.load()
            self.assertFalse(store.error)
            self.assertEqual(p.credits,789);self.assertEqual(p.buildings,5)
            self.assertEqual(p.stars,[3]*10+[0]*10)
            self.assertEqual(p.scores,[321]*10+[0]*10)
            self.assertEqual(p.pc_build,pc.snapshot())
            self.assertEqual(p.active,json.loads(json.dumps(old['active'])))
            self.assertTrue(p.available(10));self.assertFalse(p.available(11))
            self.assertTrue(store.save(p))
            self.assertEqual(vars(store.load()),vars(p))

    def test_chapter_two_resume_at_last_mission(self):
        e=MissionEngine(19);e.drop(500)
        for _ in range(400):e.step()
        with tempfile.TemporaryDirectory() as d:
            store=CampaignStore(Path(d)/'profile.json')
            p=Profile(stars=[1]*19+[0],buildings=9)
            p.active=e.campaign_snapshot();self.assertTrue(store.save(p))
            q=store.load();self.assertFalse(store.error)
            r=MissionEngine.restore(q.active)
            self.assertEqual(r.index,19);self.assertEqual(r.drops,1)
            self.assertEqual(r.mission,e.mission)
            self.assertEqual(r.attempt_id,e.attempt_id)

    def test_construction_gates_and_credits(self):
        p=Profile(credits=10000,stars=[1]*10,buildings=5)
        before=p.credits
        self.assertFalse(p.build());self.assertEqual(p.credits,before)
        p.stars[10:12]=[1,1]
        self.assertTrue(p.build());self.assertEqual(p.credits,before-BUILDINGS[5][1])
        p.stars=[1]*20;p.buildings=9;p.credits=849
        self.assertFalse(p.build());self.assertEqual(p.credits,849)

class ChapterTwoUITests(unittest.TestCase):
    def tearDown(self):pygame.quit()
    def test_chapter_tabs_locks_briefing_and_final_world(self):
        a=ProjectApplication(persist=False,muted=True)
        def click(name):
            a.draw();pos=a.view.buttons[name].center;r=a._viewport()
            a._press((r.x+pos[0]*r.width/1120,r.y+pos[1]*r.height/900));a.draw()
        click('chapter:1')
        self.assertEqual(a.view.chapter,1)
        self.assertIn('mission:19',a.view.buttons);self.assertNotIn('mission:0',a.view.buttons)
        for rect in a.view.buttons.values():
            self.assertTrue(pygame.Rect(0,0,1120,900).contains(rect))
        click('mission:10');self.assertEqual(a.page,'hub')
        a.profile.stars[:10]=[1]*10
        click('mission:10');self.assertEqual(a.page,'briefing')
        click('start');self.assertEqual(a.engine.index,10)
        a.action('hub');click('chapter:0');self.assertIn('mission:0',a.view.buttons)
        a.profile.stars=[3]*20;a.profile.buildings=10
        a.action('chapter:1');a.draw()
        a.action('pc');a.draw();self.assertEqual(a.page,'pc')

if __name__=='__main__':unittest.main()
