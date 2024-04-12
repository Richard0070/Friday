import discord
import json
import os
from discord.ext import commands
import time
import statistics
import config

def get_prefix(bot, message):
    file_path = 'data/prefixes.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)
    try:
        with open(file_path, 'r') as f:
            prefixes = json.load(f)
    except json.JSONDecodeError:
        prefixes = {}
        with open(file_path, 'w') as f:
            json.dump(prefixes, f)
    return prefixes.get(str(message.guild.id), '!')

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name="Mr. Stark is no longer connected."))
    print(f'Logged in as {bot.user.name}')
    print('----------------------')
    await load_extensions()
    await sync_commands()

async def load_extensions():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f'Loaded {filename[:-3]}.py')
            except commands.ExtensionError as e:
                print(f'- Failed to load {filename[:-3]} Cog: {e}')

async def sync_commands():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")

@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)

@bot.command(name='setprefix', usage="<new prefix>", description="Set the bot's prefix for this server.")
@commands.has_permissions(manage_guild=True)
async def set_prefix(ctx, prefix):
    file_path = 'data/prefixes.json'
    with open(file_path, 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    with open(file_path, 'w') as f:
        json.dump(prefixes, f)
        await ctx.reply(f'Your request has been processed. The new command prefix ({prefix}) is now active. Awaiting further instructions, boss.', allowed_mentions=discord.AllowedMentions.none())

@bot.command(name='ping')
async def ping(ctx):
    shard_latency = bot.latency * 1000
    round_trip_times = []
    for _ in range(3):
        start_time = time.time()
        msg = await ctx.send('⏱️ Calculating... (1)')
        end_time = time.time()
        round_trip_time = (end_time - start_time) * 1000
        round_trip_times.append(round_trip_time)
        await msg.delete()

    lowest_round_trip_time = min(round_trip_times)
    highest_round_trip_time = max(round_trip_times)
    mean_round_trip_time = statistics.mean(round_trip_times)

    command_start_time = time.time()
    cmdmsg = await ctx.send('⏱️ Calculating... (2)')
    command_end_time = time.time()
    command_reply_time = (command_end_time - command_start_time) * 1000
    await cmdmsg.delete()

    await ctx.reply(
        f'Hello boss, here\'s the result:\n\n'
        f'- Lowest: **{lowest_round_trip_time:.2f}ms**\n'
        f'- Highest: **{highest_round_trip_time:.2f}ms**\n'
        f'- Mean: **{mean_round_trip_time:.2f}ms**\n'
        f'- Shard latency: **{shard_latency:.2f}ms**\n\n'
        f'Time between ping command and first reply: **{command_reply_time:.2f}ms**', allowed_mentions=discord.AllowedMentions.none())

bot.run(config.KEY)
