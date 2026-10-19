"""Projet Q : missions déterministes, objectifs physiques et économie locale."""
from dataclasses import dataclass, field
from collections import Counter
import json
import math
import os
from pathlib import Path
import time
import uuid
from . import config as C
from .engine import GameEngine
from .model import RoundState

@dataclass(frozen=True)
class Mission:
    title: str
    story: str
    goal: str
    kind: str
    target: int
    level: int = 1
    budget: int = 16
    par: int = 8
    width: int = 480
    floor: int = 790
    sequence: tuple = (0,0,1,1)
    stock: tuple = ()  # niveau, x, y, angle, marque
    score_goal: int = 0

LEGACY_MISSIONS = (
    Mission('Premier courant','Luma attend ses premières lampes. Assemblons trois LED.',
            'Créer 3 LED','create',3,level=1,budget=12,par=6,sequence=(0,)*12),
    Mission('Des établis, enfin','Les premières livraisons arrivent par paires. Fais monter le score.',
            'Marquer 24 points','score',24,budget=18,par=8,sequence=(1,1,1,1,0,0,2,2)*3),
    Mission('Réserve d’énergie','Le stock occupe déjà le fond. Prépare deux condensateurs.',
            'Créer 2 condensateurs','create',2,level=2,budget=16,par=7,
            sequence=(1,1,0,0,1,1)*3,stock=((3,410,710,.15,False),)),
    Mission('Couloir de câbles','La zone se resserre. Oriente les boîtiers avec E.',
            'Réussir 6 fusions','merge',6,budget=20,par=10,width=400,sequence=(0,0,1,1,2,2)*4),
    Mission('Logique de chantier','Une puce logique pour commander l’alimentation.',
            'Créer 1 puce logique','create',1,level=4,budget=14,par=2,
            sequence=(3,3,2,2,1,1)*3,floor=735),
    Mission('Pièces prioritaires','Les deux résistances cerclées doivent rejoindre une fusion.',
            'Fusionner les 2 pièces marquées','marked',2,budget=18,par=2,
            sequence=(0,0,0,0,1,1)*3,stock=((0,430,765,0,True),(0,680,765,0,True))),
    Mission('Test de puissance','Les gros boîtiers prennent de la place. Garde de la marge.',
            'Marquer 60 points','score',60,budget=20,par=10,width=420,
            sequence=(3,3,2,2,3,3,1,1)*3,stock=((0,400,760,0,False),)),
    Mission('Le chef d’orchestre','Une puce est déjà livrée. Assemble le microcontrôleur.',
            'Créer 1 microcontrôleur','create',1,level=5,budget=16,par=1,
            sequence=(4,3,3,4,2,2)*3,stock=((4,556,710,0,False),)),
    Mission('Contrôle qualité','Il faut une pile productive et un score suffisant.',
            '6 fusions ET 45 points','merge',6,score_goal=45,budget=22,par=11,
            width=380,sequence=(2,2,3,3,1,1,0,0)*3),
    Mission('Laboratoire opérationnel','Dernier test : préparer la mémoire du centre de contrôle.',
            'Créer 1 RAM ET 70 points','create',1,level=6,score_goal=70,budget=20,par=4,
            sequence=(4,4,4,4,3,3,2,2)*3),
)
# V3.1 : aucune livraison de puce, microcontrôleur ou RAM.
MISSIONS = (
    Mission('Premier courant','Une série complète de lampes pour éclairer le chantier.',
            'Créer 12 LED','create',12,budget=32,par=26,sequence=(0,)*12),
    Mission('Des établis, enfin','Construis une chaîne de production, à partir des petites pièces.',
            '160 points ET 25 fusions','merge',25,score_goal=160,budget=52,par=35,
            sequence=(0,0,1,0,0,1)),
    Mission('Réserve d’énergie','Le fond est encombré. Fabrique toute une réserve de condensateurs.',
            'Créer 10 condensateurs','create',10,level=2,budget=56,par=32,
            sequence=(0,1,0,0,1,0),stock=((0,395,765,.2,False),(1,710,750,.3,False))),
    Mission('Couloir de câbles','Un atelier étroit et des livraisons décalées : organise tes piles.',
            'Réussir 38 fusions','merge',38,budget=60,par=48,width=400,
            sequence=(0,1,0,1,0,0,1,0)),
    Mission('Logique de chantier','Trois puces de contrôle à fabriquer, aucune livrée toute faite.',
            'Créer 3 puces logiques','create',3,level=4,budget=58,par=42,floor=735,
            sequence=(0,1,0,1,0,0,1,1)),
    Mission('Pièces prioritaires','Recycle les deux condensateurs cerclés puis termine la production.',
            '2 pièces marquées ET 220 points','marked',2,score_goal=220,budget=62,par=57,
            sequence=(0,0,1,0,1,0),stock=((2,430,740,0,True),(2,680,740,0,True))),
    Mission('Test de puissance','Fais fonctionner la chaîne sur la durée malgré le stock initial.',
            '420 points ET 40 fusions','merge',40,score_goal=420,budget=76,par=71,width=420,
            sequence=(0,1,0,1,2,0,1,0),stock=((0,395,760,0,False),(1,710,750,.1,False))),
    Mission('Le chef d’orchestre','Deux microcontrôleurs, entièrement assemblés dans ton atelier.',
            'Créer 2 microcontrôleurs','create',2,level=5,budget=80,par=50,
            sequence=(0,1,0,1,1,0,2,0)),
    Mission('Contrôle qualité','Une production régulière, dans la zone la plus serrée.',
            '55 fusions ET 500 points','merge',55,score_goal=500,budget=88,par=76,width=380,
            sequence=(0,1,0,2,0,1,0,1)),
    Mission('Laboratoire opérationnel','Fabrique les deux mémoires du centre de contrôle.',
            'Créer 2 RAM ET 850 points','create',2,level=6,score_goal=850,budget=110,par=102,
            sequence=(0,1,0,2,1,0,2,1)),
)
# Chapitre 2 : contrôle classique, signaux et acquisition.
CHAPTERS = ('Fondations', 'Contrôle et signaux')
MISSIONS += (
    Mission('Bus de données', 'Relie les postes de contrôle avec une production régulière.',
            '65 fusions ET 650 points', 'merge',65,score_goal=650,budget=108,par=90,
            sequence=(0,1,0,2,1,0,1,2)),
    Mission('Horloge de référence', 'Une horloge commune synchronise les appareils de mesure.',
            'Créer 3 microcontrôleurs', 'create',3,level=5,budget=80,par=58,
            sequence=(0,1,0,2,1,0,1,2),width=440),
    Mission('Signaux propres', 'Recycle les deux composants marqués avant de valider la série.',
            '2 pièces marquées ET 900 points', 'marked',2,score_goal=900,budget=142,par=120,
            sequence=(0,1,0,2,1,0,1,2),
            stock=((2,480,740,0,True),(2,632,740,0,True))),
    Mission('Ligne de commande', 'La ligne est étroite : réserve un passage pour les petites pièces.',
            '80 fusions ET 800 points', 'merge',80,score_goal=800,budget=120,par=97,
            sequence=(0,1,0,2,1,0,1,2),width=400),
    Mission('Mémoire tampon', 'Stocke les instructions avant leur envoi vers les appareils.',
            'Créer 3 RAM', 'create',3,level=6,budget=132,par=106,
            sequence=(0,1,0,2,1,0,1,2)),
    Mission('Acquisition', 'Le stock initial encombre la chaîne de mesure. Maintiens le débit.',
            '95 fusions ET 1100 points', 'merge',95,score_goal=1100,budget=152,par=127,
            sequence=(0,1,0,2,1,0,1,2),
            stock=((1,415,755,.2,False),(2,697,740,-.2,False))),
    Mission('Baie compacte', 'La baie réserve moins de hauteur à ton atelier de production.',
            'Créer 4 microcontrôleurs', 'create',4,level=5,budget=100,par=74,
            sequence=(0,1,0,2,1,0,1,2),floor=735,width=440),
    Mission('Retour de mesure', 'Prépare la lecture des signaux : recyclage et longue production.',
            '2 pièces marquées ET 1300 points', 'marked',2,score_goal=1300,budget=180,par=154,
            sequence=(0,1,0,2,1,0,1,2),
            stock=((1,480,760,0,True),(1,632,760,0,True))),
    Mission('Synchronisation', 'Produis les mémoires des voies de commande dans un atelier resserré.',
            '3 RAM ET 1400 points', 'create',3,level=6,score_goal=1400,budget=200,par=175,
            sequence=(0,1,0,2,1,0,1,2),width=420),
    Mission('Centre de pilotage', 'Valide une longue série avant de relier commande et acquisition.',
            '125 fusions ET 1700 points', 'merge',125,score_goal=1700,budget=218,par=194,
            sequence=(0,1,0,2,1,0,1,2)),
)
BUILDINGS = (
    ('Sol technique',150,2,'Le hangar devient un laboratoire.'),
    ('Énergie sécurisée',230,4,'Alimentation, câbles et éclairage.'),
    ('Postes de contrôle',320,6,'Les consoles surveillent le chantier.'),
    ('Baies de calcul',420,8,'Le contrôle classique prend forme.'),
    ('Portique central',500,10,'Prêt pour la future installation cryogénique.'),
)
BUILDINGS += (
    ('Réseau de contrôle',550,12,'Le bus relie les consoles et les baies.'),
    ('Horloge de référence',620,14,'Une référence commune synchronise les signaux.'),
    ('Générateur de signaux',700,16,'Les impulsions de commande sont préparées.'),
    ('Chaîne de lecture',780,18,'Les signaux de mesure sont acquis et numérisés.'),
    ('Pilotage synchronisé',850,20,'Le contrôle est prêt pour la future cryogénie.'),
)
TOOLS={'remove':('Pince',80,35,2),'swap':('Échange',60,25,3),'extra':('Livraison +3',100,45,5)}

