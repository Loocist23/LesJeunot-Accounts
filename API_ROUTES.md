# API Routes

Toutes les routes exposent des réponses JSON `{status, data?}` et exigent l’en-tête `Content-Type: application/json` lorsqu’un corps est envoyé. Sauf mention contraire, elles retournent aussi les erreurs standard définies dans `main.py` (401 et 404 génériques).

Base locale par défaut : `http://localhost:5002`.

## Index

- `GET /` — ping basique, utile pour vérifier que l’API est démarrée.
- `GET /versions` — liste les sous-répertoires présents dans `routes/` (ex. `["v1"]`) pour signaler les versions disponibles.

## Utilisateurs (`/v1/user`)

> Les routes protégées utilisent des JWT issus du login. Ajoute `Authorization: Bearer <token>` pour les accès qui l’exigent.

- `POST /v1/user/` — crée un compte avec les champs JSON requis `lastname`, `firstname`, `age`, `email`, `password`. Optionnellement, ajoute `role` (`user` ou `admin`).
- `GET /v1/user/` — nécessite un access token d’administrateur ; retourne `users` avec la liste complète (incluant `uuid`, champs déchiffrés et rôles).
- `POST /v1/user/login` — authentifie un utilisateur (`email`, `password`) et renvoie `token.access` (valide 6 h) + `token.refresh` (valide 7 j).
- `GET /v1/user/refresh` — nécessite un refresh token (`@jwt_required(refresh=True)`); retourne un nouvel access token non fresh.
- `GET /v1/user/me` — nécessite un access token fresh ou non; fournit `lastname`, `firstname`, `age`, `email`, `role` décryptés de l’utilisateur courant.
- `PUT /v1/user/<id>` / `PATCH /v1/user/<id>` — exigent un access token; mettent à jour l’utilisateur authentifié avec les champs fournis (tous optionnels mais au moins un requis), y compris `role` (`user` ou `admin`). Le paramètre `<id>` provient du builder Flask mais n’est pas utilisé par le handler, donc toute valeur fonctionne tant qu’un JWT valide est fourni.
- `DELETE /v1/user/` et `DELETE /v1/user/<id>` — suppriment le compte courant. Là encore, l’argument `<id>` n’est pas consommé, mais l’endpoint existe en double via le builder pour supporter la suppression globale ou ciblée.

## Tickets (`/v1/ticket`)

> Toutes les routes ticket nécessitent un JWT d’accès.

- `GET /v1/ticket/` — retourne la liste `showings` de tous les tickets appartenant à l’utilisateur (404 si aucun ticket).
- `GET /v1/ticket/<id>` — retourne `showing` pour le ticket identifié par `<id>` si et seulement s’il appartient à l’utilisateur connecté.
- `GET /v1/ticket/?scope=all` — nécessite un access token d’administrateur ; renvoie `tickets` avec chaque réservation (`uuid`, `user_id`, `showing`).
- `POST /v1/ticket/` — crée un ticket associé à l’utilisateur courant. Corps JSON requis: `showing`. La réponse 201 contient `uuid`.
- `DELETE /v1/ticket/<id>` — supprime un ticket particulier et renvoie un message confirmant la suppression; 404 si l’UUID n’existe pas pour cet utilisateur.
- `DELETE /v1/ticket/` — supprime l’ensemble des tickets de l’utilisateur connecté (texte de réponse mis automatiquement au pluriel).

## Conseils de test rapides

- Pour créer ou connecter un utilisateur :
  ```bash
  curl -X POST http://localhost:5002/v1/user/ \
    -H "Content-Type: application/json" \
    -d '{"lastname":"Zegnal","firstname":"Anthony","age":"18","email":"loocist@proton.me","password":"Papacool55"}'

  curl -X POST http://localhost:5002/v1/user/login \
    -H "Content-Type: application/json" \
    -d '{"email":"loocist@proton.me","password":"Papacool55"}'
  ```
- Réutilise `token.access` dans `Authorization: Bearer …` pour les routes protégées, et `token.refresh` pour `/v1/user/refresh`.
