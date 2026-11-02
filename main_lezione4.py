import discord
from discord.ext import commands
from bot_logic import gen_pass
from bot_logic import flip_coin
from bot_logic import gen_emodji

# la variabile intents contiene i permessi al bot
intents = discord.Intents.default()
# abilita il permesso a leggere i contenuti dei messaggi
intents.message_content = True
# crea un bot che capisce i comandi che iniziano con $
bot = commands.Bot(command_prefix='$', intents=intents)

LISTA_COMANDI = """**I comandi disponibili sono:**
- Lancio moneta: `$coin`
- Genera password: `$password` (oppure `$password 10`)
- Emoji casuale: `$smile`
- Benvenuto: `$ciao`
- Arrivederci: `$arrivederci`"""

@bot.event
async def on_ready():
    print(f'Abbiamo fatto l\'accesso come {bot.user}')

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

# se il comando non esiste (o qualcosa va storto) il bot lo dice in chat
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Comando non riconosciuto.**\n" + LISTA_COMANDI)
    else:
        await ctx.send("Ops! Qualcosa non va: " + str(error))

# incolla qui il token del tuo bot (lo stesso di main.py)
bot.run("IL TOKEN SEGRETO VA QUI")
