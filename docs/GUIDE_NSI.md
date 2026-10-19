# Circuit Merge V2 — guide NSI

## Lire le programme

Commencer par jouer avec F1 (contours), F2 (ralenti), E ou la molette (rotation).
Observer une RAM couchée puis debout : même niveau, encombrement différent.
Lire ensuite config.py, geometry.py, model.py, engine.py, faces.py et view.py.
Le moteur ne dépend pas de Pygame ; le dessin lit ses données.

## Un corps et plusieurs formes

Une Piece contient un uid unique, un niveau, un corps rigide et un tuple de
polygones convexes. Les formes partagent le même corps et restent solidaires.
Le catalogue geometry_for décrit les boîtiers, pattes, cartes et connecteurs.
Il fournit aussi leurs matériaux graphiques : art.py dessine les mêmes sommets.
Les ventilateurs, pistes, vis et visages ne créent pas de collision.

Le champ size est une échelle, pas un rayon de collision. Un contour concave
est décomposé en plusieurs polygones : les espaces entre pattes restent vides.
Les pattes sont épaissies et certains contacts regroupés pour la jouabilité.
Il s'agit d'un modèle 2D stylisé, sans déformation ni rupture des broches.

## Centre de masse et moment d'inertie

area_and_centroid applique la formule du lacet aux sommets ordonnés.
Chaque partie reçoit une masse proportionnelle à son aire et à une densité de
jeu. Le centre global est la moyenne des centres pondérée par ces masses.
Les sommets sont recentrés autour de ce centre ; le corps tourne autour de lui.
Le moment total additionne les moments des parties autour de cette origine.
Ces masses sont des unités de jeu, pas des mesures en grammes.

Pour tourner un point local d'un angle a :

```python
x2 = x * cos(a) - y * sin(a)
y2 = x * sin(a) + y * cos(a)
```

Les angles physiques sont en radians, les commandes de rotation en degrés.
L'axe y va vers le bas. Piece.bounds contient les extrema des formes tournées.
Attention aux noms de Pymunk : BB.bottom est le minimum de y, donc le haut à
l'écran ; BB.top est le maximum de y, donc le bas à l'écran.

## Temps et stabilité

La physique utilise FIXED_DT = 1/240 seconde. À 60 images/s, environ quatre
pas sont calculés par image. L'accumulateur conserve le temps restant ; une
image longue est plafonnée à 0,1 s. La pause suspend les pas. F2 multiplie le
temps de simulation et des visages par 0,25, sans changer FIXED_DT.
Les vitesses sont plafonnées, les coins chanfreinés et les parois épaisses.
La simulation numérique tolère une petite pénétration ; elle n'est pas exacte.

## Contacts et fusions

pieces associe uid à Piece ; _by_shape associe chaque polygone à sa Piece.
Un contact propose une paire triée d'identifiants dans un ensemble. Plusieurs
broches en contact ne créent donc pas plusieurs fusions pour la même paire.
Les suppressions attendent la fin de space.step, car Pymunk verrouille son
espace pendant les callbacks. Retirer une pièce retire toutes ses formes.
Une pièce déjà consommée est ignorée dans les paires suivantes.

La position et la vitesse résultantes utilisent les masses. L'angle utilise
une moyenne circulaire : +179° et -179° donnent environ 180°, pas zéro.
La nouvelle silhouette est replacée à l'intérieur des parois et au-dessus du
sol. Les voisins sont séparés par le solveur. La fusion reste une règle ludique
qui ne garantit pas une conservation physique de l'énergie.

## Visée et débordement

La rotation avant lâcher modifie les bornes horizontales autorisées.
La projection verticale applique le théorème des axes séparateurs (SAT) :
les projections des deux polygones doivent se recouvrir sur chaque normale
d'arête. On cherche le premier déplacement vertical satisfaisant toutes ces
contraintes. Une boîte horizontale écarte d'abord les voisins éloignés.
Le fantôme ne prédit ni rebond, ni déplacement futur, ni fusion.

La défaite dépend du bord réel le plus haut, pattes comprises, pendant deux
secondes continues. Chaque pièce possède son propre compteur. Une grâce de
1,15 s accompagne chaque création ; deux dépassements brefs de pièces
différentes ne s'additionnent pas. L'inspecteur utilise point_query, ce qui
permet de sélectionner le vide entre deux pattes comme du vide.

## Personnalités et expressions

Personality appartient à la vue, pas à la physique. Un générateur indépendant
par uid choisit les clignements et les grimaces occasionnelles. Il ne change
jamais les prochains composants tirés par le moteur.

Priorités : joie après fusion, réaction au choc, inquiétude en débordement,
vertige lors d'une rotation, surprise pendant une chute, puis repos. Les
clins d'œil spontanés n'interrompent pas une réaction prioritaire.
Un choc est estimé par l'impulsion divisée par la masse ; un délai par pièce
évite de répéter une grimace à chaque broche. Les yeux suivent la souris dans
le repère local. Boîtier et visage tournent ensuite ensemble.
Le rendu ne fait pas avancer l'horloge ; animate le fait seulement en jeu.
Les pauses figent donc les visages, même si l'écran continue d'être redessiné.

## Sauvegarde

Le format V2 conserve positions, angles, vitesses, orientation de visée et
état du générateur. Les contacts sont recalculés et les visages redémarrent.
Le fichier save_v2.json est distinct de save.json. Au premier lancement, une
V1 valide peut être importée en lecture seule : les pièces sont replacées et
reçoivent une grâce neuve. Leur disposition peut changer. Une sauvegarde n'est
pas une répétition bit à bit de la simulation.

## Activités

- Première : compléter silhouettes_a_completer.py (rotation, extrema, conditions).
- Première : ajouter une émotion, en justifiant sa priorité.
- Terminale : expliquer les deux index et l'ensemble de paires de fusion.
- Terminale : vérifier aire et barycentre sur un rectangle décentré.
- Expérience : lancer occupation.py et comparer une RAM à 0°, 45° et 90°.
- Test : choisir un point entre les pattes du transistor ; aucune pièce ne doit
  être sélectionnée. Puis choisir un point sur une patte.
- Test : trois pièces identiques ne doivent pas consommer deux fois la même.

Les tests sont dans tests/. Les TODO ne concernent que les exercices élèves.
Le sujet initial conserve une introduction avec des cercles, avant la V2.
Le guide V1 archivé complète les explications générales ; ses références aux
cercles, au pas de 120 Hz et à l'ancien format sont remplacées par ce guide.