class MissionEngine(GameEngine):
    """Objectifs comptés sur les contacts réels ; 8 secondes après le dernier lâcher."""
    def __init__(self,index,*,ruleset=2):
        self.ruleset=ruleset
        self.index=index; self.mission=m=(MISSIONS if ruleset==2 else LEGACY_MISSIONS)[index]
        self.created=Counter(); self.marked=set(); self.marked_done=0
        self.extra=0; self.swaps=0; self.used=set(); self.outcome=None
        self.attempt_id=uuid.uuid4().hex; self.settle_until=None; self.initializing=True
        super().__init__(index+300,arena=(556-m.width/2,556+m.width/2,m.floor))
        for level,x,y,angle,marked in m.stock:
            p=self.add_piece(level,(x,y),angle=angle)
            if marked: self.marked.add(p.uid)
        for _ in range(360): GameEngine.step(self)
        self.initializing=False; self.created.clear()
        self.score=self.merge_count=self.drops=0
        self.state=RoundState.PLAYING; self.events.clear(); self._sync_queue()

    @property
    def remaining(self): return max(0,self.mission.budget+self.extra-self.drops)
    @property
    def can_drop(self): return self.outcome is None and self.remaining>0 and super().can_drop
    def _sync_queue(self):
        seq=self.mission.sequence
        self.current_level=seq[(self.drops+self.swaps)%len(seq)]
        self.next_level=seq[(self.drops+self.swaps+1)%len(seq)]
        self.set_aim(self.aim_x)
    def drop(self,x=None):
        ok=super().drop(x)
        if ok:
            self._sync_queue()
            if not self.remaining: self.settle_until=self.time+8
        return ok
    def _process_merges(self):
        before=set(self.pieces); start=len(self.events)
        super()._process_merges()
        gone=before-set(self.pieces)
        self.marked_done+=len(gone & self.marked); self.marked-=gone
        if not self.initializing:
            for event in self.events[start:]:
                if event.kind=='merge' and event.uid is not None: self.created[event.level]+=1
    @property
    def progress(self):
        return {'score':self.score,'merge':self.merge_count,'create':self.created[self.mission.level],
                'marked':self.marked_done}[self.mission.kind]
    @property
    def achieved(self): return self.progress>=self.mission.target and self.score>=self.mission.score_goal
    def step(self,dt=C.FIXED_DT):
        if self.outcome: return
        super().step(dt)
        if self.achieved: self.outcome='won'
        elif self.state is RoundState.GAME_OVER: self.outcome='lost'
        elif self.settle_until is not None and self.time>=self.settle_until: self.outcome='lost'
    def bonus(self,kind,uid=None):
        if self.outcome or (kind not in self.used and len(self.used)>=2): return False
        if kind=='remove':
            p=self.pieces.get(uid)
            if p is None or uid in self.marked: return False
            self._remove_piece(p)
        elif kind=='swap':
            if not self.remaining: return False
            old=self.current_level; old_swaps=self.swaps
            for _ in self.mission.sequence:
                self.swaps+=1; self._sync_queue()
                if self.current_level!=old: break
            if self.current_level==old:
                self.swaps=old_swaps; self._sync_queue(); return False
        elif kind=='extra': self.extra+=3; self.settle_until=None
        else: return False
        self.used.add(kind); return True
    def campaign_snapshot(self):
        marks=[i for i,p in enumerate(self.pieces.values()) if p.uid in self.marked]
        return dict(index=self.index,ruleset=self.ruleset,engine=self.snapshot(),created=dict(self.created),marked=marks,
                    marked_done=self.marked_done,extra=self.extra,swaps=self.swaps,used=sorted(self.used),
                    attempt_id=self.attempt_id,settle_until=self.settle_until,outcome=self.outcome)
    @classmethod
    def restore(cls,data):
        engine=cls(checked_int(data['index'],0,len(MISSIONS)-1),ruleset=checked_int(data.get('ruleset',1),1,2)); old=GameEngine.from_snapshot(data['engine'])
        for p in list(engine.pieces.values()): engine._remove_piece(p)
        for key in ('time','score','drops','merge_count','highest_level','completed_circuits',
                    'last_drop','aim_angle','state','combo','_last_merge'):
            setattr(engine,key,getattr(old,key))
        for p in old.pieces.values():
            q=engine.add_piece(p.level,tuple(p.body.position),tuple(p.body.velocity),
                              angle=p.body.angle,born_at=p.born_at)
            q.body.angular_velocity=p.body.angular_velocity; q.overflow_time=p.overflow_time
        pieces=list(engine.pieces)
        engine.marked={pieces[checked_int(i,0,len(pieces)-1)] for i in data['marked']}
        engine.created=Counter({checked_int(int(k),0,10):checked_int(v,0,10000) for k,v in data['created'].items()})
        engine.marked_done=checked_int(data['marked_done'],0,10)
        engine.extra=checked_int(data['extra'],0,30000); engine.swaps=checked_int(data['swaps'],0,100000)
        engine.used=set(data['used'])
        if not engine.used<=TOOLS.keys() or len(engine.used)>2: raise ValueError('Bonus invalides')
        engine.attempt_id=str(data['attempt_id'])
        if not 1<=len(engine.attempt_id)<=64: raise ValueError('Tentative invalide')
        engine.settle_until=data['settle_until']
        if engine.settle_until is not None and (not math.isfinite(engine.settle_until) or engine.settle_until<0):
            raise ValueError('Délai invalide')
        engine.outcome=data['outcome']
        if engine.outcome not in (None,'won','lost'): raise ValueError('Résultat invalide')
        engine._sync_queue(); engine.set_aim(old.aim_x); engine.events.clear()
        return engine

