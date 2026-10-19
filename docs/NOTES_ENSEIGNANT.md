# Notes enseignant — Circuit Merge

## Scénarios pédagogiques

**Première NSI** : distribuer le sujet, le catalogue et le squelette de règles.
Fournir la création des corps Pymunk pour concentrer le travail sur fonctions,
tableaux / dictionnaires, booléens, événements, fichiers et tests. Commencer
avec quatre niveaux et des formes simples.

**Terminale NSI** : utiliser `Piece` et `GameEngine` pour les objets, les
invariants et la modularité. Étudier le traitement différé des fusions, la
complexité des candidats, la reproductibilité et la sérialisation.

**Atelier court** : donner le jeu complet, activer F1/F2, formuler une hypothèse
sur un paramètre et comparer des mesures. L'expérience de chute libre est
utile pour discuter une approximation numérique et son coût.

Les notions abordées sont des possibilités pédagogiques, pas une affirmation
que chaque détail de Pymunk appartient au programme officiel de NSI.

## Pistes de correction du squelette

### 1. Borner x

```python
return max(gauche + rayon, min(droite - rayon, x))
```

Le contrat impose une largeur suffisante. Demander ce qu'il faudrait faire
si cette précondition était fausse. Dans le jeu complet, ajouter l'épaisseur
des parois et une petite marge.

### 2. Fusion possible

```python
return niveau_a == niveau_b and 0 <= niveau_a < niveau_max
```

Le cas de deux objets terminaux n'est pas traité dans ce premier exercice.
Le jeu complet retire cette paire et compte un circuit terminé. Discuter la
différence entre « aucune fusion », « création d'un niveau » et « suppression
terminale » avant de proposer une valeur de retour unique.

### 3. Score triangulaire

```python
return (niveau + 1) * (niveau + 2) // 2
```

Comparer avec la somme de 1 à `niveau + 1`. La formule utilise un nombre
constant d'opérations arithmétiques pour des entiers de taille bornée ; une
analyse fine tient compte de la taille des entiers Python.

### 4. Dépassement

```python
return y - rayon < limite
```

Piège classique : utiliser le centre plutôt que le sommet, ou inverser le
sens de l'inégalité. Un dessin dans le repère de l'écran lève l'ambiguïté.

### 5. Paires sans doublons

```python
paires = sorted({tuple(sorted((a, b))) for a, b in contacts if a != b})
utilises = set()
resultat = []
for a, b in paires:
    if a not in utilises and b not in utilises:
        resultat.append((a, b))
        utilises.update((a, b))
return resultat
```

Ce choix est glouton. Sur `(1,2), (1,3), (2,4)`, il garde seulement `(1,2)` ;
les deux paires `(1,3)` et `(2,4)` auraient pourtant utilisé quatre objets.
Dans le jeu, ce comportement déterministe est acceptable : l'objectif n'est
pas de calculer un couplage maximum, mais d'empêcher une double consommation.

## Adapter la difficulté sans déséquilibrer l'ensemble

Modifier un paramètre à la fois. Des objets beaucoup plus grands augmentent
la saturation ; un dernier diamètre supérieur à la largeur du bac rend le
jeu impossible. Une file limitée à de très petits objets peut augmenter la
durée avant une grande fusion. Un délai de débordement trop court pénalise
les rebonds et les composants fraîchement créés.

Conserver `MAX_SPEED` et un pas suffisamment petit limite les traversées de
parois. Une friction excessive immobilise le tas ; une forte restitution
peut éjecter les objets par l'ouverture. Le bac doit rester ouvert en haut
pour garder la mécanique de débordement.

## Pièges à faire expliquer

- Retirer un objet en parcourant directement la même collection.
- Modifier l'espace Pymunk dans un callback de collision.
- Traiter seulement le premier instant d'un contact protégé par un délai.
- Fusionner le même objet avec deux voisins.
- Tirer un prochain objet après un clic refusé par le délai de lâcher.
- Faire avancer la physique et les compteurs pendant une pause.
- Réutiliser le même générateur aléatoire pour le gameplay et les particules.
- Écrire directement sur le seul fichier de sauvegarde, sans fichier temporaire.

## Distribution aux élèves

Le ZIP fourni contient le jeu de référence, le guide et ces notes. Pour une
recherche autonome, distribuer uniquement `SUJET_PROJET_NSI.md` et le squelette
élèves au début, puis les modules autorisés au fil des séances. Les TODO du
squelette sont intentionnels ; le jeu complet n'a pas de fonctionnalité laissée
à compléter pour pouvoir jouer.

## Validation de la version livrée

Voir `VALIDATION.md` pour l'environnement, les tests réellement exécutés et
les limites des vérifications. Faire un premier essai sur les postes de
l'établissement avant la séance de lancement du projet.
