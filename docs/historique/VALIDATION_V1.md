# Validation — version 1.0.1

Vérifications exécutées le **7 octobre 2026**.

## Environnement testé

- Python 3.12.14, Linux x86-64.
- pygame-ce 2.5.8, Pymunk 7.3.0.
- SDL en mode sans écran pour les scénarios automatisés et les captures.

## Résultats

- **20 tests automatisés réussis** avec `python -m unittest discover -s tests -v`.
- Test de lancement sur 120 images réussi avec `--smoke-test 120 --mute`.
- Compilation syntaxique des modules, expériences et exercices réussie.
- Résolution et téléchargement des dépendances précompilées pour Windows
  x86-64 / CPython 3.14 réussis, sans compilation de code source.
- Capture du montage de démonstration générée avec le vrai rendu Pygame.
- Inspection visuelle de l'interface, des textes, du bac et des composants.
- Expérience de chute libre exécutée à 30, 60, 120 et 240 Hz : les écarts de
  position après une seconde valent 18, 9, 4,5 et 2,25 pixels pour le modèle testé.

## Comportements couverts

Contact égal / inégal, trois contacts simultanés, fusion en chaîne, paire
terminale, prochaine pièce, délai de lâcher, bornes de visée, arrêt au sol,
stabilité de plusieurs parties pseudoaléatoires, tolérance de création,
dépassement continu, chronomètres séparés, fin de partie, sauvegarde JSON,
tirages restaurés, rejet de NaN, pause, clic / relâcher, clic sur un menu,
clavier, mode NSI, ralenti, perte de focus et redimensionnement.

## Portée

Les essais de simulation et de rendu ont été effectués sous Linux. Les
scripts Windows et les instructions macOS sont fournis mais n'ont pas été
exécutés sur ces systèmes. Le son a été initialisé avec le pilote SDL simulé,
sans écoute sur un périphérique réel. Le plein écran et le toucher matériel
n'ont pas été vérifiés sur un appareil physique.

Les contacts au chargement sont recalculés : un état sauvegardé ne garantit
pas une reprise identique bit à bit. Les tests de charge ne couvrent pas tous
les empilements possibles. Les paramètres sont ceux de Circuit Merge ; ils
n'ont pas été extraits du jeu Android.

## Correction d'installation

La version 1.0.0 épinglait Pygame 2.6.1. Sur un interpréteur sans paquet
précompilé correspondant, l'installation pouvait tenter une compilation et
échouer sur le module privé `setuptools._distutils.msvccompiler`.
La version 1.0.1 utilise pygame-ce 2.5.8 et n'autorise que les paquets
précompilés. L'installateur vérifie la version de Python, enlève l'ancienne
distribution Pygame dans `.venv` et vérifie les imports après installation.
