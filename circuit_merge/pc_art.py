"""Composants dessinés : mêmes silhouettes dans le stock et au déplacement."""
import math
import pygame
from .pc_layout import ZONES

def fan(s,x,y,r,t=0,on=False):
    pygame.draw.circle(s,(8,14,23),(x,y),r)
    pygame.draw.circle(s,(91,224,205) if on else (101,128,155),(x,y),r,3)
    for n in range(7):
        a=n*math.tau/7+(t*3 if on else .2)
        pts=[(x+math.cos(a)*r*.2,y+math.sin(a)*r*.2),
             (x+math.cos(a+.1)*r*.86,y+math.sin(a+.1)*r*.86),
             (x+math.cos(a+.64)*r*.77,y+math.sin(a+.64)*r*.77),
             (x+math.cos(a+.5)*r*.3,y+math.sin(a+.5)*r*.3)]
        pygame.draw.polygon(s,(51,73,96),pts)
    pygame.draw.circle(s,(116,143,164),(x,y),round(r*.21))

def socket(s,rect,cols,rows,color=(24,26,30)):
    x,y,w,h=rect
    pygame.draw.rect(s,(160,167,170),(x-2,y-2,w+4,h+4),border_radius=2)
    pygame.draw.rect(s,color,rect,border_radius=2)
    for col in range(cols):
        for row in range(rows):
            cw=w/cols;ch=h/rows
            box=pygame.Rect(x+col*cw+2,y+row*ch+2,max(2,cw-4),max(2,ch-4))
            pygame.draw.rect(s,(6,10,14),box)
            pygame.draw.rect(s,(140,125,80),box,1)

