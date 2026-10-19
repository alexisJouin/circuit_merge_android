# Validation V3.3 — 15 octobre 2026

Windows, Python 3.14.2, pygame-ce 2.5.8 et Pymunk 7.3.0.

70 tests validés : 65 tests de régression et 5 nouveaux tests du chapitre 2.
La migration et la navigation ont été relancées après correction de la
comparaison JSON du test et du titre de l'écran. Le parcours des dix
nouvelles missions utilise de vrais lâchers, collisions et fusions, sans
bonus ni modification des compteurs. Résultats : 88, 56, 118, 95, 104, 125,
72, 152, 173 et 192 lâchers respectivement pour les missions 11 à 20.

Vérifiés : budgets, trois étoiles accessibles, récompense versée une seule
fois, financement des cinq bâtiments à partir des premières victoires,
conditions d'achat, migration des profils à dix missions, maintien des
crédits/records/étoiles/montage PC/mission suspendue, reprise de la mission
20, onglets cliqués, verrouillage des missions et dessin du chantier final.

Lancement sans écran de 120 images réussi. Captures du chantier complet,
de sa progression et d'une mission générées ; chantier inspecté visuellement.
Les tests utilisent un dossier temporaire isolé, pas le profil du joueur.

Limites : stratégie automatique déterministe, aucune séance d'équilibrage
avec une classe. La durée humaine dépend du rythme des placements. Ces
solutions ne prouvent pas que toutes les stratégies gagnent. Les dix niveaux
du chapitre 1 et le montage PC restent couverts par les tests antérieurs.
Les chapitres 3 à 5 ne sont pas jouables dans cette version.
