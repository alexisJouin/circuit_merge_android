# Circuit Merge V2 — les composants prennent vie

Un jeu Python de chute et de fusion inspiré de Fruit Merge / Suika,
avec onze composants électroniques, des visages animés et une physique
qui suit leur silhouette. Code et supports pédagogiques en français.

![Circuit Merge V2](apercu_v2.png)

## Nouveautés de la V2

- **Des personnages** : yeux, pupilles qui suivent la souris, bouche et joues.
  Chacun cligne à son rythme. Surprise en chute, vertige en rotation, grimace
  après un choc, inquiétude près du débordement et sourire après une fusion.
  Ils font aussi occasionnellement un clin d'œil et une petite grimace.
- **Des silhouettes physiques** : résistance horizontale, LED bombée, boîtiers,
  broches, RAM allongée, cartes et trois baies de calcul. Un corps rigide porte
  plusieurs polygones convexes : les espaces entre les pattes restent libres.
- **Une rotation avant le lâcher**, par pas de 15°. Une RAM horizontale ne prend
  pas la même place qu'une RAM verticale ; les composants peuvent basculer,
  glisser, s'appuyer sur leurs broches et accrocher leurs voisins.
- **Une visée adaptée** : fantôme de la vraie silhouette et projection verticale
  sur les polygones. Les limites de visée et de débordement suivent l'orientation.
- **Une physique à 240 Hz** et un calcul du centre de masse / de l'inertie par
  partie. Les coins sont chanfreinés et les pattes suffisamment épaisses pour
  rester lisibles et jouables. Ce sont des silhouettes stylisées en 2D.
- **Les dépendances qui fonctionnent sont conservées** : `pygame-ce==2.5.8` et
  `pymunk==7.3.0`, installées uniquement à partir de paquets précompilés.

![Les onze personnages](personnages_v2.png)

## Installer sous Windows

1. Extraire **entièrement** le ZIP dans un nouveau dossier, par exemple
   `Circuit_Merge_V2`. Garder la V1 à côté permet de comparer les deux physiques.
2. Utiliser Python **3.10 à 3.14** ; Python **3.12** est conseillé. Les tests de
   cette livraison ont été exécutés sous Linux avec Python 3.12.
3. Double-cliquer sur **Installer_Windows.bat**, puis sur **Lancer_Windows.bat**.
   Une connexion est nécessaire pour installer les dépendances ; ensuite le jeu
   fonctionne hors ligne. Le code importe `pygame`, fourni ici par **pygame-ce**.

L'installateur retire l'ancienne distribution `pygame` dans l'environnement
local du projet, installe les versions épinglées et vérifie `pygame.IS_CE`.
Il évite ainsi la compilation qui pouvait produire l'erreur
`setuptools._distutils.msvccompiler`. Ne pas installer `pygame` et `pygame-ce`
simultanément : ils partagent le nom de module `pygame`.

Depuis PowerShell dans le dossier extrait, installation manuelle :

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Si `py` manque, utiliser `python` ou le chemin de l'interpréteur. Pour choisir
explicitement Python 3.12 : `py -3.12 -m venv .venv`, avant de créer ce dossier.
Dans Thonny / PyCharm, sélectionner `.venv\Scripts\python.exe` comme interpréteur.

**Pour mettre à jour ton dossier existant qui fonctionne déjà**, copier les
fichiers de la V2 dans ce dossier en conservant son `.venv`. Les versions des
dépendances sont identiques. Le dossier `circuit_merge` contient le nouveau
code ; vérifier qu'il a bien été remplacé, puis lancer `Lancer_Windows.bat`.

## Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Puis utiliser `sh lancer.sh`. Si `venv` est absent sous Linux, installer le
paquet `python3-venv` du système. La livraison est une application Python
pour ordinateur ; aucun APK Android n'est inclus.

## Commandes

| Action | Commande |
| --- | --- |
| Viser | Souris, gauche/droite, Q/D ou A/D |
| Tourner avant de lâcher | E, flèche haute ou molette ; pas de 15° |
| Tourner dans l'autre sens | Flèche basse ou molette inverse |
| Lâcher | Clic puis relâcher dans le bac, ou Espace |
| Pause / reprise | P ou Échap |
| Recommencer | R ou bouton « Nouvelle partie » |
| Son | M |
| Aide | ?, H ou F3 |
| Mode NSI | F1 |
| Ralenti ×0,25 | F2 |
| Figer l'inspecteur | Clic droit en mode NSI |
| Plein écran | F11 |

F1 montre les **polygones physiques**, le centre de masse et les vecteurs
vitesse. L'inspecteur affiche le nombre de polygones, la masse et la vitesse.
F2 ralentit aussi les expressions. Pause et menus figent physique et visages.
Le toucher SDL est géré sur un écran tactile d'ordinateur ; tourner se fait
au clavier ou à la molette.

## Règles

Deux composants du même niveau se touchant deviennent le suivant. Le contact
peut venir d'une patte ou du boîtier. La paire ne fusionne qu'une seule fois,
même si plusieurs de ses polygones se touchent. Les contacts entre niveaux
différents produisent des mouvements physiques.

Seuls les cinq petits niveaux apparaissent au lâcher, avec les poids 32, 27,
20, 14 et 7. La file annonce toujours le prochain composant. Une pression
refusée par le délai de 0,38 s ne modifie pas cette file.

