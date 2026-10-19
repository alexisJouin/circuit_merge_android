"""Chantier procédural et interface V3. Le dessin ne modifie jamais l'économie."""
import math
import pygame
from . import config as C
from .view import View
from .campaign import MISSIONS,BUILDINGS,TOOLS,MissionEngine,CHAPTERS
from .geometry import geometry_for,landing_y
from .faces import Personality

class WorldView(View):
    def __init__(self):
        super().__init__()
        self.chapter=0; self.world_time=0.; self.worker=Personality(2026)
        self.tool=None; self.profile=None; self.flash=0.
        self.subtitle='V3.3 / Projet Q — Chaque fusion fait avancer le chantier.'
    def advance_world(self,dt,menu=True):
        self.world_time+=dt; self.worker.advance(dt); self.flash=max(0,self.flash-dt)
        if menu: self.toast_time=max(0,self.toast_time-dt)
    def star(self,x,y,filled=True,r=7):
        points=[(x+math.cos(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.43),
                 y+math.sin(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.43)) for i in range(10)]
        pygame.draw.polygon(self.canvas,C.ORANGE if filled else C.LINE,points)
    def header(self,p,mouse,subtitle):
        self.buttons.clear(); self.canvas.blit(self.background,(0,0))
        self.text('CIRCUIT MERGE',(32,24),32)
        self.text('PROJET Q',(286,22),36,C.TEAL)
        self.text(subtitle,(34,65),20,C.MUTED)
        self.panel((735,20,352,73),C.ORANGE)
        self.text(f'{p.credits} crédits',(755,32),28,C.ORANGE)
        self.text(f'{sum(p.stars)} / {len(MISSIONS)*3} étoiles   ·   {p.completed} / {len(MISSIONS)} missions',(755,66),18,C.MUTED)
    def laboratory(self,p):
        s=self.canvas; n=p.buildings
        self.panel((32,116,675,434),C.TEAL)
        self.text('LABORATOIRE 01',(54,136),20,C.TEAL)
        self.text('Le chantier de ton ordinateur quantique',(54,164),22)
        floor=[(72,399),(390,260),(672,410),(352,529)]
        pygame.draw.polygon(s,(28,53,65) if n else (29,36,44),floor)
        pygame.draw.polygon(s,(75,126,138) if n else C.LINE,floor,2)
        for i in range(1,8):
            t=i/8
            pygame.draw.line(s,(43,77,90) if n else (37,44,52),(72+318*t,399-139*t),(352+320*t,529-119*t))
        for i in range(1,7):
            t=i/7
            pygame.draw.line(s,(43,77,90) if n else (37,44,52),(72+280*t,399+130*t),(390+282*t,260+150*t))
        pygame.draw.line(s,(56,75,105),(451,215),(451,434))
        for y,w in ((249,94),(287,76),(325,56),(363,37)):
            pygame.draw.ellipse(s,(66,83,113),(451-w/2,y,w,19),1)
        self.text('FUTUR CŒUR QUANTIQUE',(442,454),16,(133,150,179),True)
        for x,y in ((157,385),(254,419),(540,404)):
            pygame.draw.rect(s,(75,60,43),(x,y,45,33),border_radius=3)
            pygame.draw.line(s,(160,121,65),(x+22,y),(x+22,y+33),3)
        if n>=2:
            pygame.draw.lines(s,C.TEAL,False,[(584,374),(607,402),(354,505),(160,414)],3)
            pygame.draw.rect(s,(34,64,75),(570,309,54,82),border_radius=6)
            self.text('PWR',(580,321),18,C.TEAL)
            for y in (350,364,378): pygame.draw.circle(s,C.TEAL,(598,y),3)
            for pos in ((88,392),(653,408),(354,513)): pygame.draw.circle(s,(75,185,177),pos,6)
        if n>=3:
            for x,y in ((149,366),(247,409)):
                pygame.draw.rect(s,(60,94,109),(x-17,y+19,91,12),border_radius=3)
                pygame.draw.rect(s,(36,56,76),(x,y-22,53,40),border_radius=4)
                pygame.draw.rect(s,(53,146,157),(x+5,y-17,43,29),border_radius=2)
                for k in range(3): pygame.draw.line(s,C.TEAL,(x+10,y-10+k*7),(x+35,y-10+k*7))
        if n>=4:
            for x,y in ((267,293),(325,270)):
                pygame.draw.rect(s,(23,39,54),(x,y-61,43,102),border_radius=5)
                for k in range(6):
                    pygame.draw.rect(s,(62,86,101),(x+5,y-54+k*14,33,10),border_radius=2)
                    pygame.draw.circle(s,C.TEAL,(x+31,y-49+k*14),2)
        if n>=5:
            pygame.draw.lines(s,(173,190,207),False,[(389,414),(389,215),(507,215),(507,414)],7)
            pygame.draw.line(s,C.ORANGE,(395,224),(500,224),3)
            pygame.draw.ellipse(s,(136,113,191),(406,386,92,28),2)
            for k in range(4):
                w=88-k*18; pygame.draw.ellipse(s,(111,187,204),(451-w/2,243+k*34,w,17),2)
            self.text('CONTRÔLE OPÉRATIONNEL' if n>=10 else 'LABORATOIRE OPÉRATIONNEL',(443,483),18,C.TEAL,True)
        # Équipements visibles du chapitre 2 : réseau, horloge, émission, lecture.
        if n>=6:
            pygame.draw.lines(s,C.ORANGE,False,[(171,386),(300,451),(551,359),(598,351)],3)
            for x,y in ((300,451),(551,359)):
                pygame.draw.rect(s,(41,72,87),(x-20,y-8,40,16),border_radius=3)
                for k in range(5): pygame.draw.circle(s,C.TEAL,(x-13+k*6,y),2)
        if n>=7:
            pygame.draw.rect(s,(38,54,73),(82,253,100,60),border_radius=6)
            self.text('CLK / SYNC',(91,261),16,C.ORANGE)
            pulse=[(90+k*4,294-(12 if k%6<3 else 0)) for k in range(21)]
            pygame.draw.lines(s,C.TEAL,False,pulse,2)
        if n>=8:
            pygame.draw.rect(s,(38,54,73),(527,219,123,66),border_radius=6)
            self.text('COMMANDE',(537,226),16,C.TEAL)
            wave=[(536+k*2,261+8*math.sin(k*.3+self.world_time*2)) for k in range(52)]
            pygame.draw.lines(s,C.ORANGE,False,wave,2)
        if n>=9:
            pygame.draw.rect(s,(38,54,73),(525,295,123,55),border_radius=6)
            self.text('ACQUISITION',(532,302),16,C.TEAL)
            for k in range(12):
                height=7+int(9*(1+math.sin(k+self.world_time)))
                pygame.draw.rect(s,C.TEAL,(534+k*9,342-height,5,height))
        if n>=10:
            pygame.draw.lines(s,C.TEAL,False,[(182,283),(207,283),(207,207),(587,207),(587,219)],2)
            pygame.draw.circle(s,C.ORANGE,(int(207+(self.world_time*70)%380),207),4)
        self.component(0,170+40*math.sin(self.world_time*.45),474,22,personality=self.worker,
                       expression='joy' if self.flash else 'idle')
        if self.flash:
            for k in range(12):
                a=k*math.tau/12+self.world_time
                pygame.draw.circle(s,C.ORANGE,(round(451+110*math.cos(a)),round(330+70*math.sin(a))),3)
    def toast_layer(self):
        if self.toast_time>0:
            pygame.draw.rect(self.canvas,(37,60,73),(30,860,1060,32),border_radius=8)
            self.text(self.toast,(45,867),20)
    def render_hub(self,p,mouse,active=None):
        self.header(p,mouse,f'CHAPITRE {self.chapter+1} / {CHAPTERS[self.chapter].upper()}')
        self.laboratory(p)
        self.panel((734,116,354,280),C.ORANGE)
        self.text('PROCHAINE CONSTRUCTION',(756,138),20,C.ORANGE)
        if p.buildings<len(BUILDINGS):
            title,price,need,desc=BUILDINGS[p.buildings]
            self.text(title,(756,173),28)
            self.wrapped(desc,756,214,306,22,C.MUTED,25)
            self.text(f'{price} crédits  ·  {need} missions réussies',(756,287),20,C.TEAL)
            self.button('build','Construire',(756,333,309,43),mouse,True)
        else:
            self.text('Le pilotage est prêt !',(756,178),26,C.TEAL)
            self.wrapped('Deux chapitres terminés ! La prochaine étape du projet sera la cryogénie.',756,220,305,22,C.MUTED,26)
        self.panel((734,410,354,140))
        self.text('PROJET GLOBAL',(756,430),20,C.MUTED)
        for i in range(5):
            pygame.draw.rect(self.canvas,C.TEAL if i<min(2,p.buildings//5) else C.LINE,(756+i*61,465,51,7),border_radius=3)
        self.wrapped('2 chapitres jouables. À venir : cryogénie, qubits et calibration.',756,490,306,18,C.MUTED,20)
        self.button('pc','Mode libre : Montage PC',(735,565,353,43),mouse,True)
        self.button('chapter:0','1 / Fondations',(32,563,275,36),mouse,self.chapter==0)
        self.button('chapter:1','2 / Contrôle et signaux',(320,563,381,36),mouse,self.chapter==1)
        self.text('Première victoire : prime de recherche. Rejouer : crédits et étoiles.',(34,600),18,C.MUTED)
        for local,m in enumerate(MISSIONS[self.chapter*10:self.chapter*10+10]):
            i=self.chapter*10+local
            x=32+local%5*214; y=631+local//5*82; enabled=p.available(i)
            rect=pygame.Rect(x,y,201,70); self.buttons[f'mission:{i}']=rect
            active=enabled and not p.stars[i]
            color=(36,72,80) if active else C.PANEL
            if enabled and rect.collidepoint(mouse): color=(37,60,73)
            pygame.draw.rect(self.canvas,color,rect,border_radius=12)
            pygame.draw.rect(self.canvas,C.TEAL if active else C.LINE,rect,2 if active else 1,border_radius=12)
            label=f'{i+1:02d}  {m.title}'
            if self.fonts[20].size(label)[0]>173:
                while self.fonts[20].size(label+'…')[0]>173: label=label[:-1]
                label+='…'
            self.text(label,(x+14,y+13),20,C.TEXT if enabled else C.MUTED)
            self.text(f'Record {p.scores[i]}' if enabled else 'Verrouillée',(x+14,y+40),18,C.MUTED)
            for k in range(3): self.star(x+153+k*13,y+50,p.stars[i]>k,5)
        self.button('shop','Équipement',(32,809,204,48),mouse)
        self.button('free','Atelier libre',(250,809,204,48),mouse)
        self.button('resume','Reprendre' if p.active else 'Aucune mission en cours',(468,809,294,48),mouse,bool(p.active))
        self.button('sound','Son : ON' if p.sound else 'Son : OFF',(776,809,154,48),mouse)
        self.button('quit','Quitter',(944,809,144,48),mouse)
        self.toast_layer(); return self.canvas
    def render_briefing(self,p,index,mouse):
        self.header(p,mouse,'BRIEFING / Les livraisons restent identiques à chaque essai.')
        m=MISSIONS[index]
        self.panel((140,140,840,590),C.TEAL)
        self.text(f'MISSION {index+1:02d}',(178,175),22,C.TEAL)
        self.text(m.title,(178,217),44)
        self.wrapped(m.story,178,283,720,26,C.MUTED,32)
        self.panel((178,372,760,98),C.ORANGE)
        self.text('OBJECTIF',(200,390),20,C.ORANGE); self.text(m.goal,(200,426),28)
        size='étroit' if m.width<480 else 'standard'
        self.text(f'{m.budget} lâchers   ·   Atelier {size}   ·   {len(m.stock)} pièces déjà présentes',(178,500),22,C.MUTED)
        self.text(f'3 étoiles : {m.par} lâchers ou moins   |   2 étoiles : {m.par+3} ou moins',(178,540),22,C.TEAL)
        self.wrapped('Bonus facultatifs. E / molette : tourner. F1 : collisions. F2 : ralenti.',178,582,730,22,C.MUTED,26)
        self.button('hub','Retour au chantier',(178,657,352,48),mouse)
        self.button('start','Lancer la mission',(556,657,382,48),mouse,True)
        self.toast_layer(); return self.canvas
    def render_shop(self,p,mouse):
        self.header(p,mouse,'ÉQUIPEMENT / Des coups de pouce facultatifs pour tes missions.')
        self.text('Deux familles d’outils maximum par tentative.',(34,132),26,C.TEAL)
        descriptions={'remove':'Retire un composant. Les pièces marquées sont protégées.',
                      'swap':'Passe à la prochaine valeur différente dans la livraison.',
                      'extra':'Ajoute trois lâchers au budget de la mission en cours.'}
        for i,(key,(title,unlock,charge,need)) in enumerate(TOOLS.items()):
            x=32+i*358; self.panel((x,191,340,515),C.TEAL)
            self.component((4,1,5)[i],x+170,264,48,personality=self.worker)
            self.text(title,(x+22,336),32)
            self.wrapped(descriptions[key],x+22,385,290,22,C.MUTED,27)
            self.text(f'Réserve : {p.inventory[key]} charge(s)',(x+22,478),22,C.TEAL)
            label=f'Acheter : {charge} crédits' if key in p.unlocked else f'Débloquer : {unlock} crédits'
            self.button('buy:'+key,label,(x+20,539,300,48),mouse,True)
            self.wrapped(f'Après {need} missions · déblocage avec 1 charge',x+18,630,302,18,C.MUTED,21)
        self.button('hub','Retour au chantier',(32,790,300,48),mouse)
        self.toast_layer(); return self.canvas
    def render_result(self,p,engine,reward,mouse):
        self.header(p,mouse,'RAPPORT DE MISSION / Chaque assemblage fait avancer le Projet Q.')
        won=engine.outcome=='won'
        self.panel((175,158,770,545),C.TEAL if won else C.RED)
        self.component(5,560,249,61,personality=self.worker,expression='joy' if won else 'worried')
        self.text('MISSION ACCOMPLIE' if won else 'NOUVEL ESSAI ?',(560,339),44,C.TEAL if won else C.ORANGE,True)
        self.text(MISSIONS[engine.index].title,(560,397),26,C.TEXT,True)
        self.text(f'{engine.score} points  ·  {engine.drops} lâchers',(560,440),26,C.MUTED,True)
        if won:
            self.text(f'+ {reward} crédits de recherche',(560,482),28,C.ORANGE,True)
            for i in range(3): self.star(520+i*40,535,p.stars[engine.index]>i,15)
        else:
            self.wrapped('Budget épuisé ou atelier saturé. Les livraisons seront identiques au prochain essai.',238,487,650,24,C.MUTED,29)
        self.button('retry','Rejouer',(215,610,245,48),mouse)
        self.button('hub','Retour au chantier',(480,610,425,48),mouse,True)
        self.toast_layer(); return self.canvas
    def _left_panel(self,e,best,mouse,debug,fps,slow):
        if not isinstance(e,MissionEngine): return super()._left_panel(e,best,mouse,debug,fps,slow)
        m=e.mission
        self.panel((32,112,244,288),C.TEAL)
        self.text(f'MISSION {e.index+1:02d}',(52,133),20,C.TEAL)
        self.wrapped(m.title,52,164,204,26,C.TEXT,27)
        self.wrapped(m.goal,52,229,201,24,C.ORANGE,26)
        self.text(f'Progression : {e.progress} / {m.target}',(52,302),22)
        self.text(f'Score : {e.score}'+(f' / {m.score_goal}' if m.score_goal else ''),(52,337),22,C.MUTED)
        self.panel((32,418,244,133),C.ORANGE)
        self.text('LÂCHERS RESTANTS',(52,438),20,C.MUTED)
        self.text(str(e.remaining),(52,470),58,C.ORANGE)
        if not e.remaining: self.text('Résolution en cours.',(52,530),18,C.MUTED)
        self.text('TES OUTILS',(52,574),20,C.MUTED)
        for i,(key,(label,*_)) in enumerate(TOOLS.items()):
            count=self.profile.inventory[key]
            self.button('use:'+key,f'{label}  ×{count}',(32,607+i*53,244,43),mouse,key==self.tool)
        self.button('hub','Suspendre / chantier',(32,783,244,43),mouse)
        self.button('debug','F1 : contours '+('ON' if debug else 'OFF'),(32,841,244,33),mouse)
    def _bucket(self,e,debug,aiming,mouse):
        if not isinstance(e,MissionEngine): return super()._bucket(e,debug,aiming,mouse)
        s=self.canvas; l,r,f=e.left,e.right,e.floor
        pygame.draw.rect(s,(15,30,39),(l,C.WALL_TOP,r-l,f-C.WALL_TOP),border_radius=12)
        for x in range(round(l)+20,round(r),28):
            for y in range(round(C.WALL_TOP)+20,round(f),28): pygame.draw.circle(s,(26,47,55),(x,y),1)
        wall=((l,C.WALL_TOP),(l,f),(r,f),(r,C.WALL_TOP))
        pygame.draw.lines(s,(44,73,81),False,wall,12); pygame.draw.lines(s,(102,162,162),False,wall,2)
        for x in range(round(l)+8,round(r)-8,17):
            pygame.draw.line(s,C.RED if e.danger_ratio else (116,91,84),(x,C.DANGER_Y),(x+8,C.DANGER_Y),2)
        if aiming and e.remaining:
            key=(int(e.time*12),e.aim_x,e.aim_angle,e.current_level,len(e.pieces))
            if getattr(self,'_q_projection_key',None)!=key:
                self._q_projection_key=key
                self._q_landing=landing_y(e.current_level,e.aim_x,e.aim_angle,e.pieces.values(),C.DROP_Y,f-C.WALL_THICKNESS)
            self.component(e.current_level,e.aim_x,self._q_landing,angle=e.aim_angle,alpha=48)
            self.component(e.current_level,e.aim_x,C.DROP_Y,angle=e.aim_angle,personality=self.preview_face,alpha=255 if e.can_drop else 95)
            self.text(C.COMPONENTS[e.current_level].name,(e.aim_x,122),20,C.TEXT,True)
        for p in e.pieces.values():
            x,y=p.body.position; face=self.face_for(p.uid)
            target=p.body.world_to_local(mouse) if mouse!=(-1,-1) else (0,0)
            gaze=(max(-1,min(1,target[0]/130)),max(-1,min(1,target[1]/130)))
            self.component(p.level,x,y,angle=p.body.angle,personality=face,gaze=gaze,
                           expression=face.expression(p.body.velocity.y,p.body.angular_velocity,p.overflow_time))
            if p.uid in e.marked:
                bb=p.bounds
                pygame.draw.rect(s,C.ORANGE,(bb.left-5,bb.bottom-5,bb.right-bb.left+10,bb.top-bb.bottom+10),2,border_radius=5)
            if debug:
                for shape in p.shapes: pygame.draw.polygon(s,C.TEXT,[p.body.local_to_world(v) for v in shape.get_vertices()],1)
        if self.tool: self.text('PINCE : clique une pièce non marquée',(556,808),20,C.ORANGE,True)
    def _modal(self,mode,e,best,mouse):
        if mode!='restart' or not isinstance(e,MissionEngine): return super()._modal(mode,e,best,mouse)
        shade=pygame.Surface((C.WIDTH,C.HEIGHT),pygame.SRCALPHA); shade.fill((3,11,20,210)); self.canvas.blit(shade,(0,0))
        self.buttons.clear(); self.panel((302,231,516,436),C.TEAL)
        self.text('Recommencer la mission ?',(560,290),32,C.TEXT,True)
        self.wrapped('Le stock et les livraisons seront réinitialisés. Les charges déjà utilisées restent consommées.',353,357,414,26,C.MUTED,31)
        self.button('confirm_new','Recommencer',(351,544,199,49),mouse,True)
        self.button('close','Continuer',(567,544,199,49),mouse)
    def render_play(self,p,e,best,mouse,**kwargs):
        self.profile=p; canvas=super().render(e,best,mouse,**kwargs)
        if kwargs.get('mode') or not isinstance(e,MissionEngine): self.button('hub','Chantier',(340,24,175,40),mouse)
        return canvas
