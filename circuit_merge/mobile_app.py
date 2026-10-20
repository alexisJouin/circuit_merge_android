"""Portrait mobile UI. Shared rules/saves, bounded caches, one frame presentation."""
from collections import OrderedDict
import math
from pathlib import Path
import pygame
from .project_app import ProjectApplication
from .world_view import WorldView
from .campaign import MISSIONS, MissionEngine
from .model import RoundState
from . import config as C

W, H = 600, 1080
BG, PANEL = (13, 24, 38), (28, 46, 65)
WHITE, MINT, MUTED = (239, 247, 250), (99, 232, 195), (159, 182, 201)


class MobileView(WorldView):
    def __init__(self):
        super().__init__()
        self.canvas = pygame.Surface((W, H))
        self.labels = OrderedDict()
        self.rotations = OrderedDict()
        self.bases = {}
        self.cache_bytes = 0

    def animate(self, dt, engine):
        self.toast_time = max(0, self.toast_time-dt)

    def advance_world(self, dt, menu=True):
        if menu:
            self.toast_time = max(0, self.toast_time-dt)

    def consume(self, events):
        # The application plays audio; particles and face animations are omitted.
        pass

    def label(self, value, x, y, size=30, color=WHITE):
        key = str(value), size, color
        if key not in self.labels:
            if size not in self.fonts:
                self.fonts[size] = pygame.font.Font(None, size)
            self.labels[key] = self.fonts[size].render(str(value), True, color)
            if len(self.labels) > 128:
                self.labels.popitem(last=False)
        self.labels.move_to_end(key)
        image = self.labels[key]
        self.canvas.blit(image, image.get_rect(center=(x, y)))

    def lines(self, value, y, size=30, color=MUTED):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        row = ''
        for word in value.split():
            candidate = (row+' '+word).strip()
            if row and self.fonts[size].size(candidate)[0] > 510:
                self.label(row, 300, y, size, color)
                y += size+6
                row = word
            else:
                row = candidate
        self.label(row, 300, y, size, color)

    def tap(self, name, title, rect, primary=False):
        rect = pygame.Rect(rect)
        self.buttons[name] = rect
        pygame.draw.rect(self.canvas, MINT if primary else PANEL, rect, border_radius=22)
        self.label(title, *rect.center, 32, BG if primary else WHITE)

    def sprite(self, level, x, y, scale=1, angle=0):
        key = level, round(scale, 3), round(math.degrees(angle)/3)*3 % 360
        if key not in self.rotations:
            if level not in self.bases:
                base = self.sprites.character(level)
                shadow = pygame.mask.from_surface(base).to_surface(
                    setcolor=(3,10,18,90),unsetcolor=(0,0,0,0))
                baked = pygame.Surface((base.get_width()+12,base.get_height()+12),pygame.SRCALPHA)
                baked.blit(shadow,(6,10))
                baked.blit(base,(6,6))
                self.bases[level] = baked
            image = pygame.transform.rotozoom(self.bases[level], -key[2], scale)
            self.rotations[key] = image
            self.cache_bytes += image.get_pitch()*image.get_height()
            while self.cache_bytes > 16*1024*1024 and len(self.rotations) > 1:
                _, old = self.rotations.popitem(last=False)
                self.cache_bytes -= old.get_pitch()*old.get_height()
        self.rotations.move_to_end(key)
        image = self.rotations[key]
        self.canvas.blit(image, image.get_rect(center=(round(x), round(y))))

    def render_mobile(self, a):
        self.buttons.clear()
        self.canvas.blit(self.menu_background,(0,0)) if hasattr(self,'menu_background') else self.canvas.fill(BG)
        p, e, b = a.profile, a.engine, self.tap
        if a.page == 'home':
            self.label('CIRCUIT', 300, 185, 70)
            self.label('MERGE', 300, 250, 70, MINT)
            self.sprite(5, 300, 420, 1.3)
            self.lines('Assemble. Fusionne. Passe au niveau suivant.', 565)
            b('adventure', 'Continuer l’aventure', (55, 655, 490, 88), True)
            b('free', 'Mode fun · partie libre', (55, 765, 490, 88))
            b('sound', 'Son activé' if p.sound else 'Son coupé', (160, 930, 280, 66))
        elif a.page == 'map':
            self.label('TON AVENTURE', 300, 65, 44)
            self.label(f'{p.completed} / {len(MISSIONS)} niveaux', 300, 110, 28, MUTED)
            start = a.map_page*5
            nodes = [(220 if i%2 == 0 else 380, 225+i*135) for i in range(5)]
            pygame.draw.lines(self.canvas, (47, 77, 95), False, nodes, 14)
            for offset, (x,y) in enumerate(nodes):
                i = start+offset
                if i >= len(MISSIONS):
                    break
                enabled = p.available(i)
                pygame.draw.circle(self.canvas, MINT if enabled else PANEL, (x,y), 44)
                if enabled:
                    self.buttons[f'mission:{i}'] = pygame.Rect(x-48,y-48,96,96)
                self.label(str(i+1), x, y, 40, BG if enabled else MUTED)
                for star in range(3):
                    self.star(x-20+star*20,y+61,p.stars[i]>star,7)
            if start:
                b('map_prev','Précédents',(35,865,250,68))
            if start+5 < len(MISSIONS):
                b('map_next','Suivants',(315,865,250,68))
            b('home','Accueil',(35,960,180,70))
            b('resume' if p.active else f'mission:{a.next_level()}',
              'Reprendre' if p.active else 'Jouer',(235,960,330,70),True)
        elif a.page in ('briefing','confirm'):
            m = MISSIONS[a.selected]
            self.label(f'NIVEAU {a.selected+1}',300,175,44,MINT)
            self.lines(m.title,270,44,WHITE)
            self.lines(m.goal,400,36,WHITE)
            self.label(f'{m.budget} lâchers',300,510,36,MINT)
            if m.score_goal:
                self.label(f'Score minimum : {m.score_goal}',300,560,30,C.ORANGE)
            self.lines('Glisse pour viser, relâche pour lâcher. Tourne la pièce avec les boutons.',650)
            if a.page == 'confirm':
                self.lines('Remplacer la tentative sauvegardée ?',755,28,C.ORANGE)
            b('confirm' if a.page=='confirm' else 'start','Jouer',(55,840,490,85),True)
            b('map','Retour',(180,955,240,65))
        elif a.page == 'result':
            won = e.outcome == 'won'
            self.sprite(5,300,265,1.3)
            self.label('BRAVO !' if won else 'ENCORE UN ESSAI ?',300,440,46,MINT)
            self.lines(MISSIONS[e.index].title,515,36,WHITE)
            self.label(f'{e.score} points',300,615,36,MUTED)
            if won:
                for i in range(3):
                    self.star(250+i*50,695,p.stars[e.index]>i,18)
            if won and e.index+1 < len(MISSIONS):
                b('next_level','Niveau suivant',(55,795,490,85),True)
            else:
                b('retry','Rejouer' if won else 'Réessayer',(55,795,490,85),True)
            b('map','Parcours',(180,920,240,70))
        elif a.page == 'play':
            self.render_game(a)
        if self.toast_time > 0:
            pygame.draw.rect(self.canvas,PANEL,(20,880,560,80),border_radius=16)
            self.lines(self.toast,905,22)
        return self.canvas

    def render_game(self,a):
        e, b = a.engine, self.tap
        mission = isinstance(e,MissionEngine)
        self.label(f'NIVEAU {e.index+1}' if mission else 'MODE FUN',150,50,36,MINT)
        b('pause','Pause',(440,22,135,64))
        self.lines(e.mission.goal if mission else 'Fusionne et bats ton record !',125,30,WHITE)
        status = f'{e.progress}/{e.mission.target} · {e.remaining} lâchers' if mission else f'Record : {a.best}'
        status += f' · {e.score}/{e.mission.score_goal} pts' if mission and e.mission.score_goal else f' · {e.score} pts'
        self.label(status,300,178,26,MUTED)
        scale,ox,oy = a.arena_transform()
        def point(x,y):
            return round(ox+x*scale),round(oy+y*scale)
        l,t = point(e.left,C.WALL_TOP)
        r,f = point(e.right,e.floor)
        pygame.draw.rect(self.canvas,(20,36,49),(l,t,r-l,f-t),border_radius=16)
        pygame.draw.lines(self.canvas,(100,155,165),False,[(l,t),(l,f),(r,f),(r,t)],4)
        dy = point(0,C.DANGER_Y)[1]
        pygame.draw.line(self.canvas,C.RED if e.danger_ratio else (111,82,88),(l+5,dy),(r-5,dy),2)
        for piece in e.pieces.values():
            x,y = point(*piece.body.position)
            # A tiny visual bounce only; physical positions remain unchanged.
            age = next((fx[4] for fx in self.effects if fx[3]==piece.uid), .45)
            bounce = 5*math.sin(math.pi*age/.25) if age<.25 else 0
            self.sprite(piece.level,x,y-bounce,scale,piece.body.angle)
            if piece.uid in getattr(e,'marked',()):
                pygame.draw.circle(self.canvas,C.ORANGE,(x,y),10,3)
        if a.active and (not mission or e.remaining):
            x,y = point(e.aim_x,C.DROP_Y)
            pygame.draw.line(self.canvas,(55,91,102),(x,y+28),(x,dy),1)
            self.sprite(e.current_level,x,y,scale,e.aim_angle)
        self.label('Glisse pour viser · relâche pour lâcher',300,940,24,MUTED)
        b('rotate_left','Tourner −',(30,980,255,72))
        b('rotate_right','Tourner +',(315,980,255,72))
        if a.mode:
            self.buttons.clear()
            pygame.draw.rect(self.canvas,BG,(30,280,540,600),border_radius=28)
            over = e.state is RoundState.GAME_OVER
            restart = a.mode == 'restart'
            self.label('PARTIE TERMINÉE' if over else ('RECOMMENCER ?' if restart else 'PAUSE'),300,355,42,MINT)
            b('confirm_new' if over or restart else 'close','Rejouer' if over or restart else 'Continuer',(65,460,470,82),True)
            if not over and not restart:
                b('new','Recommencer',(65,570,470,74))
            elif restart:
                b('close','Annuler',(65,570,470,74))
            b('home','Accueil',(65,680,470,74))
            b('sound','Son activé' if a.profile.sound else 'Son coupé',(65,780,470,65))



