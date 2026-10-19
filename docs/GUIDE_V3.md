> V3.3 : voir CHAPITRE_2.md pour les missions 11–20 et les nouveaux équipements.

> Guide historique V3. Pour les objectifs actuels, voir EQUILIBRAGE_V31.md.
> Le nouveau mode est décrit dans INTRO_ARCHITECTURE.md.

# Projet Q — conception et atelier NSI

Le chapitre Fondations installe l'infrastructure classique d'un futur
ordinateur quantique. Le portique termine ce chapitre, pas l'ordinateur.
Il s'agit d'un univers de jeu : fusionner des résistances ne fabrique pas
réellement une LED. Les étapes quantiques restent à développer.

## Missions

| Mission | Objectif | Particularité |
|---|---|---|
| 1 Premier courant | 3 LED | Résistances uniquement |
| 2 Des établis, enfin | 24 points | Livraison variée |
| 3 Réserve d'énergie | 2 condensateurs | Transistor déjà présent |
| 4 Couloir de câbles | 6 fusions | Bac resserré |
| 5 Logique de chantier | 1 puce logique | Bac moins profond |
| 6 Pièces prioritaires | Fusionner 2 pièces marquées | Deux cibles séparées |
| 7 Test de puissance | 60 points | Bac resserré et stock |
| 8 Le chef d'orchestre | 1 microcontrôleur | Puce initiale |
| 9 Contrôle qualité | 6 fusions et 45 points | Bac encore plus étroit |
| 10 Laboratoire opérationnel | 1 RAM et 70 points | Double objectif final |

Ce premier chapitre est accessible, avec une mission courte de respiration
au numéro 8. Les solutions sont vérifiées automatiquement avec les vrais
contacts physiques ; le ressenti de difficulté reste à affiner avec des joueurs.

## Architecture

MissionEngine étend le moteur V2. Les parois sont propres à chaque instance,
sans changer les constantes globales de l'atelier libre. Les objectifs lisent
les fusions produites par les contacts ; une pièce marquée compte seulement
lorsqu'elle est consommée dans une fusion.

Profile possède la monnaie et l'inventaire. Un identifiant de tentative
empêche de créditer deux fois le même résultat. CampaignStore écrit un
fichier temporaire puis remplace atomiquement la sauvegarde. Un fichier
invalide est préservé avant de repartir avec un profil neuf. Ce stockage
local n'est pas un système anti-triche ni une synchronisation multijoueur.

Les constructions sont des récompenses visuelles permanentes, les outils
sont consommables. Aucun achat n'est obligatoire pour réussir une mission.
Les étoiles et les scores conservent le meilleur résultat de chaque mission.

## Activités NSI

1. Ajouter un objectif et une livraison ; trouver une solution physique avant
   de fixer le budget et les étoiles.
2. Vérifier l'invariant : crédits et charges ne deviennent jamais négatifs.
3. Comparer 60 FPS et ralenti : la simulation utilise un pas fixe de 1/240 s.
4. Tester l'idempotence d'une récompense et la sérialisation d'un état.
5. Ajouter un équipement procédural sans laisser la vue modifier l'économie.

Les profils et l'interface sont calibrés pour dix missions : ajouter un
chapitre demandera une migration de sauvegarde et une navigation adaptée.
Les supports V1/V2 restent utilisables via l'atelier historique `--classic`.
