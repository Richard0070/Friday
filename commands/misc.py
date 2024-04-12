import discord
from discord import app_commands
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="invite", description="Generate an invite link for the bot")
    async def invite(self, interaction: discord.Interaction):
        permissions = discord.Permissions(administrator=True)
        invite_link = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        await interaction.response.send_message(
            f"Boss, here is the invite link for F.R.I.D.A.Y:\n{invite_link}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Misc(bot))
    