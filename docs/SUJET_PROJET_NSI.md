# Projet NSI — Circuit Merge : assemblez l'informatique

## Mission

Créer un jeu Python où le joueur lâche des composants électroniques dans un
bac. Deux composants du même niveau fusionnent au contact en un objet plus
grand. Le joueur cherche à atteindre le supercalculateur tout en évitant
le débordement.

Le projet se réalise en binôme ou trinôme. Proposition : **8 séances de
1 h 30**, soit 12 heures, avec adaptation possible à 6–10 séances selon
l'expérience des élèves. Le professeur peut fournir le moteur physique et
faire construire les règles / l'interface, ou proposer une version plus
ambitieuse en terminale.

## Contrat minimal

1. Une fenêtre contient un bac ouvert et un composant à lâcher.
2. La souris ou le clavier permet de choisir la position horizontale.
3. Le composant tombe, rebondit et s'appuie sur le sol / les autres objets.
4. Deux objets de même niveau fusionnent en un seul du niveau suivant.
5. Le score augmente après une fusion ; le prochain objet est annoncé.
6. Une pièce dépassant trop longtemps la ligne provoque une fin de partie.
7. Le joueur peut recommencer et mettre en pause.
8. Le code comporte fonctions, noms explicites et documentation des choix.

Commencer avec quatre niveaux et des cercles colorés. Ajouter les onze niveaux
et les illustrations après validation des règles. Le mode pédagogique et la
sauvegarde constituent des prolongements, pas des prérequis au premier prototype.

## Progression par séances

| Séance | Travail attendu | Preuve de réussite |
| --- | --- | --- |
| 1 | Décrire les règles, dessiner le repère, compléter les fonctions simples | Schéma, contrats et cas limites |
| 2 | Afficher bac / objet, lire les entrées, borner la visée | Aucun lâcher ne commence dans une paroi |
| 3 | Ajouter gravité, sol et collisions avec Pymunk | Deux objets différents s'empilent |
| 4 | Séparer données et règles, organiser la file de fusion | Trois objets ne donnent pas deux fusions incohérentes |
| 5 | Ajouter score, prochain objet et tirage pondéré | Le composant annoncé est bien le prochain lâché |
| 6 | Défaite, pause, reprise et nouvelle partie | Un menu n'avance pas le chronomètre de défaite |
| 7 | Améliorer le thème, ajouter une extension et des tests | Comparaison avant/après avec un critère mesuré |
| 8 | Finaliser documentation, démonstration et présentation orale | Projet lancé sur un autre ordinateur |

## Répartition du travail

En binôme : une personne travaille sur le moteur et les règles, l'autre sur
les entrées / le rendu ; échanger les rôles au milieu du projet. En trinôme,
une troisième responsabilité regroupe les tests, les données et la persistance.

Chaque élève doit pouvoir expliquer une fonction écrite par un partenaire.
Se mettre d'accord sur les noms des fonctions, les arguments, les valeurs
renvoyées et les événements avant de travailler séparément. Les rôles ne
dispensent personne de comprendre le jeu complet.

## Travail de découverte sans bibliothèque

Compléter `atelier_nsi/regles_a_completer.py` : borner une abscisse, reconnaître
une fusion possible, calculer des points, détecter un dépassement et choisir
des paires sans réutiliser une pièce.

Pour chaque fonction, proposer au moins un cas ordinaire et un cas limite.
Justifier le résultat attendu. Le squelette est autonome : il prépare le
raisonnement, puis les fonctions pourront être adaptées au moteur du groupe.

## Expérience obligatoire

Choisir **un seul paramètre** parmi gravité, restitution, frottement ou pas
de temps. Formuler une hypothèse avant de modifier le programme. Garder une
graine de tirages fixe et un scénario d'actions aussi identique que possible.

Présenter un petit tableau avec le paramètre, deux valeurs et une mesure
concrète : temps de chute, nombre de rebonds, durée d'une simulation, etc.
Expliquer les limites de la comparaison. Le score seul dépend trop du joueur
pour établir facilement l'effet d'un paramètre physique.

## Livrables

- Dossier contenant le programme, les dépendances et les ressources nécessaires.
- README indiquant installation, lancement, contrôles et fonctionnalités.
- Schéma de l'organisation des modules et description de deux algorithmes.
- Quelques tests utiles et leurs résultats, avec les cas qu'ils protègent.
- Tableau de l'expérience et interprétation des résultats.
- Présentation orale de 5–7 minutes, démonstration incluse.
- Une trace des contributions de chaque élève (journal, commits ou tableau).

## Proposition de barème sur 20

| Critère | Points | Indicateurs |
| --- | ---: | --- |
| Règles fonctionnelles | 6 | Chute / collisions 2, fusion 2, file et score 1, fin de partie / reprise 1 |
| Structure et qualité du code | 4 | Fonctions / modules 2, noms et contrats 1, responsabilités 1 |
| Tests et cas limites | 3 | Scénarios pertinents 2, explication d'un bug évité 1 |
| Démarche expérimentale | 2 | Hypothèse / protocole 1, mesures / interprétation 1 |
| Documentation et autonomie de lancement | 2 | README 1, explications / dépendances 1 |
| Présentation et maîtrise individuelle | 3 | Démonstration 1, explication 1, questions 1 |

Une extension esthétique seule ne compense pas une fusion incorrecte. Le
barème peut récompenser l'ambition dans les rubriques concernées tout en
gardant la priorité à un programme compris et fiable.

## Questions pour l'oral

- Pourquoi distinguer le niveau et l'identifiant d'un composant ?
- Que se passe-t-il si trois objets identiques se touchent au même instant ?
- Pourquoi ne pas faire évoluer la physique d'une distance fixe par image ?
- Comment garantir que le prochain objet annoncé est réellement utilisé ?
- Pourquoi le compteur de dépassement appartient-il à chaque pièce ?
- Quelles données faut-il sauvegarder pour reprendre la partie ?
- Quel test a détecté ou empêché une erreur dans votre projet ?

## Extensions au choix

Préférer une extension aboutie : statistiques CSV, niveaux de difficulté,
thème graphique remplaçable, panneau d'inspection, sauvegarde JSON, comparaison
de distributions de tirages ou classement local.

Les fonctionnalités ajoutées doivent être décrites dans le README et
accompagnées d'un scénario montrant qu'elles fonctionnent.
