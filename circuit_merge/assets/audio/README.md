# Musique principale

Le jeu détecte automatiquement les fichiers MP3 et OGG directement dans le dossier `music/`, quel que soit leur nom. Il choisit le premier par ordre alphabétique et le lit en boucle. Les autres pistes ne sont pas enchaînées.

Pour imposer un morceau, placer `main_theme.ogg` ou `main_theme.mp3` dans `circuit_merge/assets/audio/` (OGG prioritaire). Ces fichiers ont priorité sur `music/`.

La lecture est en streaming, à 35 % du volume. Le bouton Son contrôle la musique et les effets. Le passage en arrière-plan suspend la piste, le retour reprend sa position si le son est activé. Les chemins ne dépendent pas du dossier de lancement.

Après remplacement des morceaux, pousser les changements et récupérer le nouvel APK. Les MP3 et OGG sont inclus par Buildozer. Sans musique ou en cas d'erreur de décodage, les effets restent disponibles.
