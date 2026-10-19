# Chapitre 2 — Contrôle et signaux

Après la réussite de la mission 10, sélectionner « 2 / Contrôle et signaux ».
Les missions se débloquent une à une. Les bâtiments demandent crédits et
nombre de missions réussies ; ils ne sont pas une condition supplémentaire
d'accès aux missions. Un chapitre terminé reste rejouable.

## Missions

Les trois types de livraison sont de petits composants (niveaux 0, 1 et 2).
Les pièces avancées naissent des fusions. Les missions de production 12 et
17 sont des respirations entre les longues séries. Un seul succès suffit
à progresser ; les trois étoiles demandent davantage d'efficacité.

| Mission | Objectif | Budget | 3 étoiles | Parcours testé |
|---|---|---:|---:|---:|
| 11. Bus de données | 65 fusions ET 650 points | 108 | 90 | 88 |
| 12. Horloge de référence | Créer 3 microcontrôleurs | 80 | 58 | 56 |
| 13. Signaux propres | 2 pièces marquées ET 900 points | 142 | 120 | 118 |
| 14. Ligne de commande | 80 fusions ET 800 points | 120 | 97 | 95 |
| 15. Mémoire tampon | Créer 3 RAM | 132 | 106 | 104 |
| 16. Acquisition | 95 fusions ET 1100 points | 152 | 127 | 125 |
| 17. Baie compacte | Créer 4 microcontrôleurs | 100 | 74 | 72 |
| 18. Retour de mesure | 2 pièces marquées ET 1300 points | 180 | 154 | 152 |
| 19. Synchronisation | 3 RAM ET 1400 points | 200 | 175 | 173 |
| 20. Centre de pilotage | 125 fusions ET 1700 points | 218 | 194 | 192 |

Le parcours de test vise une pièce de même niveau proche du haut de la pile,
ou une colonne de repli, et laisse la physique se stabiliser. Il n'ajoute
aucune pièce, ne modifie aucun compteur et n'emploie aucun bonus. D'autres
solutions existent ; ces nombres ne sont pas des minimums garantis.

## Les constructions

| Équipement | Coût | Missions réussies | Rôle dans le décor |
|---|---:|---:|---|
| Réseau de contrôle | 550 | 12 | Le bus relie les consoles et les baies. |
| Horloge de référence | 620 | 14 | Une référence commune synchronise les signaux. |
| Générateur de signaux | 700 | 16 | Les impulsions de commande sont préparées. |
| Chaîne de lecture | 780 | 18 | Les signaux de mesure sont acquis et numérisés. |
| Pilotage synchronisé | 850 | 20 | Le contrôle est prêt pour la future cryogénie. |

Les dix premières victoires du chapitre 2 rapportent au moins 3 875 crédits
(hors primes de score). Les constructions coûtent 3 500 crédits : elles
sont finançables sans répéter les niveaux si la monnaie leur est réservée.
Les bonus restent facultatifs et leurs prix ne changent pas.

## Utilisation en NSI

Le centre de contrôle illustre les fonctions « commander », « synchroniser »
et « acquérir ». Le décor est une représentation pédagogique stylisée : les
fusions ne décrivent pas une fabrication réelle et aucun qubit n'est encore
simulé. L'étage cryogénique et la mise en service quantique sont à venir.

Questions possibles : quel est le rôle d'une horloge commune ? Pourquoi
une chaîne de mesure et une chaîne de commande sont-elles distinctes ?
Comment une mémoire tampon régule-t-elle un flux de données ?

Pour modifier les niveaux : `circuit_merge/campaign.py` contient les données
immuables des missions. Comparer un objectif, un budget et un seuil d'étoiles.
Le test `tests/test_v33.py` vérifie les parcours physiques, la migration,
la sauvegarde de la mission 20, les transactions et les onglets.

## Installation et progression

Fermer l'ancienne version, extraire ce ZIP dans un nouveau dossier puis
utiliser `Installer_Windows.bat` et `Lancer_Windows.bat`. La V3.3 reprend
`%LOCALAPPDATA%/CircuitMerge/project_q_v3.json` sous Windows.
Conserver une copie avant migration si l'on veut pouvoir revenir à la V3.2.
Une mission V3 historique suspendue conserve son ancien jeu de règles.
Le montage PC conserve le glisser-déposer de la V3.2.
