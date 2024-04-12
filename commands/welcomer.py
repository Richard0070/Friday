import asyncio
import discord
from discord.ext import commands
import utils.welcomerutils
from utils.welcomerutils import WelcomeBtn

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channels = utils.welcomerutils.load_welcome_channels()

    @commands.command(name='set_welcome_channel', aliases=["swc"], usage=<channel>, description="Set the welcome channel for the server.")
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        self.welcome_channels[guild_id] = channel.id
        utils.welcomerutils.save_welcome_channels(self.welcome_channels)
        await ctx.send(f'😉 Successfully set the welcome channel to {channel.mention}.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        if guild_id in self.welcome_channels:
            channel_id = self.welcome_channels[guild_id]
            channel = self.bot.get_channel(channel_id)
            if channel:
                welcome_message = f"<:ConnectionStrong:1228369799667519618> {member.mention} has connected to **The Citadel**! You're now part of Earth's elite. I'm Friday, your AI guide."
                view = WelcomeBtn(self.bot, member)
                await channel.send(welcome_message, view=view)

async def setup(bot):
    await bot.add_cog(Welcomer(bot))
