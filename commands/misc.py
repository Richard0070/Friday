import discord
import json
from discord import app_commands
from discord.ext import commands, tasks
from config import is_owner

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_servers = self.load_allowed_servers()
        self.check_servers.start()

    def load_allowed_servers(self):
        try:
            with open('data/allowed_servers.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_allowed_servers(self):
        with open('data/allowed_servers.json', 'w') as file:
            json.dump(self.allowed_servers, file)

    @app_commands.command(name="invite", description="Generate an invite link for the bot")
    async def invite(self, interaction: discord.Interaction):
        permissions = discord.Permissions(administrator=True)
        invite_link = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        await interaction.response.send_message(
            f"Boss, here is the invite link for F.R.I.D.A.Y:\n{invite_link}",
            ephemeral=True
        )

    @commands.command(name='serverlist', aliases=['sl'], description="List all servers the bot is in.")
    @commands.has_permissions(manage_guild=True)
    async def serverlist(self, ctx):
        server_list = []
        for guild in self.bot.guilds:
            invite = await guild.text_channels[0].create_invite(max_uses=1)
            server_list.append(f"- {guild.name}, `{guild.id}` ({invite.url})")
        await ctx.send("\n".join(server_list))

    @commands.command(name='allow_server', aliases=['as'], description="Add allowed servers for the bot.")
    @commands.check(is_owner)
    async def allow_server(self, ctx, *server_ids):
        server_ids = list(map(int, server_ids))
        self.allowed_servers.extend(server_ids)
        self.allowed_servers = list(set(self.allowed_servers))
        self.save_allowed_servers()
        await ctx.send(f"Allowed servers updated. Current allowed servers: {', '.join(map(str, self.allowed_servers))}")

    @commands.command(name='unallow_server', aliases=['uas'], description="Remove servers from allowed servers.")
    @commands.check(is_owner)
    async def unallow_server(self, ctx, *server_ids):
        server_ids = list(map(int, server_ids))
        self.allowed_servers = [sid for sid in self.allowed_servers if sid not in server_ids]
        self.save_allowed_servers()
        await ctx.send(f"Removed servers. Current allowed servers: {', '.join(map(str, self.allowed_servers))}")

    @commands.command(name='leave', description="Command for the bot to leave all unallowed servers.")
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx):
        for guild in self.bot.guilds:
            if guild.id not in self.allowed_servers:
                await guild.leave()
        await ctx.send("Left all unallowed servers.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id not in self.allowed_servers:
            await guild.leave()

    @tasks.loop(minutes=10)
    async def check_servers(self):
        for guild in self.bot.guilds:
            if guild.id not in self.allowed_servers:
                await guild.leave()

async def setup(bot):
    await bot.add_cog(Misc(bot))
