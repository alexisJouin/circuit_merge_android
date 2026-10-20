# Circuit Merge — préparation du portage Android

Base : dépôt alexisJouin/circuit_merge, révision 44fb646 (V3.3).
Le jeu complet est conservé : chapitres 1 et 2, mode libre et montage PC.
**Aucun APK ou AAB n'a encore été compilé ni testé sur téléphone.**

## Changements

- Entrée Android distincte ; lancement PC conservé.
- Affichage paysage proportionnel avec barre Accueil/Pause/Rotation.
- Un seul doigt contrôle une interaction ; doublons souris tactiles ignorés.
- Sauvegarde dans le stockage privé Android, sans permission de stockage.
- Sauvegarde et pause au passage en arrière-plan ; bouton Retour adapté.
- Recettes locales Pygame-CE 2.5.8 et Pymunk 7.3.0.

## Générer un APK de test

1. Reporter le contenu de cette archive dans le dépôt, y compris le dossier caché .github.
2. Dans GitHub : Actions > Android APK and AAB > Run workflow. Laisser release désactivé.
3. Après succès, télécharger circuit-merge-android dans Artifacts et extraire l'APK.
4. Installer sur un appareil de test ARM64 Android 8 ou plus récent.

Les recettes natives n'ont pas été compilées ici. Le premier lancement du workflow peut révéler des incompatibilités à corriger. Cette configuration ne garantit pas encore un binaire fonctionnel.

## AAB signé pour Google Play

Identifiant provisoire : fr.alexisjouin.circuitmerge. À confirmer avant la première publication.
Créer et conserver une clé d'envoi personnelle :

    keytool -genkeypair -v -keystore circuitmerge-upload.jks -alias upload -keyalg RSA -keysize 3072 -validity 10000

Ne jamais committer cette clé. Ajouter ces secrets dans Settings > Secrets and variables > Actions :

- ANDROID_KEYSTORE_BASE64 : fichier de clé encodé en base64.
- ANDROID_KEYSTORE_PASSWORD : mot de passe du fichier.
- ANDROID_KEY_ALIAS : upload.
- ANDROID_KEY_PASSWORD : mot de passe de la clé.

Relancer avec release activé. L'AAB signé sera joint à l'APK si la compilation réussit.
Aucune clé ni aucun mot de passe n'est fourni. Ne pas envoyer de clé privée dans une conversation.

## Validation nécessaire avant publication

Tester les deux chapitres, la physique, le son, les rotations, le montage PC, le multi-touch, Retour, la mise en arrière-plan et la restauration après arrêt forcé. Vérifier la lisibilité sur petit écran : la disposition PC reste réduite proportionnellement.

Vérifier les exigences actuelles dans Play Console, l'API cible et la compatibilité des bibliothèques natives avec les pages mémoire de 16 Ko. La configuration cible API 36 et ARM64 ; sa conformité doit être contrôlée sur le binaire produit. Prévoir les licences des dépendances, l'icône, des captures Android réelles, la politique de confidentialité et les déclarations Play Console.

## Alternative Ubuntu

Installer Java 17 et les dépendances indiquées dans .github/workflows/android.yml, puis lancer :

    buildozer -v android debug

Prévoir plusieurs Go disponibles. Le premier téléchargement et la compilation peuvent être longs.

## Références

- https://developer.android.com/guide/app-bundle
- https://github.com/kivy/python-for-android
- https://github.com/pygame-community/pygame-ce
- https://github.com/viblo/pymunk

## Vérifications effectuées le 19 octobre 2026

75 tests Python réussis sur Windows avec Pygame-CE 2.5.8 et Pymunk 7.3.0, dont 5 tests ajoutés pour les événements Android simulés. Vérification syntaxique Python réussie. Aperçu du rendu paysage inspecté en mode SDL sans écran. Ces vérifications ne remplacent ni la compilation native Android ni un test sur appareil.

## Version 0.2.0 — interface téléphone

- Orientation portrait, accueil Aventure / Mode fun, parcours de 20 niveaux et
  accès direct au niveau suivant après une victoire.
- Les menus chantier, boutique et montage PC restent dans la version ordinateur.
  Le format de sauvegarde existant est conservé, y compris la progression et les
  tentatives suspendues.
- Un seul `display.flip()` par image complète : suppression de l'alternance
  avec/sans barre tactile. Cible de 30 images/s en jeu, 15 dans les menus.
- Canevas 600 × 1080, surface de mise à l'échelle réutilisée, cache de texte
  limité à 128 entrées et cache de rotations limité à 16 Mio. Visages statiques,
  sans particules ni simulation d'aperçu de chute. La physique reste inchangée.
- Validation locale : tests de navigation tactile, reprise, mise en arrière-plan,
  présentation unique et progression ; rendu de toutes les missions.
- À vérifier sur téléphone : fluidité avec un bac chargé, lisibilité, glisser /
  relâcher, reprise après verrouillage. Les mesures sur ordinateur ne préjugent
  pas du débit réel sur Android.
