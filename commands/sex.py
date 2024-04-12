import discord
from discord import app_commands
import random
from discord.ext import commands

class Sex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sex_gifs = [
    "https://tenor.com/view/anime-hand-holding-holding-hands-gif-26896661"
        ]

    @app_commands.command(name="fuck", description="Fuck someone")
    @app_commands.describe(user="User to fuck")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        random_gif = random.choice(self.sex_gifs)
        await interaction.response.send_message(
            f"{interaction.user.mention} is fucking {user.mention}! 😳"
            f"[.]({random_gif})")

async def setup(bot):
    await bot.add_cog(Sex(bot))
    