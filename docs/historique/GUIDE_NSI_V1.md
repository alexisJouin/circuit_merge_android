# Guide NSI — comprendre Circuit Merge

Ce jeu est à la fois un programme complet et un terrain d'expérimentation.
L'objectif pédagogique est d'expliquer les choix, d'établir des contrats puis
de modifier un comportement en s'appuyant sur des tests.

## 1. Faire une première lecture utile

Commencer par jouer cinq minutes. Décrire les règles sans lire le code :
quand la fusion se produit-elle ? Quel objet apparaît ensuite ? Que signifie
« dépasser la limite » ? Une collision est-elle forcément une fusion ?

Ouvrir ensuite les fichiers dans cet ordre :

1. `config.py` : quels paramètres permettent de décrire les règles ?
2. `model.py` : quelles informations faut-il conserver pour une pièce ?
3. `engine.py`, méthodes `drop`, `_on_contact`, `_process_merges`,
   `_check_overflow` : où les règles deviennent-elles des algorithmes ?
4. `app.py`, méthode `update` : comment le temps fait-il avancer le jeu ?
5. `view.py` : comment un état devient-il une image ?

Pour la première NSI, partir des fonctions du squelette élèves et des
collections. Pour la terminale, approfondir les objets, les responsabilités,
les événements et les invariants. La simulation des contacts est confiée à
Pymunk : construire un moteur complet de corps rigides n'est pas nécessaire
pour réaliser le projet.

## 2. Séparer règles, affichage et application

| Module | Responsabilité | Exemple de question |
| --- | --- | --- |
| `config` | Paramètres et catalogue | Quel rayon associer au niveau 4 ? |
| `model` | Données et états | Quels champs distinguent deux résistances ? |
| `engine` | Règles et simulation | Quels contacts donnent une fusion ? |
| `app` | Entrées et orchestration | Un clic doit-il viser ou ouvrir un menu ? |
| `view` / `art` | Rendu et décorations | Comment dessiner une carte graphique ? |
| `audio` | Synthèse sonore | Quelle fréquence associer à une fusion ? |
| `storage` | Persistance | Comment retrouver une partie interrompue ? |

Le moteur n'importe jamais Pygame. On peut donc le faire évoluer dans un test
ou une expérience sans créer de fenêtre. La vue lit les pièces et reçoit des
événements ; elle ne décide pas des fusions.

Cette séparation réduit les dépendances : remplacer les dessins ne modifie
pas la gravité ; ajouter un test de score ne nécessite pas de carte son.

## 3. Modéliser les données

`ComponentSpec` est une dataclass **immuable** : elle décrit un type de
composant (nom, rayon, couleur, points, rôle). Le catalogue est un tuple.

`Piece` est une dataclass **mutable** : elle décrit une instance dans la
partie. Elle contient un identifiant unique, un niveau, un corps, une forme,
une date de naissance et son chronomètre de dépassement.

Il faut distinguer trois notions :

- le **niveau** : indice de 0 à 10 dans le catalogue ;
- le **corps** Pymunk : position, vitesse, angle, masse et moment d'inertie ;
- la **forme** Pymunk : cercle utilisé pour calculer les contacts.

Deux résistances ont le même niveau mais des corps, des positions et des
identifiants différents. Le sprite n'est qu'une représentation : les trous
entre les pattes d'un transistor ne sont pas des zones de collision.

Le dictionnaire `pieces` associe un identifiant à une pièce. `_by_shape`
permet de retrouver une pièce depuis une forme reçue dans un contact. Les
deux index doivent rester cohérents : ajouter ou supprimer une pièce implique
de mettre à jour les deux index et l'espace Pymunk.

## 4. Comprendre la boucle de jeu

Une image suit cet ordre : lire les événements clavier / souris ; mesurer le
temps écoulé ; réaliser les pas de simulation nécessaires ; consommer les
événements de jeu ; dessiner ; afficher.

Un écran rapide peut afficher 144 images par seconde et un écran lent 30.
Si les pièces avançaient d'une distance fixe par image, la vitesse dépendrait
du matériel. Il faut exprimer les vitesses en pixels par seconde.

La simulation utilise un **pas fixe de 1/120 seconde**. L'accumulateur garde
le temps réel non encore simulé :

```python
accumulateur += temps_ecoule
while accumulateur >= pas_fixe:
    moteur.step(pas_fixe)
    accumulateur -= pas_fixe
```

À 60 images par seconde, deux pas de physique sont normalement réalisés par
image. À 30 images par seconde, il y en a quatre. La version réelle plafonne
le temps d'une image à 0,1 seconde pour éviter un rattrapage excessif après
un blocage. Sous forte charge, le jeu ralentit volontairement.

La pause empêche d'appeler `step`, puis remet l'accumulateur à zéro. Les
compteurs de grâce et de dépassement n'avancent donc pas pendant un menu.
F2 multiplie le temps à simuler par 0,25 sans changer le pas de calcul.

