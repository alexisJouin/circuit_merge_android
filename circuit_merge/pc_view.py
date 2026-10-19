"""Montage : stock illustré à glisser et carte mère lisible sans surlignage."""
import pygame
from . import config as C
from .pc_builder import PARTS
from .pc_layout import ZONES, PLACED, PAGES, accepts
from .pc_art import fan, board, part_image, socket

def render_pc(v,b,selected,mouse,guide=False,confirm=False,drag=None,page=0):
    s=v.canvas; done=b.installed; on=b.booted
    v.buttons.clear(); v.pc_cards={}; s.blit(v.background,(0,0))
    v.text('ATELIER ARCHITECTURE',(27,25),36,C.TEAL)
    v.text('Prends une pièce, glisse-la, puis relâche sur son emplacement.',(28,68),22,C.MUTED)
    v.button('hub','Chantier',(925,27,167,43),mouse)
    v.panel((24,110,247,683))
    v.text('STOCK DE COMPOSANTS',(39,128),20,C.TEAL)
    v.button('pc:page:0','Pièces',(38,159,104,32),mouse,page==0)
    v.button('pc:page:1','Finition',(150,159,107,32),mouse,page==1)
    if not hasattr(v,'pc_icons'):
        v.pc_icons={k:part_image(k,(78,59)) for k in PARTS}
    for i,key in enumerate(PAGES[page]):
        r=pygame.Rect(38,204+i*77,219,70)
        v.pc_cards[key]=r
        v.buttons['pc:select:'+key]=r
        color=(40,66,77) if key==selected else (25,42,54)
        if r.collidepoint(mouse): color=(40,65,79)
        pygame.draw.rect(s,color,r,border_radius=8)
        pygame.draw.rect(s,C.TEAL if key==selected else C.LINE,r,2 if key==selected else 1,border_radius=8)
        icon=v.pc_icons[key]
        s.blit(icon,icon.get_rect(center=(r.x+44,r.centery)))
        v.wrapped(PARTS[key].short,r.x+88,r.y+10,125,20,C.TEXT,21)
        v.text('Installé' if key in done else 'Glisser',(r.x+89,r.y+49),16,C.TEAL if key in done else C.MUTED)
        if key in done:pygame.draw.circle(s,C.TEAL,(r.right-9,r.y+9),3)
    v.text('Échap : annuler le déplacement',(41,764),18,C.MUTED)
    # Châssis, rails, entretoises et passages de câbles restent visibles.
    pygame.draw.polygon(s,(25,34,48),[(304,143),(782,143),(813,168),(813,760),(304,760)])
    pygame.draw.rect(s,(54,70,88) if 'case' in done else (30,40,54),(304,143,478,617),border_radius=13)
    pygame.draw.rect(s,(12,20,32),(319,182,446,555),border_radius=9)
    for x in (330,701):pygame.draw.rect(s,(45,61,79),(x,756,52,14),border_radius=4)
    pygame.draw.line(s,C.TEAL if on else (67,92,114),(327,166),(728,166),3)
    pygame.draw.circle(s,C.TEAL if on else C.ORANGE,(748,164),6,2)
    v.text('NOVA / OPEN LAB',(339,150),20,C.TEXT)
    pygame.draw.rect(s,(24,34,48),(326,614,431,117),border_radius=6)
    for y in (248,373,490):pygame.draw.rect(s,(5,12,21),(711,y,9,44),border_radius=4)
    for y in (258,386,515):
        pygame.draw.circle(s,(43,59,70),(751,y),32,1)
        for dx,dy in ((-25,-25),(25,-25),(25,25),(-25,25)):
            pygame.draw.circle(s,(92,112,127),(751+dx,y+dy),2)
    if 'case' not in done:
        v.wrapped('Glisse le boîtier sur cette zone de travail.',388,352,295,32,C.MUTED,36)
    elif 'board' not in done:
        pygame.draw.rect(s,(28,42,52),ZONES['board'],1,border_radius=5)
        for x,y in ((361,225),(698,225),(361,583),(698,583),(361,409),(698,409)):
            pygame.draw.circle(s,(180,152,94),(x,y),5)
            pygame.draw.circle(s,(30,34,31),(x,y),2)
        v.text('PLATEAU / ENTRETOISES',(384,395),20,C.MUTED)
    if 'board' in done:board(s,ZONES['board'],v.fonts)
    def draw_part(key):
        rect=pygame.Rect(PLACED[key]);im=part_image(key,rect.size,v.world_time,on)
        s.blit(im,im.get_rect(center=rect.center))
    if 'cpu' in done:draw_part('cpu')
    if 'paste' in done:pygame.draw.circle(s,(217,222,228),(489,327),7)
    if 'ram' in done:
        for x in (594,642):
            pygame.draw.rect(s,(33,88,71),(x,271,17,150),border_radius=2)
            pygame.draw.rect(s,(110,122,142),(x+1,274,14,142),border_radius=3)
            pygame.draw.line(s,(171,129,237),(x+3,279),(x+12,279),3)
            for y in range(294,403,24):pygame.draw.rect(s,(13,24,33),(x+3,y,10,17),border_radius=2)
    if 'ssd' in done:draw_part('ssd')
    if 'cooler' in done:
        draw_part('cooler')
        pygame.draw.lines(s,(225,190,100),False,[(549,281),(560,281),(560,242),(529,242)],2)
    if 'gpu' in done:draw_part('gpu')
    if 'psu' in done:draw_part('psu')
    else:
        v.text('PSU / BLOC ALIMENTATION',(360,680),20,C.MUTED)
        for y in range(647,724,8):pygame.draw.line(s,(42,55,66),(350,y),(372,y),2)
    if 'fans' in done:
        for y in (258,386,515):fan(s,751,y,32,v.world_time,on)
        fan(s,331,262,20,v.world_time,on)
        if on:
            for y in (258,386,515):
                x=713-int(v.world_time*34)%40
                pygame.draw.line(s,C.TEAL,(x+14,y),(x,y),2)
                pygame.draw.lines(s,C.TEAL,False,[(x+5,y-4),(x,y),(x+5,y+4)],2)
    cables={
      'atx':([(570,698),(720,698),(720,344),(687,344)],(86,218,199)),
      'eps':([(558,650),(330,650),(330,201),(428,201),(428,240)],(238,184,88)),
      'pcie':([(578,714),(704,714),(704,472),(638,472),(638,493)],(175,133,241)),
    }
    for key,(pts,col) in cables.items():
        if key in done:
            pygame.draw.lines(s,(8,13,22),False,pts,10)
            pygame.draw.lines(s,col,False,pts,4)
            r=pygame.Rect(ZONES[key])
            pygame.draw.rect(s,(40,45,50),r,border_radius=2)
            pygame.draw.rect(s,col,r,2,border_radius=2)
    # La sérigraphie est physique et permanente. Le guide ajoute seulement un halo.
    if selected and guide:
        rect=pygame.Rect(ZONES[selected])
        pygame.draw.rect(s,C.TEAL if selected in done else C.ORANGE,rect.inflate(8,8),2,border_radius=6)
        v.text(PARTS[selected].destination,(550,793),22,C.TEAL,True)
    elif 'board' in done:
        v.text('Repère les formes, contacts, clips et inscriptions.',(550,793),20,C.MUTED,True)
    v.panel((839,110,257,683),C.TEAL)
    v.text('COMPRENDRE',(856,130),22,C.TEAL)
    if selected:
        p=PARTS[selected]
        v.wrapped(p.title,856,172,221,28,C.TEXT,30)
        v.wrapped(p.role,856,248,221,20,C.MUTED,23)
        v.text('QUESTION POUR LA CLASSE',(856,524),16,C.ORANGE)
        v.wrapped(p.question,856,552,221,20,C.TEXT,26)
        v.button('pc:remove','Retirer cette pièce',(855,685,225,38),mouse)
    else:
        v.wrapped('Un PC complet : calcul, mémoire, stockage, énergie et refroidissement.',856,182,220,28,C.TEXT,32)
        v.wrapped('Maintiens une pièce du stock, déplace-la et relâche sur son connecteur. Les inscriptions du circuit restent visibles sans guide.',856,366,220,22,C.MUTED,27)
    v.text(f'{len(done)} / {len(PARTS)} étapes',(855,749),26,C.TEAL)
    v.button('pc:guide','Guide : '+('ON' if guide else 'OFF'),(25,816,179,42),mouse)
    v.button('pc:reset','Recommencer',(218,816,190,42),mouse)
    v.button('pc:boot','Démarrer le PC',(427,816,278,42),mouse,True)
    v.text('POST OK' if on else 'PC hors tension',(858,827),26,C.TEAL if on else C.MUTED)
    if on:
        v.text('Matériel prêt · Système à installer sur le SSD',(550,116),20,C.TEAL,True)
    if confirm:
        shade=pygame.Surface((1120,900),pygame.SRCALPHA);shade.fill((2,9,17,225));s.blit(shade,(0,0))
        v.buttons.clear();v.panel((260,260,600,330),C.ORANGE)
        v.text('Recommencer le montage ?',(560,303),36,C.TEXT,True)
        v.wrapped('Seul le montage PC sera vidé. Ta campagne et tes crédits sont conservés.',300,373,520,26,C.MUTED,30)
        v.button('pc:cancel','Continuer',(300,503,233,46),mouse)
        v.button('pc:confirm','Vider le boîtier',(551,503,269,46),mouse,True)
    if drag:
        key=drag['key']
        # La pièce reste attachée au pointeur jusqu'au relâchement.
        carried=part_image(key,(156,130))
        carried.set_alpha(220)
        rect=carried.get_rect(center=(round(mouse[0]),round(mouse[1])))
        shadow=pygame.Surface(carried.get_size(),pygame.SRCALPHA)
        shadow.fill((0,0,0,75));s.blit(shadow,rect.move(5,6));s.blit(carried,rect)
        pygame.draw.circle(s,(251,233,190),(round(mouse[0]),round(mouse[1])),4,1)
        if guide and accepts(key,mouse):
            color=C.TEAL if set(PARTS[key].needs)<=done else C.ORANGE
            pygame.draw.rect(s,color,pygame.Rect(ZONES[key]).inflate(8,8),3,border_radius=4)
    v.toast_layer()
    return s
