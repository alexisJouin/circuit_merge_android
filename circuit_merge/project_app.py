"""Navigation du Projet Q, transactions et sauvegarde séparée de la V2."""
import os
from pathlib import Path
import time
import pygame
from .app import Application
from .engine import GameEngine
from .campaign import Profile,CampaignStore,MissionEngine,BUILDINGS
from .world_view import WorldView
from .pc_builder import PCBuild, PARTS
from .pc_view import render_pc
from .pc_layout import ZONES, PLACED, PAGES, accepts

class ProjectApplication(Application):
    def __init__(self,*,save_path=None,persist=True,muted=False):
        self.ready=False; self.page='hub'; self.selected=0; self.reward=0
        self.project_persist=persist; self.campaign_store=CampaignStore(save_path)
        self.profile=self.campaign_store.load() if persist else Profile()
        self.pc=PCBuild.restore(self.profile.pc_build) if self.profile.pc_build else PCBuild()
        self.pc_selected=None; self.pc_guide=False; self.pc_confirm=False
        self.pc_drag=None; self.pc_page=0
        super().__init__(persist=False,muted=muted,save_path=Path.cwd()/'unused_v2.json')
        self.view=WorldView(); self.view.chapter=1 if self.profile.completed>=10 else 0; self.audio.enabled=self.profile.sound and not muted
        self.profile.sound=self.audio.enabled
        self.ready=True; self.engine=GameEngine(3); self.mode=None; self.best=self.profile.best
        pygame.display.set_caption('Circuit Merge V3.3 - Projet Q / Chapitres 1 et 2')
        if self.campaign_store.error: self.view.notify(self.campaign_store.error,8)
        self.draw()
    @property
    def active(self):
        return getattr(self,'ready',False) and self.page=='play' and super().active and not getattr(self.engine,'outcome',None)
    def save(self):
        if not self.ready: return
        if self.page=='play':
            if isinstance(self.engine,MissionEngine):
                if not self.engine.outcome: self.profile.active=self.engine.campaign_snapshot()
            else: self.profile.free_round=self.engine.snapshot()
        self.profile.pc_build=self.pc.snapshot()
        self.profile.best=max(self.profile.best,self.best); self.profile.sound=self.audio.enabled
        if self.project_persist and not self.campaign_store.save(self.profile): self.view.notify(self.campaign_store.error,8)
        self.last_autosave=time.monotonic()
    def _clear_view(self):
        self.view.effects.clear(); self.view.particles.clear(); self.view.personalities.clear()
        self.view.goal_time=0; self.view.tool=None
        self.view._projection_key=None; self.view._q_projection_key=None
        self.inspect_uid=None; self.dragging=False; self.accumulator=0
    def start(self,index):
        if not self.profile.available(index): return
        self.selected=index; self.engine=MissionEngine(index); self._clear_view()
        self.page='play'; self.mode=None; self.profile.active=self.engine.campaign_snapshot(); self.save()
    def action(self,name):
        if not self.ready: return
        if name in ('pc','hub','quit') or name.startswith('pc:'):
            self.pc_drag=None
        if name=='pc':
            self.save(); self.page='pc'; self.mode=None; self.pc_confirm=False
        elif name.startswith('pc:'):
            action=name[3:]
            if action.startswith('select:'):
                self.pc_selected=action.split(':')[1]
            elif action.startswith('page:'): self.pc_page=int(action[-1])
            elif action=='guide': self.pc_guide=not self.pc_guide
            elif action=='reset': self.pc_confirm=True
            elif action=='cancel': self.pc_confirm=False
            elif action=='confirm':
                self.pc=PCBuild(); self.pc_selected=None; self.pc_confirm=False; self.save()
            elif action=='remove':
                ok,msg=self.pc.remove(self.pc_selected)
                self.view.notify(msg,6)
                if ok: self.save()
            elif action=='boot':
                ok,msg=self.pc.boot(); self.view.notify(msg,9); self.save()
        elif name=='hub':
            self.save(); self.page='hub'; self.mode=None; self.view.tool=None; self.dragging=False
        elif name.startswith('chapter:'):
            self.view.chapter=int(name.split(':')[1]); self.page='hub'
        elif name.startswith('mission:'):
            i=int(name.split(':')[1])
            if self.profile.available(i): self.selected=i; self.page='briefing'
            else: self.view.notify('Réussis la mission précédente pour ouvrir celle-ci.')
        elif name=='start':
            if self.profile.active: self.page='confirm'
            else: self.start(self.selected)
        elif name=='confirm':
            self.profile.active=None; self.start(self.selected)
        elif name=='cancel': self.page='hub'
        elif name=='resume':
            if self.profile.active:
                try:
                    self.engine=MissionEngine.restore(self.profile.active); self.selected=self.engine.index
                    self._clear_view(); self.page='play'; self.mode='pause'
                except (ValueError,KeyError,TypeError,IndexError): self.view.notify('Tentative incompatible : relance sa mission.',6)
        elif name in ('retry','confirm_new'):
            if isinstance(self.engine,MissionEngine): self.start(self.engine.index)
            else:
                self.engine=GameEngine(); self._clear_view(); self.page='play'; self.mode=None; self.save()
        elif name=='shop': self.page='shop'
        elif name=='free':
            self.engine=GameEngine.from_snapshot(self.profile.free_round) if self.profile.free_round else GameEngine()
            self._clear_view(); self.page='play'; self.mode='pause' if self.profile.free_round else None
        elif name=='build':
            if self.profile.build():
                self.view.flash=3.5; self.view.notify(BUILDINGS[self.profile.buildings-1][0]+' : construction terminée !',4); self.save()
            elif self.profile.buildings<len(BUILDINGS):
                _,price,need,_=BUILDINGS[self.profile.buildings]
                self.view.notify(f'Il faut {price} crédits et {need} missions réussies.',4)
        elif name.startswith('buy:'):
            if self.profile.buy(name.split(':')[1]): self.view.notify('Une charge ajoutée à ta réserve.'); self.save()
            else: self.view.notify('Crédits insuffisants ou outil encore verrouillé.')
        elif name.startswith('use:') and self.active and isinstance(self.engine,MissionEngine):
            key=name.split(':')[1]
            if self.profile.inventory[key]<=0: self.view.notify('Achète des charges depuis le chantier.')
            elif key=='remove': self.view.tool=None if self.view.tool=='remove' else 'remove'
            elif self.profile.use(self.engine,key):
                self.view._q_projection_key=None; self.view.notify('Bonus activé.'); self.save()
            else: self.view.notify('Livraison identique ou deux familles de bonus déjà utilisées.')
        elif name=='quit': self.save(); self.running=False
        elif name=='sound': self.audio.enabled=not self.audio.enabled; self.profile.sound=self.audio.enabled; self.save()
        elif name=='new' and isinstance(self.engine,MissionEngine): self.mode='restart'
        else: super().action(name)
        self.accumulator=0
    def _pc_press(self,pos,button=1,pointer='mouse'):
        self.mouse=self.logical_position(pos)
        if button==3:
            self.pc_drag=None; return
        if button!=1 or self.pc_drag is not None: return
        # Les cartes sont des objets à saisir, pas des boutons d'installation.
        if not self.pc_confirm:
            for key,rect in getattr(self.view,'pc_cards',{}).items():
                if rect.collidepoint(self.mouse):
                    self.pc_selected=key
                    if key not in self.pc.installed:
                        self.pc_drag={'key':key,'start':self.mouse,'pointer':pointer}
                    return
        for name,rect in self.view.buttons.items():
            if rect.collidepoint(self.mouse):
                self.action(name); self.draw(); return
        if not self.pc_confirm:
            for key in reversed(tuple(PARTS)):
                if key in self.pc.installed and pygame.Rect(PLACED[key]).collidepoint(self.mouse):
                    self.pc_selected=key; return

    def _pc_release(self,pos,pointer='mouse'):
        if not self.pc_drag or self.pc_drag['pointer']!=pointer: return
        self.mouse=self.logical_position(pos)
        drag=self.pc_drag; self.pc_drag=None
        # Un clic simple ouvre la fiche ; seul un vrai déplacement pose la pièce.
        if pygame.Vector2(self.mouse).distance_to(drag['start'])<6: return
        key=drag['key']
        if self.mouse==(-1.0,-1.0) or not accepts(key,self.mouse):
            self.view.notify('Pose refusée : '+PARTS[key].short+' rejoint '+PARTS[key].destination.lower()+'.',6)
            return
        ok,msg=self.pc.install(key)
        self.view.notify(msg,6)
        if ok: self.save()

    def _pc_event(self,event):
        if event.type in (pygame.QUIT,pygame.WINDOWFOCUSLOST,pygame.VIDEORESIZE):
            self.pc_drag=None
            if event.type==pygame.QUIT: self.save(); self.running=False
            elif event.type==pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode((max(500,event.w),max(420,event.h)),pygame.RESIZABLE)
            return
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if self.pc_drag: self.pc_drag=None
                elif self.pc_confirm: self.pc_confirm=False
                else: self.action('hub')
            elif event.key==pygame.K_m: self.action('sound')
            return
        # SDL peut doubler un toucher avec des événements souris synthétiques.
        if event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.MOUSEMOTION):
            if getattr(event,'touch',False): return
            if self.pc_drag and self.pc_drag['pointer']!='mouse': return
            if event.type==pygame.MOUSEBUTTONDOWN: self._pc_press(event.pos,event.button)
            elif event.type==pygame.MOUSEBUTTONUP and event.button==1: self._pc_release(event.pos)
            elif event.type==pygame.MOUSEMOTION: self.mouse=self.logical_position(event.pos)
        elif event.type in (pygame.FINGERDOWN,pygame.FINGERUP,pygame.FINGERMOTION):
            pointer=('finger',event.finger_id)
            if self.pc_drag and self.pc_drag['pointer']!=pointer: return
            w,h=self.screen.get_size(); pos=(event.x*w,event.y*h)
            if event.type==pygame.FINGERDOWN: self._pc_press(pos,pointer=pointer)
            elif event.type==pygame.FINGERUP: self._pc_release(pos,pointer)
            else: self.mouse=self.logical_position(pos)

    def _press(self,pos,button=1):
        if self.page=='pc': return self._pc_press(pos,button)
        self.mouse=self.logical_position(pos)
        for name,rect in self.view.buttons.items():
            if button==1 and rect.collidepoint(self.mouse): self.action(name); self.draw(); return
        if self.active and self.view.tool=='remove'  and button==1:
            p=self.engine.piece_at(*self.mouse)
            if p and self.profile.use(self.engine,'remove',p.uid):
                self.view.tool=None; self.view._q_projection_key=None
                self.view.notify('Composant retiré.'); self.save()
            else: self.view.notify('Choisis une pièce non marquée ; aucune charge consommée.')
            return
        if self.page=='play': super()._press(pos,button)
    def handle_event(self,event):
        if self.page=='pc': return self._pc_event(event)
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE and self.view.tool:
            self.view.tool=None; return
        if self.page=='play': return super().handle_event(event)
        if event.type==pygame.QUIT: self.running=False
        elif event.type==pygame.VIDEORESIZE:
            self.screen=pygame.display.set_mode((max(500,event.w),max(420,event.h)),pygame.RESIZABLE)
        elif event.type==pygame.MOUSEMOTION: self.mouse=self.logical_position(event.pos)
        elif event.type==pygame.MOUSEBUTTONDOWN: self._press(event.pos,event.button)
        elif event.type==pygame.FINGERDOWN:
            w,h=self.screen.get_size(); self._press((event.x*w,event.y*h))
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE: self.page='hub'
            elif event.key==pygame.K_m: self.action('sound')
    def update(self,elapsed):
        self.view.advance_world(min(max(elapsed,0),.1),self.page!='play')
        if self.page=='play':
            super().update(elapsed)
            if isinstance(self.engine,MissionEngine) and self.engine.outcome:
                self.reward=self.profile.award(self.engine); self.profile.active=None
                self.page='result'; self.mode=None; self.dragging=False; self.view.tool=None; self.save()
    def draw(self):
        if not self.ready: return super().draw()
        p=self.profile
        if self.page=='pc': canvas=render_pc(self.view,self.pc,self.pc_selected,self.mouse,self.pc_guide,self.pc_confirm,self.pc_drag,self.pc_page)
        elif self.page=='hub': canvas=self.view.render_hub(p,self.mouse,p.active)
        elif self.page=='shop': canvas=self.view.render_shop(p,self.mouse)
        elif self.page=='briefing': canvas=self.view.render_briefing(p,self.selected,self.mouse)
        elif self.page=='result': canvas=self.view.render_result(p,self.engine,self.reward,self.mouse)
        elif self.page=='confirm':
            self.view.header(p,self.mouse,'REMPLACER LA TENTATIVE EN COURS ?')
            self.view.panel((180,230,760,390))
            self.view.text('Une mission est déjà en cours',(216,272),36)
            self.view.wrapped('La nouvelle tentative remplacera celle suspendue. Les charges déjà utilisées restent consommées.',216,345,660,26,leading=32)
            self.view.button('cancel','Conserver',(216,532,285,48),self.mouse)
            self.view.button('confirm','Remplacer et commencer',(520,532,382,48),self.mouse,True)
            canvas=self.view.canvas
        else:
            canvas=self.view.render_play(p,self.engine,self.best,self.mouse,mode=self.mode,debug=self.debug,
                                        muted=not self.audio.enabled,fps=self.clock.get_fps(),slow=self.slow,inspect_uid=self.inspect_uid)
        self._fitted=self._viewport(); self.screen.fill((5,10,16))
        self.screen.blit(pygame.transform.smoothscale(canvas,self._fitted.size),self._fitted); pygame.display.flip()

def launch_project(*,save_path=None,muted=False,screenshot=None,smoke_test=None):
    if screenshot or smoke_test:
        os.environ.setdefault('SDL_VIDEODRIVER','dummy'); os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    app=ProjectApplication(save_path=save_path,muted=muted,persist=not(screenshot or smoke_test))
    if screenshot:
        app.draw(); Path(screenshot).parent.mkdir(parents=True,exist_ok=True)
        pygame.image.save(app.view.canvas,str(screenshot)); pygame.quit()
    else:
        if smoke_test: app.start(0); app.engine.drop()
        app.run(smoke_test)
