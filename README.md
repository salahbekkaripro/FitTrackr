# FitTrackr

## Données de démo
Un jeu de données prêt à charger est disponible dans `fixtures/demo_data.json`.

Charger les données (depuis la racine du projet) :
```bash
python3 manage.py migrate
python3 manage.py loaddata fixtures/demo_data.json
```

Comptes inclus :
- admin superuser : `admin` / `Admin123!`
- admin (rôle, sans superuser) : `admin_role` / `AdminRole123!`
- coach : `coach_user` / `Coach123!`
- membre : `test_user` / `Member123!`

Les offres d’abonnement de base (FREE, POWER, SUPER_POWER) sont préchargées pour ces comptes.
