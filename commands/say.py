import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say', aliases=['speak'], description='Sends a message to a specified channel.')
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, channel: discord.TextChannel = None, *, message: str):
        if channel is None:
            channel = ctx.channel

        await channel.send(message)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Say(bot))
    