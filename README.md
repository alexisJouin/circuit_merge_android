# Circuit Merge V3.3 — Projet Q + Montage PC

Construis le laboratoire qui accueillera ton ordinateur quantique !
Cette version livre **deux chapitres, 20 missions et 10 constructions**.
Le chapitre 2 « Contrôle et signaux » transforme le laboratoire en centre
de pilotage. La cryogénie et les qubits viendront dans les chapitres suivants.

![Le centre de pilotage](docs/chapitre2_v33.png)

## Nouveautés V3.3

- Dix nouvelles missions (11 à 20), accessibles après la mission 10.
- Deux onglets pour naviguer entre les chapitres depuis le chantier.
- Petites livraisons uniquement : résistances, LED et condensateurs.
- Objectifs de longue production, pièces marquées, bacs étroits ou moins profonds.
- Cinq constructions : réseau de contrôle, horloge de référence, générateur
  de signaux, chaîne de lecture et pilotage synchronisé.
- Décor animé : impulsions, onde de commande et acquisition.
- Progression, crédits, bonus, montage PC et mission suspendue conservés.

Les solutions de test du chapitre 2 demandent **56 à 192 lâchers** sans
bonus. Cela prouve l'existence de parcours réalisables, pas un minimum
théorique ni une durée imposée. La difficulté ressentie reste à éprouver
en classe. Voir [le guide du chapitre 2](docs/CHAPITRE_2.md).

## Nouveautés V3.2

- Vrai glisser-déposer : maintenir une pièce du stock, la déplacer puis
  relâcher sur le connecteur. Un clic simple ouvre seulement sa fiche.
- Stock illustré en deux onglets, **Pièces** et **Finition**, avec des
  silhouettes distinctes pour CPU, RAM, GPU, SSD, ventirad et câbles.
- Carte mère agrandie et détaillée : socket et levier CPU, contacts,
  quatre logements DIMM avec clips, M.2 et vis, port PCIe x16 avec loquet,
  connecteurs ATX 24 et CPU/EPS, pile, dissipateurs et ports arrière.
- Guide désactivé par défaut : les inscriptions du circuit restent visibles.
- Mauvais emplacement ou prérequis manquant : la pièce reste dans le stock
  et une explication apparaît. Échap ou clic droit annule le déplacement.
- Campagne, crédits et montage précédemment sauvegardé sont conservés.

![Carte mère sans guide](docs/carte_mere_v32.png)

## Équilibrage conservé de la V3.1

- Dix missions rééquilibrées : de 24 à 100 lâchers dans les solutions de test,
  au lieu de 1 à 11 pour plusieurs anciennes missions. Ce sont des essais,
  pas des minimums garantis ni une durée imposée.
- Aucune puce, aucun microcontrôleur et aucune RAM livrés tout faits.
  Les six premières missions livrent seulement résistances et LED ; les
  suivantes ajoutent quelques condensateurs.
- Objectifs de production en série, budgets et seuils d'étoiles revus.
- **Mode libre Montage PC**, accessible dès le départ, sans crédits ni chrono.

## Montage PC — introduction à l'architecture matérielle

Depuis le chantier, clique **Mode libre : Montage PC**.
Maintiens le clic gauche sur une vignette du stock, déplace la pièce dans
le boîtier, puis relâche au-dessus de son emplacement. Le petit repère au
centre de la pièce portée indique le point de dépose. Pour la carte graphique,
vise le port PCI Express x16 ; pour les câbles, vise leur connecteur.
Un clic sans déplacement consulte la fiche et ne pose rien.

Les onglets **Pièces** et **Finition** donnent accès à tout le stock.
Le guide est OFF par défaut ; active-le si tu souhaites un surlignage.
Sans guide, utilise les formes, clips, contacts et inscriptions sur le PCB.
La RAM est un kit de deux barrettes qui se fixe ici dans A2 et B2.
Le déplacement fonctionne aussi au toucher. Échap ou clic droit annule ;
sortir de la fenêtre ou la redimensionner ne provoque aucune installation.
La colonne de droite présente le rôle de chaque élément et une question
pour la classe. Cliquer une pièce déjà installée permet de relire sa fiche.