class PolishedView(MobileView):
    """Decorations never alter physics. At most eight fusion effects."""
    def __init__(self):
        super().__init__()
        self.menu_background = pygame.Surface((W, H))
        for y in range(H):
            t = y/H
            pygame.draw.line(self.menu_background,
                             (13+int(7*t), 24+int(10*t), 38+int(16*t)),
                             (0,y),(W,y))
        for x,y in ((25,150),(550,340),(28,680),(545,890)):
            points = [(x,y),(x+22,y),(x+22,y+65),(x+40,y+83)]
            pygame.draw.lines(self.menu_background,(35,66,80),False,points,2)
            pygame.draw.circle(self.menu_background,(60,111,121),points[-1],5,2)
        self.intro_shade = pygame.Surface((W,H))
        self.intro_shade.fill(BG)
        self.result_age = 0.

    def consume(self, events):
        for event in events:
            if event.kind == 'merge':
                self.effects.append([event.x,event.y,event.level,event.uid,0.])
        self.effects = self.effects[-8:]

    def animate(self, dt, engine):
        super().animate(dt,engine)
        for effect in self.effects:
            effect[4] += dt
        self.effects = [effect for effect in self.effects if effect[4] < .45]

    def tap(self,name,title,rect,primary=False):
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.canvas,(5,14,23),rect.move(0,5),border_radius=22)
        super().tap(name,title,rect,primary)
        pygame.draw.line(self.canvas,(152,249,216) if primary else (52,76,97),
                         (rect.left+23,rect.top+2),(rect.right-23,rect.top+2),2)

    def render_mobile(self,a):
        result = super().render_mobile(a)
        if a.page == 'map':
            zones = ('ALIMENTATION','LOGIQUE','MÉMOIRE','CONTRÔLE')
            self.label(zones[a.map_page],300,155,22,MINT)
            i = a.next_level()
            if i//5 == a.map_page:
                offset = i%5
                x,y = (220 if offset%2==0 else 380),225+offset*135
                pygame.draw.circle(self.canvas,C.ORANGE,(x,y),50,3)
        elif a.page == 'result' and a.engine.outcome == 'won':
            # Cover the static stars, reveal earned stars in sequence.
            pygame.draw.rect(self.canvas,BG,(215,660,170,72),border_radius=15)
            for i in range(3):
                earned = a.profile.stars[a.engine.index]>i
                reveal = self.result_age >= .18+i*.22
                self.star(250+i*50,695,earned and reveal,18)
            if a.engine.index+1<len(MISSIONS):
                self.label('Niveau suivant débloqué !',300,745,26,MINT)
        if a.intro_remaining > 0:
            self.canvas.blit(self.intro_shade,(0,0))
            progress = 1-a.intro_remaining/1.2
            points = [(80,560),(180,560),(220,520),(300,520),(300,460)]
            pygame.draw.lines(self.canvas,(40,70,87),False,points,5)
            segments = len(points)-1
            amount = max(0,min(1,progress/.65))*segments
            for i in range(segments):
                if amount<=i: break
                t = min(1,amount-i)
                end = (points[i][0]+(points[i+1][0]-points[i][0])*t,
                       points[i][1]+(points[i+1][1]-points[i][1])*t)
                pygame.draw.line(self.canvas,MINT,points[i],end,5)
                pygame.draw.circle(self.canvas,WHITE,(round(end[0]),round(end[1])),5)
            self.sprite(5,300,380,1.3)
            if progress>.55:
                self.label('CIRCUIT MERGE',300,660,52,MINT)
            self.label('Toucher pour passer',300,940,24,MUTED)
        return result

    def render_game(self,a):
        super().render_game(a)
        if a.mode: return
        e = a.engine
        # Small preview above the arena, not a second physics projection.
        pygame.draw.rect(self.canvas,PANEL,(312,18,110,72),border_radius=16)
        self.label('ENSUITE',367,32,20,MUTED)
        icon = self.sprites.get(e.next_level,18)
        self.canvas.blit(icon,icon.get_rect(center=(367,63)))
        scale,ox,oy = a.arena_transform()
        previous_clip = self.canvas.get_clip()
        self.canvas.set_clip(pygame.Rect(24,230,552,695))
        for x,y,level,uid,age in self.effects:
            x,y = round(ox+x*scale),round(oy+y*scale)
            t = age/.45
            color = tuple(round(c*(1-t)+b*t) for c,b in zip(MINT,BG))
            pygame.draw.circle(self.canvas,color,(x,y),round(15+35*t),2)
            for i in range(6):
                angle = i*math.tau/6
                radius = 18+42*t
                pos = round(x+math.cos(angle)*radius),round(y+math.sin(angle)*radius)
                pygame.draw.circle(self.canvas,color,pos,max(1,round(3*(1-t))))
        self.canvas.set_clip(previous_clip)

