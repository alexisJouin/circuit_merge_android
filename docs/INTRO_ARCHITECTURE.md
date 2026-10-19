# Une introduction à l'architecture matérielle — 15 minutes

Manipulation V3.2 : maintenir une vignette du stock, glisser et relâcher
sur le connecteur. Les onglets Pièces et Finition contiennent tout le matériel.
Le guide est désactivé par défaut ; la sérigraphie du PCB reste visible.
Échap annule une prise. Un clic simple consulte seulement la fiche.

Objectif : distinguer calcul, mémoire temporaire, stockage, communication,
alimentation et refroidissement à partir d'un montage de PC.

## Déroulement

1. **2 minutes — Observer.** Ouvrir Montage PC, guide désactivé.
   Demander aux élèves de nommer les pièces et de proposer leur rôle.
2. **6 minutes — Construire.** Faire placer les composants, éventuellement
   par un élève au tableau. Lire la fiche à droite après chaque étape.
   Activer le guide si nécessaire. Distinguer support physique et fonction.
3. **3 minutes — Diagnostiquer.** Tenter de démarrer avant de poser les
   câbles. Faire expliquer ce qui manque. Compléter puis valider le POST.
4. **4 minutes — Suivre une donnée.** « J'ouvre une image stockée sur le SSD.
   Où passe-t-elle ? Que change une modification non enregistrée ? »

## Réponses et points de vigilance pour l'enseignant

| Élément | Fonction à retenir |
|---|---|
| CPU | Exécuter les instructions et traiter les données |
| RAM | Conserver temporairement les données et programmes utilisés |
| SSD | Conserver durablement fichiers, logiciels et système |
| GPU | Produire les images et accélérer des calculs parallèles |
| Carte mère | Relier les composants par des bus et connecteurs |
| Alimentation | Convertir l'énergie secteur en tensions continues |
| Ventirad et pâte | Transférer puis dissiper la chaleur du CPU |
| Ventilateurs de boîtier | Renouveler l'air autour des composants |

Exemple simplifié : SSD → RAM → traitement par le CPU ; le GPU participe
à l'affichage vers l'écran. La sauvegarde écrit la nouvelle version sur le
stockage. Une coupure efface la RAM, pas les fichiers déjà enregistrés.
Les détails des caches, du DMA, des pilotes et du système peuvent être
introduits ensuite : cette chaîne est une première représentation.

Les câbles ATX, CPU/EPS et GPU/PCIe transportent l'énergie, pas les images.
Le connecteur PCIe de la carte graphique véhicule les données et fournit
aussi une partie de l'énergie. CPU/EPS et GPU/PCIe ne sont pas interchangeables.
M.2 désigne ici le format/connecteur ; NVMe le protocole utilisé sur PCIe.
Ce SSD n'a pas besoin d'un câble SATA, contrairement à d'autres stockages.

Le jeu suppose des composants compatibles et un GPU dédié ; tous les PC
n'en ont pas besoin. Le POST réel ne vérifie pas toutes les étapes physiques
que ce jeu impose : ici, c'est une validation pédagogique du montage complet.
Un POST réussi ne remplace pas l'installation d'un système d'exploitation.
Les ventilateurs sont connectés automatiquement dans cette représentation.
Les périphériques externes (écran, clavier, souris) peuvent être présentés
ensuite comme entrées/sorties ; ils ne sont pas à installer dans ce mode.

## Trois questions de sortie

- Pourquoi un SSD de grande capacité ne remplace-t-il pas la RAM ?
- Quelle différence entre calculer une image et l'afficher sur un écran ?
- Un PC correctement assemblé contient-il nécessairement déjà un système ?

Le montage est libre, sans note, monnaie ni pénalité. Recommencer ne touche
pas à la progression de la campagne. Un élève peut retirer les pièces pour
retrouver les dépendances entre support, alimentation et fonctionnement.
