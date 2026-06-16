import json
import discord
import random

from utils.economy import get, add
from games import guess as guess_game
from games import rps as rps_game
from games import flags as flags_game
from games.jokes import get_joke
from games import timecountry as tc

from cogs.blackjack import start_blackjack
from cogs.memory import start_memory
from cogs.tictactoe import start_ttt
from cogs.slots import start_slots
from cogs.flags import start_flags
from cogs.rps import start_rps

intents = discord.Intents.none()
bot = discord.Bot(intents=intents)

with open("data/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["token"]

def reward(uid, amount):
    return add(uid, amount)

@bot.slash_command()
async def coinflip(ctx):
    reward(ctx.author.id, 1)
    await ctx.respond(random.choice(["Heads", "Tails"]) + " +1💰")

@bot.slash_command()
async def joke(ctx):
    reward(ctx.author.id, 1)

    joke = await get_joke()
    await ctx.respond(joke)

@bot.slash_command()
async def fact(ctx):
    reward(ctx.author.id, 1)
    await ctx.respond("Honey never spoils")

@bot.slash_command()
async def slots(ctx):
    await start_slots(ctx)

@bot.slash_command()
async def guess(ctx, number: int):
    secret, ok = guess_game.play(number)
    reward(ctx.author.id, 3 if ok else 1)

    await ctx.respond("🎉 Correct!" if ok else f"❌ Wrong! It was {secret}")

@bot.slash_command()
async def rps(ctx, opponent: discord.Member = None):
    await start_rps(ctx, opponent)

@bot.slash_command()
async def flag(ctx):
    await start_flags(ctx)

@bot.slash_command()
async def balance(ctx):
    await ctx.respond(f"💰 {get(ctx.author.id)}")

@bot.slash_command()
async def memory(ctx):
    await start_memory(ctx)

@bot.slash_command()
async def blackjack(ctx):
    await start_blackjack(ctx)

@bot.slash_command()
async def ttt(
    ctx,
    mode: discord.Option(str, choices=["bot", "pvp"]),
    opponent: discord.Option(discord.Member, required=False)
):
    await start_ttt(ctx, mode, opponent)

bot.load_extension("cogs.time")

bot.run(TOKEN)