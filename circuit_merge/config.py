"""Paramètres du jeu et catalogue des composants.

Point d'entrée conseillé pour les élèves : modifier une constante, prévoir
son effet, puis vérifier cette prédiction en jouant. Les coordonnées sont
exprimées en pixels logiques ; le redimensionnement ne modifie pas la physique.
"""

from dataclasses import dataclass

# Repère commun à Pygame et Pymunk : x vers la droite, y vers le bas.
WIDTH, HEIGHT = 1120, 900
LEFT, RIGHT, FLOOR = 316.0, 796.0, 790.0
WALL_TOP, WALL_THICKNESS = 224.0, 6.0
DROP_Y, DANGER_Y = 184.0, 272.0

# Les petites pattes nécessitent un pas plus court : quatre pas par image à 60 Hz.
FIXED_DT = 1.0 / 240.0
RENDER_FPS = 60
GRAVITY = 1080.0             # pixels / seconde²
AIR_DAMPING = 0.985         # proportion de vitesse conservée après une seconde
FRICTION = 0.72             # frottement des objets
ELASTICITY = 0.28           # restitution d'un objet (valeurs multipliées au contact)
WALL_ELASTICITY = 0.45
MAX_SPEED = 800.0           # limite contre la traversée de parois à grande vitesse
ROTATION_STEP = 15          # degrés par pression de E / flèche haute / molette
DROP_INTERVAL = 0.38        # temps minimal entre deux lâchers
DROP_GRACE = 1.15           # tolérance après création / fusion
OVERFLOW_DELAY = 2.0        # durée continue au-dessus de la limite avant défaite
MERGE_GRACE = 0.06          # laisse au moteur un pas pour résoudre un nouveau contact
COMBO_WINDOW = 1.1          # indicateur visuel uniquement, pas de multiplicateur

# Seuls les cinq plus petits objets peuvent être tirés au sort.
DROP_WEIGHTS = (32, 27, 20, 14, 7)

# Palette : fond de circuit imprimé et accents lisibles.
BG = (11, 20, 30)
PANEL = (19, 32, 44)
PANEL_LIGHT = (25, 43, 56)
LINE = (43, 67, 82)
TEXT = (232, 243, 244)
MUTED = (151, 177, 187)
TEAL = (84, 231, 192)
ORANGE = (255, 187, 99)
RED = (255, 112, 123)


@dataclass(frozen=True)
class ComponentSpec:
    """Description immuable d'un niveau ; aucun objet physique ici.

    ``size`` est une unité de conception : ce n'est PAS un rayon de collision.
    Les dimensions et polygones sont définis dans ``geometry.py``. ``points`` est le
    nombre de points gagné en CREANT ce niveau. L'ordre est une progression
    ludique, pas un procédé réel d'assemblage électronique.
    """

    name: str
    short: str
    size: int
    color: tuple[int, int, int]
    points: int
    role: str


COMPONENTS = (
    ComponentSpec("Résistance", "R", 17, (250, 195, 117), 1,
                  "Limite l'intensité du courant dans un circuit."),
    ComponentSpec("LED", "LED", 24, (250, 132, 151), 3,
                  "Diode qui émet de la lumière lorsqu'elle est alimentée."),
    ComponentSpec("Condensateur", "CAP", 31, (108, 203, 251), 6,
                  "Stocke temporairement de l'énergie électrique."),
    ComponentSpec("Transistor", "TR", 39, (168, 142, 247), 10,
                  "Peut commander un courant : interrupteur ou amplificateur."),
    ComponentSpec("Puce logique", "IC", 48, (97, 220, 180), 15,
                  "Réalise des opérations logiques grâce à ses transistors."),
    ComponentSpec("Microcontrôleur", "MCU", 59, (255, 174, 106), 21,
                  "Réunit processeur, mémoire et entrées-sorties sur une puce."),
    ComponentSpec("Mémoire RAM", "RAM", 71, (116, 194, 156), 28,
                  "Mémoire de travail rapide ; son contenu est volatil."),
    ComponentSpec("Processeur", "CPU", 84, (118, 187, 248), 36,
                  "Exécute les instructions des programmes."),
    ComponentSpec("Carte graphique", "GPU", 98, (217, 146, 237), 45,
                  "Effectue de nombreux calculs en parallèle, notamment graphiques."),
    ComponentSpec("Carte mère", "CM", 114, (96, 223, 206), 55,
                  "Relie les composants de l'ordinateur et leurs interfaces."),
    ComponentSpec("Supercalculateur", "HPC", 132, (251, 200, 97), 66,
                  "Associe de nombreux nœuds de calcul pour traiter de grands problèmes."),
)

# Les vrais noms restent visibles ; ces surnoms servent aux personnages.
NICKNAMES = ("Rési", "Luma", "Cappy", "Tris", "Logi", "Micro", "Ramona",
             "Corey", "Pixie", "Maya", "Atlas")