Le montage comprend le boîtier, la carte mère, le CPU, la pâte thermique,
deux barrettes de RAM, le SSD NVMe, le ventirad, la carte graphique,
l'alimentation, les ventilateurs et les câbles ATX, CPU/EPS et GPU/PCIe.
Les connexions CPU_FAN et SYS_FAN sont automatiques dans ce modèle.
Le SSD NVMe ne demande pas de câble SATA.

**Démarrer le PC** vérifie le montage. Si des éléments manquent, le message
les indique ; complète le montage et réessaie. Après réussite, les ventilateurs
s'animent et l'air circule. Le POST validé signifie ici « matériel prêt » :
le système d'exploitation reste à installer sur le SSD, hors de ce mode.

Tu peux retirer les pièces pour expérimenter ; les dépendances doivent être
retirées avant leur support. **Recommencer** vide seulement le montage après
confirmation, jamais la campagne. L'état du PC est sauvegardé à chaque
modification, indépendamment de la partie de fusion suspendue.

![Montage du PC](docs/pc_complet_v32.png)

Cette configuration est supposée compatible et représente un PC avec GPU
dédié. Ce n'est pas un simulateur de compatibilité entre références réelles.
Les zones et trajets de câbles sont schématiques. Sur de vrais PC, le GPU
dédié, les câbles et le nombre de ventilateurs varient selon la configuration.
Écran, clavier, souris et système d'exploitation sont hors du montage interne.
Voir `docs/INTRO_ARCHITECTURE.md` pour une proposition de séance de 15 minutes.

## Mettre à jour depuis la V3, V3.1 ou V3.2

Extraire ce ZIP dans un nouveau dossier et utiliser ses lanceurs.
Les crédits, constructions, records et bonus sont conservés automatiquement.
Une tentative V3 suspendue conserve ses anciennes règles jusqu'à sa fin ;
recommencer ou lancer une autre mission applique l'équilibrage V3.1.
Les anciens records et étoiles restent conservés. La sauvegarde passe
automatiquement de 10 à 20 emplacements de mission. La V3.2 ne sait pas
relire ce format étendu : utiliser la V3.3 après migration, ou restaurer
une copie du JSON faite avant la mise à jour pour revenir en arrière.
Les anciens records et étoiles restent conservés. Fermer le jeu précédent
avant de lancer cette version ; garder une copie du JSON permet un retour
à l'ancienne version si nécessaire.

## Installation Windows

1. Extraire entièrement le ZIP dans un nouveau dossier `Circuit_Merge_V3_3`.
2. Avec Python 3.10 à 3.14 installé, lancer `Installer_Windows.bat`.
3. Lancer `Lancer_Windows.bat`.

Internet est nécessaire pour l'installation ; ensuite le jeu fonctionne
hors ligne. Les dépendances restent `pygame-ce==2.5.8` et `pymunk==7.3.0`.
Garder la V2 dans son dossier permet de conserver les deux versions.

Installation manuelle depuis le dossier extrait :

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Sous Linux/macOS : `python3 -m venv .venv`, puis
`.venv/bin/python -m pip install -r requirements.txt` et
`.venv/bin/python main.py`.

## Jouer

Choisis une mission sur le chantier et lis son objectif. La livraison reste
identique à chaque essai : trouve les bons placements et orientations.
Les niveaux varient le stock initial, la largeur ou la hauteur du bac,
les pièces marquées et les objectifs de fabrication, de score ou de fusions.

| Action | Commande |
|---|---|
| Viser | Souris ou flèches gauche/droite |
| Lâcher | Relâcher le clic gauche dans le bac, ou Espace |
| Tourner | E, flèches haut/bas ou molette |
| Pause | P ou Échap |
| Suspendre la mission | Bouton « Suspendre / chantier » |
| Contours physiques | F1 |
| Ralenti | F2 |
| Aide | H ou F3 |
| Son | M |