def board(s,rect,fonts=None):
    """PCB détaillé, sérigraphie et connecteurs toujours visibles sans guide."""
    # Dessiné à taille native : la miniature réutilise exactement ce PCB.
    surf=pygame.Surface((358,380),pygame.SRCALPHA)
    def text(label,xy,size=16,color=(195,213,205)):
        f=fonts[size] if fonts else pygame.font.Font(None,size)
        surf.blit(f.render(label,True,color),xy)
    pygame.draw.rect(surf,(18,57,58),(0,0,358,380),border_radius=6)
    pygame.draw.rect(surf,(61,115,108),(0,0,358,380),2,border_radius=6)
    for k in range(15):
        pygame.draw.lines(surf,(31,83,79),False,[(48,42+k*19),(70+k*3,42+k*19),(95+k*3,67+k*19),(325,67+k*19)],1)
    for x,y in ((9,9),(346,9),(9,367),(346,367),(9,193),(346,193)):
        pygame.draw.circle(surf,(183,174,131),(x,y),5)
        pygame.draw.circle(surf,(10,29,31),(x,y),2)
    # Connectique arrière, dissipateurs VRM, selfs et condensateurs.
    for y,h in ((43,32),(79,39),(123,45),(174,30)):
        pygame.draw.rect(surf,(128,148,160),(0,y,25,h),border_radius=2)
        pygame.draw.rect(surf,(24,37,50),(2,y+6,16,h-13),border_radius=2)
    pygame.draw.rect(surf,(52,66,77),(31,57,35,128),border_radius=3)
    for x in range(36,64,5):pygame.draw.line(surf,(99,117,131),(x,64),(x,178),2)
    for y in (64,91,118,145):
        pygame.draw.rect(surf,(107,116,114),(69,y,12,17),border_radius=2)
        pygame.draw.circle(surf,(187,189,162),(76,y+23),4)
    # Socket avec cadre de rétention, contacts, levier et repère d'orientation.
    pygame.draw.rect(surf,(131,145,150),(85,64,104,94),border_radius=4)
    pygame.draw.rect(surf,(36,42,44),(93,72,88,78),border_radius=2)
    for x in range(99,177,5):
        for y in range(78,145,5):pygame.draw.circle(surf,(144,127,86),(x,y),1)
    pygame.draw.rect(surf,(213,218,215),(89,68,96,86),2,border_radius=2)
    pygame.draw.lines(surf,(213,218,215),False,[(190,66),(194,66),(194,158),(185,164)],2)
    pygame.draw.polygon(surf,(240,192,92),[(94,74),(101,74),(94,81)])
    text('CPU SOCKET',(88,169),18)
    text('CPU_FAN',(157,34),16)
    socket(surf,(163,21,26,9),4,1)
    # Quatre DIMM, clips et détrompeur. A2/B2 sont les deux positions du kit.
    for i,x in enumerate((218,242,266,290)):
        pygame.draw.rect(surf,(9,18,23),(x,53,16,156),border_radius=2)
        pygame.draw.rect(surf,(126,147,141) if i in (1,3) else (64,85,83),(x,53,16,156),1)
        pygame.draw.line(surf,(178,156,103),(x+7,61),(x+7,199),2)
        pygame.draw.rect(surf,(139,149,143),(x,121,16,5))
        for y in (49,207):pygame.draw.rect(surf,(151,163,151),(x-1,y,18,7),border_radius=2)
        text(('A1','A2','B1','B2')[i],(x-1,218),16)
    text('DDR / DIMM',(218,28),18)
    # M.2 : prise à gauche, détrompeur, vis de fixation à droite.
    socket(surf,(85,202,18,28),1,5)
    pygame.draw.rect(surf,(92,127,117),(109,202,122,28),1)
    for x in (168,196,225):
        pygame.draw.circle(surf,(192,180,137),(x,216),4)
        pygame.draw.circle(surf,(29,52,49),(x,216),2)
    text('M.2 / NVMe',(88,238),18)
    # Long port x16 avec séparation des contacts et loquet de verrouillage.
    pygame.draw.rect(surf,(174,179,177),(36,277,269,21),border_radius=2)
    pygame.draw.rect(surf,(16,27,28),(40,282,251,11))
    for x in range(43,288,4):pygame.draw.line(surf,(193,167,103),(x,283),(x,289),1)
    pygame.draw.rect(surf,(154,165,161),(71,278,6,19))
    pygame.draw.rect(surf,(195,207,194),(298,273,11,26),border_radius=2)
    text('PCI EXPRESS x16',(44,303),18)
    pygame.draw.rect(surf,(24,31,36),(36,334,61,12),border_radius=2)
    text('PCIe x1',(40,352),16)
    # ATX 24 contacts, EPS 8 contacts : silhouettes et inscriptions distinctes.
    socket(surf,(322,75,26,108),2,12)
    text('ATX 24',(302,190),16)
    socket(surf,(46,14,61,21),4,2)
    text('CPU / EPS',(37,38),16)
    pygame.draw.rect(surf,(68,80,85),(252,325,66,31),border_radius=3)
    for x in range(257,316,6):pygame.draw.line(surf,(116,135,141),(x,329),(x,350))
    pygame.draw.circle(surf,(173,190,191),(211,339),18)
    pygame.draw.circle(surf,(107,128,131),(211,339),14,1)
    text('+',(207,331),18)
    text('SYS_FAN',(111,354),16);socket(surf,(115,343,25,8),4,1)
    for x in (324,339):pygame.draw.rect(surf,(47,55,59),(x,328,12,28),border_radius=2)
    text('SATA',(320,361),16)
    s.blit(pygame.transform.smoothscale(surf,pygame.Rect(rect).size),pygame.Rect(rect))