Le score vient des fusions : LED 3, condensateur 6, transistor 10, etc.
L'indicateur de chaîne n'est pas un multiplicateur. Le joueur vise le
supercalculateur. Deux supercalculateurs se retirent, libèrent le bac et
rapportent 132 points ; la partie peut continuer.

Le débordement utilise **le sommet réel de la silhouette tournée**, pattes
comprises. Une même pièce doit dépasser la ligne pendant **2 secondes
continues**, après **1,15 seconde de grâce** suivant sa création. Son retour
sous la ligne remet son compteur à zéro.

Le fantôme prévoit le premier contact lors d'une descente verticale à
orientation constante, avec les voisins dans leur position actuelle. Il ne
prédit pas les rebonds, les rotations ultérieures ni les fusions.

La progression est ludique : deux résistances ne fabriquent pas une LED.
Les pattes sont rigides et les composants ne sont ni déformables ni simulés
en 3D. Le dessin stylise la silhouette ; les détails internes et le visage
sont décoratifs. Les paramètres n'ont pas été extraits du jeu Android.

## Sauvegardes V1 / V2

Record, son, file de lâcher, orientation choisie et partie sont enregistrés
toutes les 10 s, à la fermeture, à la pause et en fin de partie.

- Windows : `%LOCALAPPDATA%\CircuitMerge\save_v2.json`.
- Linux / macOS : `~/CircuitMerge/save_v2.json`.
- Un autre fichier : `python main.py --save-file sauvegardes/alexis.json`.
- Nouveau montage en gardant le record : `python main.py --fresh`.

Si la V2 n'a pas encore de sauvegarde, elle lit automatiquement l'ancien
`save.json` de la V1. Le record et la partie sont repris ; les disques sont
convertis en silhouettes et une nouvelle grâce laisse la pile se réarranger.
**Le fichier V1 reste intact.** La reprise démarre en pause.

Les contacts physiques sont recalculés et les clignements recommencent : la
sauvegarde conserve la partie et les futurs tirages, pas une répétition bit
à bit. Une sauvegarde V2 corrompue est conservée sous un nom distinct quand
le disque le permet. Une V1 corrompue est simplement laissée en place.

## Pour le cours de NSI

- **`docs/GUIDE_NSI.md`** : couches du programme, pas fixe, formes composées,
  centre de masse, fusions, expressions, visée et sauvegarde.
- **`docs/SUJET_PROJET_NSI.md`** : sujet distribuable, huit séances et barème.
- **`docs/NOTES_ENSEIGNANT.md`** : pistes de correction et différenciation.
- **`atelier_nsi/regles_a_completer.py`** : fonctions simples du prototype
  circulaire, pour commencer sans dépendance.
- **`atelier_nsi/silhouettes_a_completer.py`** : exercices V2 sans bibliothèque
  graphique : rotation, boîte englobante, visée et expression.
- **`experiences/chute_libre.py`** : comparer simulation et formule continue.
- **`experiences/occupation.py`** : dimensions à plusieurs angles.
- **`docs/historique/`** : ancien manuel PDF et guide V1, conservés comme références.
- **`docs/VALIDATION.md`** : tests exécutés et portée des vérifications.

Le code complet est la référence fonctionnelle. Les TODO sont uniquement dans
les squelettes élèves. Pour une recherche autonome, distribuer le sujet et
les exercices, puis fournir les modules au fil des séances. Les notes
enseignant peuvent être retirées de la copie destinée aux élèves.

## Expériences et vérifications

```bash
python main.py --fresh --seed 42
python main.py --demo
python experiences/chute_libre.py
python experiences/occupation.py
python -m unittest discover -s tests -v
python main.py --smoke-test 120 --mute
python main.py --demo --screenshot capture.png
```

`--demo` utilise une pile illustrant plusieurs composants et le vrai moteur
physique ; elle ne modifie pas les sauvegardes. Les captures et tests sans
écran n'écrivent pas non plus de sauvegarde.

## Organisation du code

| Fichier | Responsabilité |
| --- | --- |
| `main.py` | Options et lancement |
| `config.py` | Catalogue et paramètres |
| `geometry.py` | Silhouettes, centre de masse, transformations et projection |
| `model.py` | Pièces, état de partie et événements |
| `engine.py` | Corps physiques, règles et fusions |
| `faces.py` | Clignements, priorités des expressions et dessin des visages |
| `art.py` | Silhouettes illustrées et cache graphique |
| `view.py` | Interface, visages et effets |
| `app.py` | Entrées, temps fixe et orchestration |
| `audio.py` | Sons générés localement |
| `storage.py` | Sauvegarde JSON et import V1 |

Les modules se trouvent dans `circuit_merge/`. Le moteur n'importe pas
Pygame. La physique n'utilise **aucun cercle de collision pour les pièces**.
Les cercles encore dessinés servent aux yeux, ventilateurs et effets visuels.

## Références et licence

- [Pymunk : corps et formes](https://www.pymunk.org/en/latest/pymunk.html).
- [pygame-ce : documentation officielle](https://pyga.me/docs/).
- [pygame-ce 2.5.8](https://pypi.org/project/pygame-ce/2.5.8/) et
  [Pymunk 7.3.0](https://pypi.org/project/pymunk/7.3.0/).
- [Fruit Merge: Match Game, référence de mécanique](https://play.google.com/store/apps/details?id=com.melon.drop.fruit.merge.master).

Code, dessins et documentation : licence MIT, voir `LICENSE`.
Les bibliothèques gardent leurs propres licences. Aucune image, police ou
ressource audio n'est téléchargée pendant le jeu ; aucun serveur n'est utilisé.
