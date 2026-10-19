# Validation V2 — 11 octobre 2026

Copie de travail récupérée, puis vérifiée sous Linux / Python 3.12.14,
pygame-ce 2.5.8 et Pymunk 7.3.0. Pilotes SDL simulés.

- 38 tests automatisés réussis en 26 secondes.
- Contacts égaux / différents, chaînes, paire terminale et absence de double fusion.
- Sol, 11 niveaux à trois orientations, stress de plusieurs parties.
- Masse centrée, rotation de RAM, espaces entre pattes et baies laissés vides.
- Bornes de visée et débordement selon l'orientation ; projection SAT.
- Clignements, réactions prioritaires, choc réel et indépendance du hasard.
- Pause, clavier, molette, souris, redimensionnement et sauvegarde.
- Import V1 sans modifier le fichier d'origine ; format V2 restauré.
- Aperçu généré avec le vrai rendu et inspecté visuellement.

Les tests ne garantissent pas tous les empilements. Les silhouettes sont des
approximations 2D rigides. Le son matériel, le toucher et le plein écran sur
moniteur réel ne sont pas validés. Les scripts Windows sont conservés et relus,
mais cette copie n'a pas été exécutée sur Windows. L'ancien compte rendu V1
reste dans historique et ne constitue pas une validation de la V2.

Lancement sans écran sur 120 images réussi (code retour 0). Compilation
syntaxique réussie ; expérience occupation.py exécutée.