def part_image(key,size=(130,90),t=0,on=False):
    """Icône/objet porté : pas de simple étiquette, chaque forme est distincte."""
    dims={'cpu':(100,90),'ram':(110,158),'ssd':(160,37),'gpu':(309,77),
          'psu':(245,84),'cooler':(124,138),'fans':(90,220),'board':(358,380),
          'case':(180,220),'paste':(130,60),'atx':(130,94),'eps':(130,94),'pcie':(130,94)}
    w,h=dims[key]; s=pygame.Surface((w,h),pygame.SRCALPHA)
    def txt(label,xy,sz=20,col=(218,232,237)):
        s.blit(pygame.font.Font(None,sz).render(label,True,col),xy)
    if key=='board':board(s,(0,0,w,h))
    elif key=='cpu':
        pygame.draw.rect(s,(35,81,72),(3,3,94,84),border_radius=4)
        pygame.draw.rect(s,(179,194,201),(10,8,80,74),border_radius=4)
        pygame.draw.rect(s,(217,224,226),(17,16,66,58),border_radius=3)
        txt('CPU',(34,36),24,(39,56,67))
        pygame.draw.polygon(s,(237,190,86),[(7,7),(17,7),(7,17)])
        for x in range(23,80,8):pygame.draw.rect(s,(167,144,91),(x,1,4,3))
    elif key=='ram':
        for x in (15,64):
            pygame.draw.rect(s,(30,91,71),(x,3,30,151),border_radius=2)
            pygame.draw.rect(s,(118,129,150),(x,4,23,147),border_radius=3)
            pygame.draw.line(s,(170,125,236),(x+3,10),(x+20,10),3)
            for y in range(25,137,26):pygame.draw.rect(s,(14,23,34),(x+5,y,15,19),border_radius=2)
            for y in range(14,148,6):pygame.draw.rect(s,(208,174,99),(x+25,y,5,3))
            pygame.draw.rect(s,(0,0,0,0),(x+24,79,7,6))
    elif key=='ssd':
        pygame.draw.rect(s,(28,70,66),(2,3,155,30),border_radius=3)
        for y in range(7,31,4):pygame.draw.line(s,(219,185,106),(1,y),(12,y),2)
        pygame.draw.rect(s,(15,23,34),(22,7,31,22),border_radius=2)
        pygame.draw.rect(s,(208,219,217),(60,6,77,24),border_radius=2)
        txt('NVMe',(72,9),20,(36,48,56))
        pygame.draw.circle(s,(193,166,100),(149,18),4)
    elif key=='gpu':
        pygame.draw.rect(s,(31,42,58),(0,2,w,70),border_radius=6)
        pygame.draw.rect(s,(100,121,143),(0,2,w,70),2,border_radius=6)
        fan(s,53,39,29,t,on);fan(s,128,39,29,t,on)
        txt('GPU',(217,25),26);pygame.draw.line(s,(176,121,240),(190,57),(291,57),3)
        for x in range(20,180,5):pygame.draw.rect(s,(212,180,111),(x,72,3,5))
        pygame.draw.rect(s,(157,168,175),(0,0,7,77))
        socket(s,(231,1,52,13),4,2)
    elif key=='psu':
        pygame.draw.rect(s,(49,62,78),(1,1,w-2,h-2),border_radius=5)
        fan(s,49,42,33);txt('PSU',(110,19),30);txt('AC / DC',(110,51),20,(110,219,197))
        pygame.draw.rect(s,(14,23,32),(213,23,23,33),border_radius=2)
        for y in range(10,78,7):pygame.draw.line(s,(113,134,148),(91,y),(99,y))
    elif key=='cooler':
        pygame.draw.rect(s,(124,141,152),(1,1,w-2,h-2),border_radius=5)
        for y in range(7,133,6):pygame.draw.line(s,(48,68,81),(4,y),(120,y),2)
        fan(s,62,67,51,t,on)
        for x in (33,88):pygame.draw.rect(s,(176,125,75),(x,126,7,12),border_radius=3)
    elif key=='fans':
        for y in (36,110,184):
            pygame.draw.rect(s,(33,46,60),(9,y-35,72,70),border_radius=5)
            fan(s,45,y,31,t,on)
    elif key=='case':
        pygame.draw.rect(s,(58,77,94),(5,3,161,207),border_radius=7)
        pygame.draw.rect(s,(13,25,37),(15,27,141,172),border_radius=3)
        for y in (63,108,153):fan(s,139,y,16)
        pygame.draw.rect(s,(47,63,81),(22,164,97,28),border_radius=3)
        pygame.draw.line(s,(99,223,208),(22,17),(143,17),3)
        for x in (18,135):pygame.draw.rect(s,(80,96,107),(x,208,20,9),border_radius=3)
    elif key=='paste':
        pygame.draw.line(s,(182,195,201),(20,31),(111,31),12)
        pygame.draw.rect(s,(218,224,219),(33,20,58,23),border_radius=3)
        pygame.draw.rect(s,(68,148,156),(52,21,25,21))
        pygame.draw.line(s,(216,225,225),(7,18),(7,44),5)
        pygame.draw.line(s,(127,152,165),(7,31),(33,31),5)
        pygame.draw.polygon(s,(202,213,213),[(110,25),(127,31),(110,37)])
    else:
        col={'atx':(87,213,193),'eps':(237,187,92),'pcie':(177,133,238)}[key]
        for i in range(5):pygame.draw.lines(s,col,False,[(7,85-i*4),(32+i*3,66-i*3),(32+i*3,20),(66,20+i*3)],3)
        if key=='atx': socket(s,(54,20,74,24),12,2)
        else: socket(s,(66,12,42,42),4,2)
        pygame.draw.rect(s,col,(76,6,20,6),border_radius=2)
        txt({'atx':'ATX 24','eps':'CPU / EPS','pcie':'GPU / PCIe'}[key],(48,65),18)
    scale=min(size[0]/w,size[1]/h)
    return pygame.transform.smoothscale(s,(max(1,round(w*scale)),max(1,round(h*scale))))
