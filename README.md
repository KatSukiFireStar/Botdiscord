# Bot Discord — Suggestions de films

Bot Discord permettant aux membres d'un serveur de proposer des films, avec
un tirage au sort automatique chaque vendredi à 16h.

## Fonctionnalités

- `!film <nom du film>` : cherche le film sur l'API **OMDb** (gratuite).
  S'il existe, il est ajouté à la liste avec le pseudo de la personne qui l'a
  proposé, et l'affiche du film est envoyée dans le salon. S'il n'existe pas,
  le bot le signale.
- `!removefilm <nom du film>` : retire un film de la liste, **uniquement**
  si c'est la même personne qui l'avait ajouté.
- **Tirage automatique** : chaque vendredi à 16h00 (heure de Paris), le bot
  tire un film au sort parmi la liste, l'annonce avec son affiche, puis vide
  la liste pour la semaine suivante.
- `!forcedraw` (réservée aux administrateurs) : force un tirage immédiat,
  pratique pour tester sans attendre vendredi.

## 1. Créer le bot Discord

1. Va sur https://discord.com/developers/applications et crée une nouvelle
   application.
2. Dans l'onglet **Bot**, clique sur "Reset Token" pour récupérer ton
   `DISCORD_TOKEN`, et active l'option **MESSAGE CONTENT INTENT** (nécessaire
   pour lire les commandes `!film ...`).
3. Dans l'onglet **OAuth2 > URL Generator**, coche les scopes `bot` et
   `applications.commands`, puis les permissions `Send Messages`,
   `Embed Links`, `Read Message History`. Utilise l'URL générée pour inviter
   le bot sur ton serveur.

## 2. Récupérer une clé API OMDb (gratuite)

Va sur http://www.omdbapi.com/apikey.aspx, choisis l'offre **FREE** (1000
requêtes/jour), renseigne un email : tu recevras ta clé API par mail.

## 3. Configuration

1. Copie `.env.example` en `.env` :
   ```bash
   cp .env.example .env
   ```
2. Remplis les valeurs dans `.env` :
   - `DISCORD_TOKEN` : le token de ton bot.
   - `OMDB_API_KEY` : ta clé OMDb.
   - `DRAW_CHANNEL_ID` : l'identifiant du salon où le tirage du vendredi
     sera annoncé (active le mode développeur dans Discord, puis clic droit
     sur le salon → "Copier l'identifiant").

## 4. Installation et lancement

```bash
python -m venv venv
source venv/bin/activate   # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

Le bot se connecte, et la liste des films est sauvegardée automatiquement
dans `films.json` à côté du script (elle survit donc à un redémarrage).

## Notes techniques

- Le fuseau horaire utilisé pour le tirage du vendredi est `Europe/Paris`
  (modifiable dans `bot.py`, variable `PARIS_TZ`).
- Le tirage vérifie l'heure toutes les minutes ; il ne se déclenche qu'une
  seule fois par vendredi grâce à un verrou sur la date.
- Le bot doit rester en ligne en permanence pour que le tirage automatique
  fonctionne (hébergement recommandé : un petit VPS, Railway, Render, etc.).
- Le stockage est un simple fichier JSON. Pour un usage multi-serveurs
  (plusieurs serveurs Discord utilisant le même bot), il faudrait adapter
  le stockage pour séparer les listes par `guild_id` — actuellement la
  liste est globale au bot.
