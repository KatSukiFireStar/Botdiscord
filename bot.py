"""
Bot Discord - Gestion de suggestions de films
================================================

Commandes :
  !film <nom du film>      -> Cherche le film via l'API OMDb, l'ajoute à la
                               liste s'il existe et envoie l'affiche.
  !removefilm <nom du film>-> Retire le film de la liste, uniquement si
                               c'est la personne qui l'a ajouté.

Tâche planifiée :
  Chaque vendredi à 16h00 (heure de Paris), le bot tire un film au sort
  parmi la liste, annonce le résultat avec l'affiche, puis réinitialise
  la liste.

Stockage :
  La liste des films est sauvegardée dans un fichier JSON (films.json)
  afin de survivre à un redémarrage du bot.
"""

import os
import json
import random
import logging
from datetime import datetime
import pytz

import aiohttp
import discord
from discord.ext import commands, tasks

try:
    from dotenv import load_dotenv
    load_dotenv()  # charge automatiquement le fichier .env s'il existe
except ImportError:
    pass  # python-dotenv est optionnel ; on peut aussi définir les variables autrement

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
# ID du salon dans lequel le tirage hebdomadaire sera annoncé.
DRAW_CHANNEL_ID = os.getenv("DRAW_CHANNEL_ID")

DATA_FILE = "films.json"
PARIS_TZ = pytz.timezone("Europe/Paris")

OMDB_URL = "https://www.omdbapi.com/"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("film-bot")

intents = discord.Intents.default()
intents.message_content = True  # nécessaire pour lire le contenu des commandes préfixées

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------------------------------------------------------
# Persistance (stockage JSON simple)
# ---------------------------------------------------------------------------

