import os
import discord
from discord.ext import commands

async def is_owner(ctx):
    allowed_ids = [918862839316373554, 1121017074333003847]
    return ctx.author.id in allowed_ids
  
KEY = os.environ['KEY']
NASA = os.environ['NASA']