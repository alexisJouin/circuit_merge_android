# Validation V3.2 — 14 octobre 2026

Windows, Python 3.14.2, pygame-ce 2.5.8 et Pymunk 7.3.0.

65 tests automatisés réussis, dont les campagnes V3 et V3.1 et les interactions
de montage. Les tests envoient des événements de pression, déplacement et
relâchement à l'application : montage complet, mauvais socket, dépendances,
dépose hors fenêtre, petit connecteur après redimensionnement, Échap,
perte de focus, toucher et événements souris synthétiques en double.

Une pièce en cours de déplacement n'est pas sauvegardée comme installée.
Une dépose réussie l'est. Sans guide, changer de sélection ne dessine aucun
surlignage de la zone cible. Les captures de la carte mère et du montage
complet ont été inspectées. Test de lancement de 120 images sans écran réussi.

Les événements tactiles sont simulés ; aucun écran tactile physique n'a été
testé. Les formes sont pédagogiques et schématiques, pas un modèle d'une
carte mère commerciale. La compatibilité des références et la rotation des
composants ne sont pas simulées. Les deux barrettes forment un kit.