Après le dernier lâcher, les fusions disposent de huit secondes de simulation.
Le ralenti et la pause préservent ce délai. Une seule étoile suffit pour
ouvrir la mission suivante. Les étoiles récompensent le nombre de lâchers.
Il n'y a ni vies ni attente imposée.

## Crédits et constructions

La première victoire paie une prime croissante, augmentée par le score.
Rejouer rapporte aussi de 25 à 40 crédits par victoire et permet d'améliorer
ses étoiles. Les premières victoires de chaque chapitre financent ses cinq constructions,
si les crédits leur sont réservés. Acheter des bonus peut demander des replays.

| Construction | Coût | Missions réussies |
|---|---:|---:|
| Sol technique | 150 | 2 |
| Énergie sécurisée | 230 | 4 |
| Postes de contrôle | 320 | 6 |
| Baies de calcul | 420 | 8 |
| Portique central | 500 | 10 |
| Réseau de contrôle | 550 | 12 |
| Horloge de référence | 620 | 14 |
| Générateur de signaux | 700 | 16 |
| Chaîne de lecture | 780 | 18 |
| Pilotage synchronisé | 850 | 20 |

Les constructions s'achètent dans cet ordre et transforment le décor.
Elles ne changent pas les règles des missions.

| Bonus | Effet | Déblocage avec 1 charge | Charge suivante | Après |
|---|---|---:|---:|---:|
| Pince | Retirer une pièce non marquée | 80 | 35 | 2 missions |
| Échange | Prochaine valeur différente de la livraison | 60 | 25 | 3 missions |
| Livraison +3 | Ajouter trois lâchers | 100 | 45 | 5 missions |

Au maximum deux familles de bonus par tentative. Une activation réussie
consomme une charge ; une action refusée ne consomme rien. Les charges
utilisées restent consommées après un échec ou un redémarrage de mission.
Toutes les missions sont gagnables sans bonus. Les crédits sont une monnaie
de jeu, sans achat en argent réel.

## Sauvegarde

La progression, les charges, une tentative suspendue une partie libre et le montage PC
sont conservés dans `%LOCALAPPDATA%/CircuitMerge/project_q_v3.json` sous
Windows, ou `~/CircuitMerge/project_q_v3.json` sans LOCALAPPDATA.
Sauvegarde à l'achat, à la suspension, au résultat, à la fermeture et toutes
les dix secondes pendant le jeu. Pour une copie de sécurité, ferme le jeu
et copie ce JSON. Évite deux fenêtres sur le même profil.

La sauvegarde V2 n'est ni importée ni remplacée. Reprendre ouvre une pause ;
appuie sur P pour continuer. Lancer une autre mission demande de confirmer
le remplacement de la tentative suspendue.

## Atelier libre et code NSI

L'atelier libre reste disponible depuis le chantier. Les onze personnages,
leurs clignements et réactions ainsi que les collisions en polygones sont
conservés. La physique suit des silhouettes stylisées en 2D.

- `circuit_merge/campaign.py` : missions, objectifs, économie et sauvegarde.
- `circuit_merge/project_app.py` : navigation et actions du joueur.
- `circuit_merge/world_view.py` : chantier et interface.
- `engine.py`, `geometry.py`, `faces.py` : physique et personnages.
- `docs/GUIDE_V3.md` : conception et pistes pédagogiques.
- `docs/GUIDE_NSI.md`, `atelier_nsi/`, `experiences/` : supports précédents.

`python main.py --classic` lance directement l'atelier historique V2.
`--seed` et `--fresh` concernent cet atelier historique ; la campagne utilise
ses propres livraisons. `--save-file chemin.json` sélectionne un autre profil
pour le mode lancé. `--demo` montre la démonstration V2.

## Vérification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py --smoke-test 120 --mute
```

Les captures de `docs` illustrent le départ, une mission et un laboratoire
construit. Elles ne préremplissent pas ta progression. Le rapport de validation
précise les tests et l'environnement utilisés.
