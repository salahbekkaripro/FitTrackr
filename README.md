# FitTrackr
Plateforme web de suivi d’entraînement avec programmes, journal, boutique et gestion d’abonnements.

## Aperçu rapide
- Suivi complet des séances (durée, séries, reps, poids, RPE, temps de repos).
- Programmes et exercices personnalisés, rattachables aux séances.
- Dashboard & journal (stats hebdo, badges, export CSV pour les offres payantes).
- Abonnements Free/Power/Super Power avec remise boutique pour Super Power.
- Boutique intégrée (panier, commande, historique) et administration des utilisateurs/abonnements.

## Installation locale (dev)
1. Créer un environnement virtuel :  
   `python3 -m venv .venv && source .venv/bin/activate`
2. Installer les dépendances :  
   `pip install -r requirements.txt`
3. Appliquer les migrations :  
   `python manage.py migrate`
4. Charger la base de démo (indispensable pour tester) :  
   `python manage.py loaddata fixtures/demo_data.json`
5. Lancer le serveur :  
   `python manage.py runserver` puis ouvrir http://127.0.0.1:8000
   - Si vous avez déjà des données locales, supprimez `db.sqlite3` ou exécutez `python manage.py flush --noinput` avant de recharger la fixture, sinon l’unicité des e-mails bloquera l’import.

Par défaut, le projet utilise SQLite (`db.sqlite3`). En production, définissez `DATABASE_URL` (PostgreSQL supporté) pour basculer automatiquement.

## Données de démo et comptes
Le jeu de données officiel à importer est `fixtures/demo_data.json`.  
Comptes prêts à l’emploi :
- admin démo complet (Super Power + données riches) : `demo_admin` / `DemoAdmin123!`
- admin superuser : `admin` / `Admin123!`
- admin (rôle, sans superuser) : `admin_role` / `AdminRole123!`
- coach : `coach_user` / `Coach123!`
- membre : `test_user` / `Member123!`

Les offres d’abonnement (FREE, POWER, SUPER_POWER) sont déjà préchargées pour ces comptes.  
Le compte `demo_admin` inclut : un abonnement Super Power actif, un programme avancé 4 jours, 12 séances récentes avec séries/RPE, un objectif poids, un panier et une commande payée pour illustrer la boutique.

## Guide d’utilisation (manuel rapide)
- Connexion / création de compte : via `Créer un compte` ou en utilisant les identifiants ci-dessus.
- Onboarding : au premier login, renseignez âge, poids, taille et objectif pour personnaliser les stats (modifiable ensuite dans Profil).
- Abonnements : menu `Abonnement` pour choisir Free/Power/Super Power. L’offre Super applique -20% en boutique et déverrouille l’export CSV.
- Navigation principale :
  - `Suivi` : dashboard avec résumé hebdo, progression et badges.
  - `Journal` : historique des séances, filtre par programme, export CSV (Power+).
  - `Programmes` : créer/éditer un programme, y ajouter des exercices et ordonner les journées.
  - `Séances` : planifier une séance, lier à un programme, saisir séries/reps/poids/RPE/temps de repos.
  - `Boutique` → `Boutique` / `Panier` / `Historique des commandes` : ajouter au panier, passer commande, voir les achats; remise auto pour Super Power.
  - `Profil` : mettre à jour identité et mesures.
  - `Admin` : (admin/admin_role) gérer les utilisateurs, leur rôle et leur abonnement.
- Badges et rappels : les badges suivent la régularité et le volume des 4 dernières semaines; des messages invitent à compléter le profil si besoin.

## Fichiers utiles
- `fixtures/demo_data.json` : jeu de données officiel pour tests/démos.
- `render.yaml` : exemple de configuration Render (PostgreSQL + Django).
- `static/`, `templates/` : assets et templates HTML/CSS si vous personnalisez le front.
