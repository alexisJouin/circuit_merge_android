"""Géométrie commune au dessin des connecteurs et aux zones de dépose."""
ZONES={
 'case':(304,143,510,620),'board':(352,216,358,380),
 'cpu':(437,280,104,94),'paste':(449,291,80,72),
 'ram':(570,269,94,156),'ssd':(437,418,148,28),
 'cooler':(437,280,104,94),'gpu':(388,493,269,21),
 'psu':(340,641,245,84),'fans':(725,218,66,345),
 'atx':(674,291,26,108),'eps':(398,230,61,21),'pcie':(612,483,52,20),
}
# Dimensions visibles une fois posées (le GPU se dépose sur son port).
PLACED={**ZONES,'cooler':(429,270,124,138),'gpu':(381,492,309,77),
        'cpu':(449,291,80,72),'ram':(570,269,94,156)}
PAGES=(('case','board','cpu','ram','ssd','gpu','psu'),
       ('paste','cooler','fans','atx','eps','pcie'))

def accepts(key,pos):
    """Marge de quelques pixels pour les prises fines, jamais une zone voisine."""
    x,y,w,h=ZONES[key]
    margin=7 if key in ('atx','eps','pcie','ssd','gpu') else 0
    return x-margin<=pos[0]<=x+w+margin and y-margin<=pos[1]<=y+h+margin