def load_films() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_films(films: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(films, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Appel à l'API OMDb
# ---------------------------------------------------------------------------

async def search_movie(title: str) -> dict | None:
    """Cherche un film par titre sur OMDb. Retourne un dict ou None."""
    if not OMDB_API_KEY:
        raise RuntimeError("OMDB_API_KEY n'est pas configurée.")

    params = {"apikey": OMDB_API_KEY, "t": title, "type": "movie"}

    async with aiohttp.ClientSession() as session:
        async with session.get(OMDB_URL, params=params) as resp:
            data = await resp.json()

    if data.get("Response") == "True":
        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "poster": data.get("Poster"),
            "imdb_id": data.get("imdbID"),
        }
    return None


# ---------------------------------------------------------------------------
# Événements
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    log.info(f"Connecté en tant que {bot.user} (id: {bot.user.id})")
    if not weekly_draw_loop.is_running():
        weekly_draw_loop.start()

# ---------------------------------------------------------------------------
# Commande !help
# ---------------------------------------------------------------------------

@bot.command(name="helps")
async def helps_command(ctx: commands.Context, *, titre: str = None):
    await ctx.send("Il existe plusieurs commandes: " +
                    "\n - !film 'Nom du film': Ajoute le premier film trouvé dans la base de film de OMDB au tirage"+
                    "\n - !removefilm 'Nom du film': Enleve le film si le nom exacte se trouve dans le tirage et que tu es à l'origine de l'ajout"+
                    "\n - !affichefilms: Affiche les films présent pour le prochain tirage")

# ---------------------------------------------------------------------------
# Commande !affichefilm
# ---------------------------------------------------------------------------

@bot.command(name="affichefilms")
async def affichefilms_command(ctx: commands.Context, *, titre: str = None):
    films = load_films()

    nb = 0
    for film in films:
        nb += 1

    if nb == 0:
        await ctx.send("Il n'y a pas encore de film dans la liste pour le prochain tirage.")
        return
    
    await ctx.send("Il y a " + str(nb) + " films ajouté pour le prochain tirage. Voici les films déjà ajouter.")

    for film in films:
        embed = discord.Embed(
            title=f"🎬 {film['title']} ({film['year']})",
            description=f"Ajouté à la liste par **{ctx.author.mention}**",
            color=discord.Color.green(),
        )
        if film["poster"] and film["poster"] != "N/A":
            embed.set_image(url=film["poster"])
        

        await ctx.send(embed=embed)

# ---------------------------------------------------------------------------
# Commande !film
# ---------------------------------------------------------------------------

@bot.command(name="film")
async def film_command(ctx: commands.Context, *, titre: str = None):
    if not titre:
        await ctx.send("⚠️ Merci d'indiquer un nom de film. Exemple : `!film Inception`")
        return

    async with ctx.typing():
        try:
            movie = await search_movie(titre)
        except RuntimeError as e:
            await ctx.send(f"❌ Erreur de configuration du bot : {e}")
            return
        except aiohttp.ClientError:
            await ctx.send("❌ Impossible de contacter la base de films pour le moment, réessaie plus tard.")
            return

    if movie is None:
        await ctx.send(f"❌ Le film **{titre}** n'existe pas (ou n'a pas été trouvé).")
        return

    films = load_films()

    entry = {
        "title": movie["title"],
        "year": movie["year"],
        "poster": movie["poster"],
        "imdb_id": movie["imdb_id"],
        "added_by_id": ctx.author.id,
        "added_by_name": str(ctx.author),
        "added_at": datetime.now(PARIS_TZ).isoformat(),
    }
    

    embed = discord.Embed(
        title=f"🎬 {movie['title']} ({movie['year']})",
        description=f"Ajouté à la liste par **{ctx.author.mention}**",
        color=discord.Color.green(),
    )
    if movie["poster"] and movie["poster"] != "N/A":
        embed.set_image(url=movie["poster"])
    embed.set_footer(text="Film ajouté au tirage de vendredi !")

    try:
        await ctx.send(embed=embed)
        films.append(entry)
        save_films(films)
    except:
        await ctx.send("Permission refusée le film n'est pas ajouté")


# ---------------------------------------------------------------------------
# Commande !removefilm
# ---------------------------------------------------------------------------

@bot.command(name="removefilm")
async def removefilm_command(ctx: commands.Context, *, titre: str = None):
    if not titre:
        await ctx.send("⚠️ Merci d'indiquer le nom du film à retirer. Exemple : `!removefilm Inception`")
        return

    films = load_films()

    # On cherche une correspondance insensible à la casse.
    match = next((f for f in films if f["title"].lower() == titre.lower()), None)

    if match is None:
        await ctx.send(f"❌ Le film **{titre}** n'est pas dans la liste.")
        return

    if match["added_by_id"] != ctx.author.id:
        await ctx.send(
            f"❌ Tu ne peux pas retirer **{match['title']}** : "
            f"seul **{match['added_by_name']}** (celui/celle qui l'a ajouté) peut le faire."
        )
        return

    films.remove(match)
    save_films(films)
    await ctx.send(f"🗑️ **{match['title']}** a été retiré de la liste par {ctx.author.mention}.")


# ---------------------------------------------------------------------------
# Tirage hebdomadaire (chaque vendredi à 16h, heure de Paris)
# ---------------------------------------------------------------------------

_last_draw_date = None  # évite de tirer deux fois pendant la même minute/heure


@tasks.loop(minutes=1)
async def weekly_draw_loop():
    global _last_draw_date

    now = datetime.now(PARIS_TZ)

    # vendredi = weekday() == 4 ; on déclenche à 16h00 pile (contrôle sur la minute)
    if now.weekday() == 4 and now.hour == 16 and now.minute == 0:
        if _last_draw_date == now.date():
            return  # déjà fait aujourd'hui
        _last_draw_date = now.date()
        await do_weekly_draw()


@weekly_draw_loop.before_loop
async def before_weekly_draw_loop():
    await bot.wait_until_ready()


async def do_weekly_draw():
    if not DRAW_CHANNEL_ID:
        log.warning("DRAW_CHANNEL_ID n'est pas configuré, tirage annulé.")
        return

    channel = bot.get_channel(int(DRAW_CHANNEL_ID))
    if channel is None:
        log.warning("Impossible de trouver le salon DRAW_CHANNEL_ID=%s", DRAW_CHANNEL_ID)
        return

    films = load_films()

    if not films:
        await channel.send("📭 Aucun film n'a été proposé cette semaine, pas de tirage aujourd'hui !")
        return

    winner = random.choice(films)

    embed = discord.Embed(
        title=f"🎉 Tirage au sort de la semaine : {winner['title']} ({winner['year']})",
        description=f"Proposé par **{winner['added_by_name']}**",
        color=discord.Color.gold(),
    )
    if winner["poster"] and winner["poster"] != "N/A":
        embed.set_image(url=winner["poster"])
    embed.set_footer(text=f"{len(films)} film(s) étaient en lice cette semaine.")

    await channel.send(embed=embed)

    # Réinitialisation de la liste
    save_films([])
    log.info("Tirage effectué : %s. Liste réinitialisée.", winner["title"])


# ---------------------------------------------------------------------------
# (Optionnel) Commande pour forcer manuellement un tirage - utile pour tester
# ---------------------------------------------------------------------------

@bot.command(name="forcedraw")
@commands.has_permissions(administrator=True)
async def force_draw_command(ctx: commands.Context):
    """Commande admin pour tester le tirage sans attendre vendredi 16h."""
    await do_weekly_draw()


# ---------------------------------------------------------------------------
# Lancement
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("❌ La variable d'environnement DISCORD_TOKEN est manquante.")
    if not OMDB_API_KEY:
        raise SystemExit("❌ La variable d'environnement OMDB_API_KEY est manquante.")
    bot.run(DISCORD_TOKEN)