## 5. Repère et physique

Le repère est celui de l'écran : x augmente vers la droite, y vers le bas.
Un objet en chute a une vitesse verticale positive. Son sommet se trouve à
`y - rayon` ; il dépasse donc la limite si `y - rayon < limite`.

Les grandeurs utilisent des unités de simulation : positions en pixels,
temps en secondes, vitesse en pixels/seconde, gravité en pixels/seconde².
Les masses sont relatives, sans prétendre décrire les masses réelles des
composants électroniques.

Pour une chute sans frottement, la mécanique continue donne :

- `v(t) = v0 + g × t` ;
- `y(t) = y0 + v0 × t + g × t² / 2`.

Un calcul numérique utilise de petits intervalles ; il approche ces formules.
L'expérience `experiences/chute_libre.py` compare plusieurs fréquences.
Elle retire obstacles et frottements pour isoler l'effet du pas de temps.
Pymunk ne réemploie pas forcément la même variante d'Euler qu'un code écrit
par les élèves : l'important est de mesurer et expliquer l'écart.

### Paramètres à expérimenter

| Paramètre | Valeur initiale | Effet à étudier |
| --- | --- | --- |
| `GRAVITY` | 1080 | Durée de chute et vitesse d'impact |
| `ELASTICITY` | 0,38 | Intensité des rebonds |
| `FRICTION` | 0,72 | Glissement et rotations |
| `AIR_DAMPING` | 0,985 | Dissipation de vitesse en une seconde |
| `FIXED_DT` | 1/120 | Précision et coût de la simulation |
| `DROP_INTERVAL` | 0,38 | Rythme de placement |
| `DROP_GRACE` | 1,15 | Tolérance après création |
| `OVERFLOW_DELAY` | 2,0 | Dépassement continu autorisé |

Pymunk multiplie les restitutions des deux formes qui se touchent : deux
objets réglés à 0,38 ont une restitution de contact de 0,1444. Il multiplie
également leurs coefficients de frottement. Ne pas confondre le coefficient
d'un objet avec celui du contact.

La masse est proportionnelle à l'aire : `(rayon / rayon_initial)²`. Le moment
d'inertie est obtenu par `pymunk.moment_for_circle`. Les gros objets repoussent
donc davantage les petits et tournent selon leur inertie.

## 6. Organiser une fusion sûre

Pymunk détecte les contacts. Le callback `_on_contact` compare les niveaux
et ajoute seulement les identifiants d'une paire candidate à un ensemble.
Il ne retire pas les corps pendant le calcul physique.

Une fois `space.step` terminé, `_process_merges` :

1. Trie les paires par identifiant pour un choix déterministe.
2. Vérifie que les deux pièces existent encore et ont le même niveau.
3. Calcule une position et une vitesse moyennes pondérées par les masses.
4. Retire les deux anciennes pièces.
5. Crée le niveau suivant, ou retire les deux objets terminaux.
6. Ajoute le score et un événement d'animation / de son.

La position du nouvel objet est bornée par les parois et le sol. Son rayon
plus grand peut recouvrir un voisin : Pymunk corrigera le chevauchement.
Le jeu ne simule pas une fusion physiquement conservatrice : la nouvelle
masse résulte du nouveau rayon, et les anciennes masses ne sont pas forcément
additionnées. C'est un choix de jouabilité.

### Trois objets qui se touchent

Supposons que les contacts soient `(1,2)`, `(1,3)` et `(2,3)`. Après la fusion
de 1 et 2, ces deux identifiants sont retirés du dictionnaire. Les deux paires
suivantes contiennent une pièce disparue : elles sont ignorées. La pièce 3
reste donc seule, et un nouvel objet reçoit un autre identifiant.

Le callback est `pre_solve` plutôt que seulement `begin` : il est rappelé
tant que le contact existe. Une nouvelle pièce encore protégée par les
0,06 seconde de `MERGE_GRACE` pourra fusionner dès que cette grâce expire.

### Invariants utiles

- Les identifiants des pièces présentes sont uniques.
- Une pièce supprimée ne reste dans aucun index.
- Une fusion normale retire deux pièces et en crée une : l'effectif diminue de 1.
- Deux objets terminaux retirés diminuent l'effectif de 2.
- Une pièce est consommée au plus une fois pendant la résolution d'un pas.
- Le score n'est ajouté qu'après une fusion effectivement réalisée.

## 7. Défaite et chronomètres

Un compteur global de débordement donnerait une règle injuste : une pièce
dépassant une seconde, suivie d'une autre dépassant une seconde, provoquerait
une défaite alors qu'aucune n'a dépassé deux secondes de suite.

Chaque pièce possède donc `overflow_time`. À chaque pas, si elle est assez
ancienne et son sommet dépasse la limite, on ajoute `dt`. Sinon, on remet
son compteur à zéro. La partie se termine si un compteur atteint le délai.

