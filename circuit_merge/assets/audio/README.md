# Musique principale

La piste intégrée est `music/Tetsuo_TheIronMan.mp3`, à la racine du projet.
Le chemin est résolu depuis le module Python, indépendamment du dossier de lancement.
Le MP3 est inclus dans l'APK par `source.include_exts` dans `buildozer.spec`.

Pour remplacer cette piste, placer le morceau choisi dans ce dossier sous le nom `main_theme.mp3` (ou `main_theme.ogg`, prioritaire).

La piste est lue en boucle et en streaming, à 35 % du volume. Le bouton Son contrôle la musique et les effets. Le passage en arrière-plan suspend la piste ; le retour reprend sa position si le son est activé. La piste peut être remplacée sans changer le code.

Sans fichier musical ou en cas d'erreur de décodage, le jeu conserve ses effets sonores.
