import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import config

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = config.KEY
        self.change_description.start()
    @app_commands.command(name="invite", description="Generate an invite link for the bot")
    async def invite(self, interaction: discord.Interaction):
        permissions = discord.Permissions(administrator=True)
        invite_link = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        await interaction.response.send_message(
            f"Boss, here is the invite link for F.R.I.D.A.Y:\n{invite_link}",
            ephemeral=True
        )

    @tasks.loop(minutes=2)
    async def change_description(self):
        new_description = "Good evening, boss."
        url = f"https://discord.com/api/v10/users/@me"
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "bio": new_description
        }
        response = requests.patch(url, headers=headers, json=payload)

async def setup(bot):
    await bot.add_cog(Misc(bot))