class AndroidApplication(ProjectApplication):
    def __init__(self,**kwargs):
        self.intro_remaining = 0.
        self.mobile_ready = False
        self.suspended = False
        self.finger = self.pointer_button = None
        super().__init__(**kwargs)
        self.view = PolishedView()
        self.page = 'home'
        self.map_page = self.next_level()//5
        self.mobile_ready = True
        self._scaled = None
        self.draw()

    def next_level(self):
        return next((i for i in range(len(MISSIONS)) if self.profile.available(i) and not self.profile.stars[i]),len(MISSIONS)-1)

    def _viewport(self):
        w,h = self.screen.get_size()
        scale = min(w/W,h/H)
        size = round(W*scale),round(H*scale)
        return pygame.Rect((w-size[0])//2,(h-size[1])//2,*size)

    def logical_position(self,pos):
        rect = self._viewport()
        if not rect.collidepoint(pos):
            return -1.,-1.
        return (pos[0]-rect.x)*W/rect.w,(pos[1]-rect.y)*H/rect.h

    def arena_transform(self):
        e = self.engine
        scale = min(520/(e.right-e.left+24),690/(e.floor-140))
        return scale,300-(e.left+e.right)*scale/2,230-140*scale

    def _aim(self,pos):
        x,y = self.logical_position(pos)
        scale,ox,oy = self.arena_transform()
        if 20<=x<=580 and 225<=y<=925:
            self.engine.set_aim((x-ox)/scale)
            return True
        return False

    def _cancel_pointer(self):
        self.finger = self.pointer_button = None
        self.dragging = False

    def action(self,name):
        self.dragging = False
        if name in ('home','hub'):
            self.save(); self.page='home'; self.mode=None
        elif name in ('map','adventure'):
            self.save(); self.page='map'; self.mode=None; self.map_page=self.next_level()//5
        elif name in ('map_prev','map_next'):
            self.map_page=max(0,min((len(MISSIONS)-1)//5,self.map_page+(-1 if name=='map_prev' else 1)))
        elif name=='next_level':
            index=self.engine.index+1
            if self.profile.available(index):
                self.start(index)
        elif name.startswith('rotate_'):
            if self.active:
                self.engine.rotate_aim(C.ROTATION_STEP*(-1 if name=='rotate_left' else 1))
        elif name=='cancel':
            self.page='map'
        else:
            super().action(name)
        self.accumulator=0

    def _back(self):
        self._cancel_pointer()
        if self.page=='play' and self.mode is None:
            self.action('pause')
        elif self.page=='home':
            self.save(); self.running=False
        elif self.page in ('briefing','confirm','result'):
            self.action('map')
        else:
            self.action('home')

    def handle_event(self,event):
        backgrounds=tuple(getattr(pygame,n,-1) for n in ('APP_WILLENTERBACKGROUND','APP_DIDENTERBACKGROUND','WINDOWFOCUSLOST'))
        foregrounds=tuple(getattr(pygame,n,-1) for n in ('APP_DIDENTERFOREGROUND','WINDOWFOCUSGAINED'))
        if event.type in backgrounds:
            self._cancel_pointer(); self.accumulator=0
            if self.active:
                self.action('pause')
            self.suspended=True; self.save(); return
        if event.type in foregrounds:
            self.suspended=False; return
        if event.type==pygame.QUIT:
            self.save(); self.running=False; return
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_AC_BACK):
                self._back()
            return
        if self.suspended:
            return
        touch=event.type in (pygame.FINGERDOWN,pygame.FINGERUP,pygame.FINGERMOTION)
        mouse=event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.MOUSEMOTION)
        if not touch and not mouse:
            return
        if mouse and (getattr(event,'touch',False) or self.finger is not None):
            return
        if mouse and hasattr(event,'button') and event.button!=1:
            return
        down=event.type in (pygame.FINGERDOWN,pygame.MOUSEBUTTONDOWN)
        up=event.type in (pygame.FINGERUP,pygame.MOUSEBUTTONUP)
        if touch:
            if down:
                if self.finger is not None:
                    return
                self.finger=event.finger_id
            elif self.finger!=event.finger_id:
                return
            w,h=self.screen.get_size(); pos=event.x*w,event.y*h
        else:
            pos=event.pos
        logical=self.logical_position(pos)
        if self.intro_remaining > 0:
            if down:
                self.intro_remaining = 0.
                self._cancel_pointer()
            return
        if down:
            self.pointer_button=next((name for name,rect in self.view.buttons.items() if rect.collidepoint(logical)),None)
            if self.pointer_button is None and self.active:
                self.dragging=self._aim(pos)
        elif up:
            name=self.pointer_button
            if name and self.view.buttons.get(name,pygame.Rect(0,0,0,0)).collidepoint(logical):
                self.action(name)
            elif self.dragging and self.active and self._aim(pos):
                self.engine.drop()
            self._cancel_pointer()
        elif self.dragging and self.active:
            self._aim(pos)

    def update(self,elapsed):
        if not self.suspended:
            dt = min(.1,max(0,elapsed))
            self.intro_remaining = max(0,self.intro_remaining-dt)
            before = self.page
            super().update(elapsed)
            if self.page == 'result':
                self.view.result_age = 0. if before != 'result' else self.view.result_age+dt
            else:
                self.view.result_age = 0.

    def draw(self):
        if not getattr(self,'mobile_ready',False) or self.suspended:
            return
        canvas=self.view.render_mobile(self)
        rect=self._viewport()
        if self._scaled is None or self._scaled.get_size()!=rect.size:
            self._scaled=pygame.Surface(rect.size)
        pygame.transform.scale(canvas,rect.size,self._scaled)
        self.screen.fill(BG)
        self.screen.blit(self._scaled,rect)
        pygame.display.flip()

    def run(self,frames=None):
        count=0
        try:
            while self.running and (frames is None or count<frames):
                elapsed=self.clock.tick(30 if self.active else 15)/1000
                for event in pygame.event.get():
                    self.handle_event(event)
                self.update(elapsed); self.draw(); count+=1
        finally:
            self.save(); pygame.quit()


def launch_android():
    from android.storage import app_storage_path
    folder=Path(app_storage_path())
    folder.mkdir(parents=True,exist_ok=True)
    app=AndroidApplication(save_path=folder/'project_q_v3.json')
    app.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    app.fullscreen=True
    app.intro_remaining=1.2
    app.run()
