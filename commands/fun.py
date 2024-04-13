import discord
from discord.ext import commands
import requests
import urllib.parse
import os
from datetime import datetime
from utils.userprofileutils import create_user_info_image
from utils.nasautils import NASAButton
import aiohttp
import config

from typing import Union
from utils.emojifyutils import emojify_image, find_closest_emoji
from PIL import Image

key = config.NASA

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def generate_image(self, ctx, member: discord.Member = None):
        await ctx.message.add_reaction("<:loading:1221899453234151576>")
        r_msg = ctx.message
        if member is None:
            member = ctx.author
        user = await self.bot.fetch_user(member.id)
        image_path = await create_user_info_image(user)

        await ctx.reply(f"F.R.I.D.A.Y has generated **{member.display_name}**'s profile:", file=discord.File(image_path), allowed_mentions=discord.AllowedMentions.none())

        await r_msg.clear_reaction("<:loading:1221899453234151576>")
        
        os.remove(image_path)

    @commands.command()
    async def nasa(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.nasa.gov/planetary/apod?api_key={key}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    data = None

        embed = discord.Embed(title="Access NASA's Database", description="Explore the vast database of NASA using the interactive buttons below.\n\n>>> **APOD** displays the Astronomy Picture of the Day from NASA's API.\n\n**NeoWs (Near Earth Object Web Service)** is a RESTful web service for near earth Asteroid information.\n\n**EPIC** provides information on the daily imagery collected by DSCOVR's Earth Polychromatic Imaging Camera (EPIC) instrument.\n\nUse **NIVL** to access the NASA Image and Video Library site at images.nasa.gov.\n\n**Landsat imagery** is provided to the public as a joint project between NASA and USGS.", color=0xf4424d)
        embed.set_thumbnail(url="https://i.ibb.co/xmS3KKY/769603815783006228.png")
        view = NASAButton(self.bot, ctx)
        msg = await ctx.send(embed=embed, view=view)

    @commands.command(name='createqr')
    async def create_qrcode(self, ctx, *, data: str = None):
        if data is None:
            embed = discord.Embed(
                title="Wrong Command Usage!",
                description=
                f"Please provide data/link to generate QR code.\n\n**Command Usage:**\n`{ctx.prefix}createqr <data/link>`",
                color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        api_url = f"https://api.qrserver.com/v1/create-qr-code/?data={urllib.parse.quote(data)}"
        response = requests.get(api_url)

        if response.status_code == 200:
            with open("qrcode.png", "wb") as f:
                f.write(response.content)
            embed = discord.Embed(description="### Generated QR code:",
                                color=0xf4424d, timestamp=datetime.utcnow())
            file = discord.File("qrcode.png")
            embed.set_image(url="attachment://qrcode.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.message.reply(embed=embed, file=file, mention_author=False)
            os.remove("qrcode.png")
        else:
            embed = discord.Embed(title="Error!",
                                description="Failed to generate QR code.",
                                color=0xf4424d, timestamp=datetime.utcnow())
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command(name='readqr')
    async def read_qrcode(self, ctx, image_link: str = None):
        if image_link is None:
            embed = discord.Embed(
                title="Wrong Command Usage!",
                description=
                "Please provide data/link to generate QR code.\n\n**Command Usage:**\n`!readqr <image_link>`",
                color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        api_url = f"http://api.qrserver.com/v1/read-qr-code/?fileurl={urllib.parse.quote(image_link)}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if data and data[0] and 'symbol' in data[0] and 'data' in data[0]['symbol'][0]:
                decoded_data = data[0]['symbol'][0]['data']
                embed = discord.Embed(
                    description=f"### Decoded data from QR code:\n_ _\n```\n{decoded_data}\n```",
                    color=0xf4424d, timestamp=datetime.utcnow())
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.message.reply(embed=embed, mention_author=False)
            else:
                embed = discord.Embed(title="Error!",
                                    description="Failed to decode QR code.",
                                    color=0xf4424d, timestamp=datetime.utcnow())
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.message.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(title="Error!",
                                description="Failed to read QR code.",
                                color=0xf4424d)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command()
    async def enlarge(self, ctx, *, emoji: str):
        emoji_id = None

        if emoji.startswith(":") and emoji.endswith(":"):
            emoji_id = ctx.guild.get_emoji(int(emoji.strip(":")))
        if emoji_id:
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id.id}.png"
            await ctx.send(emoji_url)
        else:
            if len(emoji) > 1 and emoji.startswith("<:") and emoji.endswith(">"):
                emoji_id = emoji.split(":")[-1].split(">")[0]
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
                await ctx.send(emoji_url)
            else:
                await ctx.send("Invalid emoji provided.")

    @commands.command(name="emojify", usage="<user>", description="Emojify someone's avatar.")
    async def emojify(self, ctx, url: Union[discord.Member, str], size: int = 14):
        """Emojify someone's avatar."""
        if not isinstance(url, str):
            url = url.display_avatar.url

        def get_emojified_image():
            r = requests.get(url, stream=True)
            image = Image.open(r.raw).convert("RGB")
            res = emojify_image(image, size)

            if size > 14:
                res = f"```{res}```"
            return res

        result = await self.bot.loop.run_in_executor(None, get_emojified_image)
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(Fun(bot))