La tolérance commence à la création de la pièce, lors d'un lâcher ou d'une
fusion. Après une fusion, la pièce possède un nouveau compteur. Le jeu prévoit
aussi une fin de partie si une pièce s'échappe du bac, afin de ne pas laisser
un objet hors de l'écran poursuivre une simulation infinie.

## 8. File et hasard reproductible

`current_level` désigne l'objet à lâcher et `next_level` celui annoncé. Après
un lâcher réussi, le prochain devient le courant puis un nouveau prochain
est tiré. Un clic trop rapide ne doit changer ni la file ni le score.

Les poids initiaux sont 32, 27, 20, 14 et 7, dont la somme vaut 100. Les
probabilités correspondent donc à ces pourcentages. Il ne s'agit pas d'une
distribution uniforme.

Une instance `random.Random(seed)` appartient au moteur. Les décorations
utilisent un autre générateur : changer le nombre de particules ne doit pas
changer la suite des objets. Avec `--fresh --seed 42`, comparer des paramètres
en conservant les mêmes tirages. Il faut aussi conserver la même suite
d'actions ; une graine ne reproduit pas les mouvements de la souris.

## 9. Événements et animations

Le moteur émet des `GameEvent` : `drop`, `impact`, `merge`, `goal`, `game_over`.
L'application transmet ces messages à la vue et au son. Un événement de
fusion contient une position, un niveau, des points et une indication de
fusions rapprochées.

Les particules sont de petits points sans corps Pymunk. Elles n'encombrent
pas les collisions. Les sprites sont mis en cache : un composant déjà dessiné
est réutilisé. Pour créer un nouveau thème, modifier `art.py` et le catalogue,
sans modifier la fusion.

Les notes sont des sinusoïdes échantillonnées. L'enveloppe diminue leur volume
au fil du temps. Cela permet d'étudier une fonction mathématique et sa
représentation numérique sans installer de bibliothèque audio supplémentaire.

## 10. Sauvegarder des objets complexes

Un corps Pymunk contient des objets natifs qui ne sont pas directement du
JSON. `snapshot` en extrait des valeurs simples : niveaux, vecteurs, angles,
compteurs et état du générateur aléatoire.

`from_snapshot` crée de nouveaux corps à partir de ces valeurs. JSON transforme
les tuples en listes : il faut reconstruire des tuples pour `Random.setstate`.
Les champs numériques sont vérifiés pour refuser NaN, les niveaux impossibles
et les compteurs déraisonnables.

La sauvegarde est écrite dans un fichier temporaire, puis déplacée avec
`os.replace`. Cette opération évite de remplacer l'ancien fichier avant que
le nouveau soit entièrement écrit. La reprise recalcule les contacts : c'est
une sauvegarde de partie, pas une simulation bit à bit identique.

## 11. Tester des comportements

Les tests fournis ne dessinent pas de captures comparées pixel par pixel.
Ils vérifient les conséquences observables : un contact égal fusionne ; un
contact différent ne fusionne pas ; trois objets ne sont pas consommés deux
fois ; le prochain objet est respecté ; le sol arrête les chutes ; une même
pièce doit dépasser continuellement ; la pause gèle le temps ; la sauvegarde
conserve les prochains tirages.

Commande : `python -m unittest discover -s tests -v`.

Avant d'ajouter une fonctionnalité, écrire un scénario qui distingue le
comportement attendu d'une erreur plausible. Exemple : un bouton placé à
gauche ne doit pas lâcher un composant. Ce test protège la frontière entre
entrées de l'interface et actions dans le bac.

Le test de charge lance plusieurs parties avec des positions pseudoaléatoires
et contrôle les coordonnées finies et l'absence de traversée du sol. Il complète
les tests isolés sans garantir tous les cas possibles de simulation.

## 12. Complexité et pistes de prolongement

Une détection naïve de tous les contacts entre n objets examine
`n × (n - 1) / 2` paires, donc O(n²). Pymunk utilise des structures spatiales
pour limiter les candidats ; son coût réel dépend de la disposition des corps.
Ne pas lui attribuer une complexité constante garantie.

Pour k contacts candidats, le tri des paires coûte O(k log k). Les accès aux
dictionnaires sont en moyenne O(1). La recherche de la pièce sous la souris
parcourt les n objets : O(n). La projection verticale de visée est également
O(n) à chaque image.

Prolongements pertinents : thème personnalisable, autre distribution de
tirages, statistiques de partie en CSV, réglages de difficulté, import de
sprites, chronologie des actions, meilleur guide de visée, puis moteur
simplifié écrit par les élèves.

Un mode duel ou une version Android demande un travail supplémentaire.
Pour un premier projet, privilégier une amélioration mesurable et documentée
du jeu local avant d'ajouter des services ou une nouvelle plateforme.
