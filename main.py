import os
import random
import aiohttp
import discord
from discord.ext import commands
from bot_logic import gen_pass
from bot_logic import flip_coin
from bot_logic import gen_emodji

# lavora sempre nella cartella di questo file (così trova images e token.txt)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# la variabile intents contiene i permessi al bot
intents = discord.Intents.default()
# abilita il permesso a leggere i contenuti dei messaggi
intents.message_content = True
# crea un bot che capisce i comandi che iniziano con $
bot = commands.Bot(command_prefix='$', intents=intents)

LISTA_COMANDI = """**I comandi disponibili sono:**
- Inquinamento di una città: `$pollution Milano`
- Link sull'inquinamento: `$inquinamento`
- Meme a caso: `$mem`
- Apri lo scrigno dei meme (comune, raro o leggendario?): `$scrigno`
- Lancia un dado: `$dado` (oppure `$dado 20`)
- Scegli per me: `$scegli pizza gelato patatine`
- Lancio moneta: `$coin`
- Genera password: `$password` (oppure `$password 10`)
- Emoji casuale: `$smile`
- Benvenuto: `$ciao`
- Arrivederci: `$arrivederci`"""

@bot.event
async def on_ready():
    print(f'Abbiamo fatto l\'accesso come {bot.user}')

# ---------- Lezione 3 e 4: i primi comandi ----------

# $ciao
@bot.command()
async def ciao(ctx):
    await ctx.send("Ciao!")

# $arrivederci
@bot.command()
async def arrivederci(ctx):
    await ctx.send("\U0001f642")

# $smile
@bot.command()
async def smile(ctx):
    await ctx.send(gen_emodji())

# $coin
@bot.command()
async def coin(ctx):
    await ctx.send(flip_coin())

# $password oppure $password 10 (se non scrivi la lunghezza, è 30)
@bot.command()
async def password(ctx, lunghezza: int = 30):
    await ctx.send("La tua password " + gen_pass(lunghezza))

# $comandi
@bot.command()
async def comandi(ctx):
    await ctx.send(LISTA_COMANDI)

# ---------- Compito M1L4: comandi presi dagli esempi di discord.py (basic_bot.py) ----------

# $dado oppure $dado 20 -> lancia un dado con 6 (o 20) facce
@bot.command()
async def dado(ctx, facce: int = 6):
    await ctx.send(f"🎲 È uscito {random.randint(1, facce)}!")

# $scegli pizza gelato patatine -> il bot sceglie per te
@bot.command()
async def scegli(ctx, *scelte):
    if len(scelte) == 0:
        await ctx.send("Scrivi cosa devo scegliere, per esempio: `$scegli pizza gelato`")
    else:
        await ctx.send("Scelgo... **" + random.choice(scelte) + "**!")

# ---------- Lezione M2L1: file e cartelle, il bot dei meme ----------

# $mem -> un meme a caso dalla cartella images
@bot.command()
async def mem(ctx):
    img_name = random.choice(os.listdir('images'))
    with open(f'images/{img_name}', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

# ---------- Compito M2L1: una nuova funzione, i meme hanno una rarità! ----------

# più alto è il numero, più spesso esce il meme
RARITA = {
    'mem1.webp': 45,   # comune
    'mem2.webp': 35,   # non comune
    'mem3.png': 15,    # raro
    'meme.png': 5,     # epico: l'ho fatto io!
}

# $scrigno -> apri lo scrigno: che meme ti capita?
@bot.command()
async def scrigno(ctx):
    nomi = list(RARITA.keys())
    pesi = list(RARITA.values())
    img_name = random.choices(nomi, weights=pesi)[0]
    if RARITA[img_name] <= 5:
        await ctx.send("👑 Meme **LEGGENDARIO**!")
    elif RARITA[img_name] <= 15:
        await ctx.send("💎 Meme **RARO**!")
    else:
        await ctx.send("⭐ Meme comune")
    with open(f'images/{img_name}', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

# ---------- Lezione M2L2: un link sull'inquinamento ----------

# scrivi qui il link che vuoi, tra le virgolette (per ora è vuoto)
LINK_INQUINAMENTO = "https://docs.google.com/document/d/1zU2Hqljsj7OMptlF5q1x1a39J9TekmWYZRItx7h7fM0/edit"

# $inquinamento -> manda un link con il titolo sull'inquinamento
@bot.command()
async def inquinamento(ctx):
    link = discord.Embed(
        title="🌍 How to reduce pollution",
        description="Click the title to read our tips!",
    )
    if LINK_INQUINAMENTO != "":
        link.url = LINK_INQUINAMENTO
    await ctx.send(embed=link)

# $pollution Milano -> how polluted is the air in a city (number from the internet)
@bot.command()
async def pollution(ctx, *, city: str = ""):
    if city == "":
        await ctx.send("Write a city, for example: `$pollution Rome`")
        return
    async with aiohttp.ClientSession() as session:
        # 1. find the city's position (latitude and longitude)
        async with session.get("https://geocoding-api.open-meteo.com/v1/search",
                               params={"name": city, "count": 10, "language": "it"}) as r:
            places = await r.json()
        # keep only towns and cities (not countries or regions)
        towns = [p for p in places.get("results", []) if p.get("feature_code", "").startswith("PPL")]
        if len(towns) == 0:
            await ctx.send(f"I can't find the city **{city}** 🤔")
            return
        # if many cities have this name, take the biggest one
        place = max(towns, key=lambda p: p.get("population", 0))
        # 2. ask the air quality at that position
        async with session.get("https://air-quality-api.open-meteo.com/v1/air-quality",
                               params={"latitude": place["latitude"],
                                       "longitude": place["longitude"],
                                       "current": "us_aqi"}) as r:
            air = await r.json()
    aqi = air["current"]["us_aqi"]
    if aqi is None:
        await ctx.send(f"No pollution data for **{place['name']}** right now.")
        return
    if aqi <= 50:
        level = "🟢 Good"
    elif aqi <= 100:
        level = "🟡 Moderate"
    elif aqi <= 150:
        level = "🟠 Unhealthy for sensitive people"
    elif aqi <= 200:
        level = "🔴 Unhealthy"
    elif aqi <= 300:
        level = "🟣 Very unhealthy"
    else:
        level = "🟤 Hazardous"
    await ctx.send(f"🌍 Air pollution in **{place['name']}, {place.get('country', '')}**: "
                   f"**{aqi}** US AQI → {level}")

# se il comando non esiste (o qualcosa va storto) il bot lo dice in chat
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Comando non riconosciuto.**\n" + LISTA_COMANDI)
    else:
        await ctx.send("Ops! Qualcosa non va: " + str(error))

# il token è nel file token.txt, così non finisce mai su GitHub!
if os.path.exists('token.txt'):
    with open('token.txt', 'r') as f:
        token = f.read().strip()
else:
    token = ''

if token == '':
    print('Manca il token! Incollalo nel file token.txt e riavvia il bot.')
else:
    bot.run(token)