def checked_int(value,lo,hi):
    if type(value) is not int or not lo<=value<=hi: raise ValueError('Entier invalide')
    return value

@dataclass
class Profile:
    credits: int=0
    stars: list=field(default_factory=lambda:[0]*len(MISSIONS))
    scores: list=field(default_factory=lambda:[0]*len(MISSIONS))
    buildings: int=0
    unlocked: list=field(default_factory=list)
    inventory: dict=field(default_factory=lambda:{k:0 for k in TOOLS})
    receipts: list=field(default_factory=list)
    active: dict|None=None
    free_round: dict|None=None
    best: int=0
    sound: bool=True
    pc_build: dict|None=None
    def __post_init__(self):
        # Migration additive : aucun crédit, record ni montage n'est effacé.
        for name in ('stars','scores'):
            values=getattr(self,name)
            if isinstance(values,list) and len(values)==10:
                setattr(self,name,values+[0]*(len(MISSIONS)-10))
    @property
    def completed(self): return sum(s>0 for s in self.stars)
    def available(self,index): return 0<=index<len(MISSIONS) and (index==0 or self.stars[index-1]>0)
    def award(self,engine):
        if engine.outcome!='won' or engine.attempt_id in self.receipts: return 0
        i=engine.index; par=engine.mission.par
        stars=3 if engine.drops<=par else (2 if engine.drops<=par+3 else 1)
        reward=(170+15*i+min(50,engine.score//5)) if not self.stars[i] else (25+min(15,engine.score//10))
        self.credits+=reward; self.stars[i]=max(self.stars[i],stars)
        self.scores[i]=max(self.scores[i],engine.score); self.receipts.append(engine.attempt_id)
        self.active=None
        return reward
    def build(self):
        if self.buildings>=len(BUILDINGS): return False
        _,price,need,_=BUILDINGS[self.buildings]
        if self.credits<price or self.completed<need: return False
        self.credits-=price; self.buildings+=1; return True
    def buy(self,kind):
        if kind not in TOOLS: return False
        _,unlock,charge,need=TOOLS[kind]; price=charge if kind in self.unlocked else unlock
        if self.completed<need or self.credits<price: return False
        self.credits-=price
        if kind not in self.unlocked: self.unlocked.append(kind)
        self.inventory[kind]+=1; return True
    def use(self,engine,kind,uid=None):
        if self.inventory.get(kind,0)<=0 or not engine.bonus(kind,uid): return False
        self.inventory[kind]-=1; return True

class CampaignStore:
    def __init__(self,path=None):
        base=Path(os.environ['LOCALAPPDATA']) if os.environ.get('LOCALAPPDATA') else Path.home()
        self.path=Path(path) if path else base/'CircuitMerge'/'project_q_v3.json'; self.error=''
    def load(self):
        try:
            data=json.loads(self.path.read_text(encoding='utf8'))
            if data.pop('version')!=3: raise ValueError('Version inconnue')
            p=Profile(**data)
            checked_int(p.credits,0,10**12); checked_int(p.buildings,0,len(BUILDINGS)); checked_int(p.best,0,10**12)
            if len(p.stars)!=len(MISSIONS) or len(p.scores)!=len(MISSIONS): raise ValueError('Campagne invalide')
            for n in p.stars: checked_int(n,0,3)
            for n in p.scores: checked_int(n,0,10**12)
            if any(p.stars[i] and not p.stars[i-1] for i in range(1,len(MISSIONS))): raise ValueError('Progression discontinue')
            if set(p.inventory)!=set(TOOLS) or not set(p.unlocked)<=TOOLS.keys(): raise ValueError('Inventaire invalide')
            for n in p.inventory.values(): checked_int(n,0,10**6)
            if type(p.sound) is not bool: raise ValueError('Son invalide')
            if not isinstance(p.receipts,list) or any(not isinstance(s,str) for s in p.receipts): raise ValueError('Transactions invalides')
            if p.active and not p.available(MissionEngine.restore(p.active).index): raise ValueError('Mission verrouillée')
            if p.pc_build is not None:
                from .pc_builder import PCBuild
                PCBuild.restore(p.pc_build)
            if p.free_round: GameEngine.from_snapshot(p.free_round)
            return p
        except FileNotFoundError: return Profile()
        except (OSError,ValueError,TypeError,KeyError,IndexError,OverflowError,AttributeError):
            self.error='Sauvegarde invalide : original conservé, nouveau profil.'
            if self.path.exists():
                try: self.path.rename(self.path.with_name(f'project_q_corrompu_{time.time_ns()}.json'))
                except OSError: self.path=self.path.with_name(f'project_q_recupere_{time.time_ns()}.json')
            return Profile()
    def save(self,p):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temp=self.path.with_suffix('.tmp')
            with temp.open('w',encoding='utf8') as f:
                json.dump(dict(version=3,**vars(p)),f,ensure_ascii=False,allow_nan=False)
                f.flush(); os.fsync(f.fileno())
            os.replace(temp,self.path); self.error=''; return True
        except (OSError,ValueError,TypeError):
            self.error='Sauvegarde impossible : garde le jeu ouvert et vérifie le dossier.'; return False
