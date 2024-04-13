import discord
from discord.ext import commands
import shlex
from datetime import datetime
import asyncio
import re

from utils.autothreadsutils import AutoThreadsButton, AutoThreadsModal
import json
import uuid

from utils.serverinfobtns import ViewRolesButton

global_semaphore = asyncio.Semaphore(1)

class ChannelNotFound(Exception):
    pass

class InvalidDuration(Exception):
    pass

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo", aliases=["guildinfo", "guild"], description="Fetches server information.")
    @commands.has_permissions(manage_messages=True)
    async def serverinfo(self, ctx):
        """Fetches server information."""
        guild = ctx.guild

        invite_link = await guild.text_channels[0].create_invite(max_age=0,
                                                                 max_uses=0,
                                                                 unique=False)

        online_members = sum(1 for member in guild.members
                             if member.status != discord.Status.offline)

        embed = discord.Embed(title=f"Server Info", color=0xFF0000)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        if guild.description:
            embed.add_field(name="Server Description",
                            value=guild.description,
                            inline=False)
        embed.add_field(
            name="Server Owner",
            value=
            f"> {guild.owner.mention}\n> @{guild.owner.name}\n> {guild.owner.id}",
            inline=False)
        embed.add_field(name="Created At",
                        value=f"<t:{int(guild.created_at.timestamp())}:F>",
                        inline=False)

        assets_value = ""
        if guild.icon:
            assets_value += f"[Server Icon]({guild.icon.url}) "
        if guild.banner:
            assets_value += f"[Server Banner]({guild.banner.url})\n"
        if guild.splash:
            assets_value += f"[Server Splash]({guild.splash.url})\n"

        if assets_value:
            embed.add_field(name="Assets", value=assets_value, inline=False)

        embed.add_field(name="Invite Link", value=invite_link, inline=False)

        embed.add_field(name="Verification Level",
                        value=guild.verification_level,
                        inline=True)

        total_members = len(guild.members)

        bot_members = sum(member.bot for member in guild.members)

        human_members = total_members - bot_members

        member_counter = f"> Total Members: {total_members}\n> Humans: {human_members}\n> Bots: {bot_members}"

        embed.add_field(name="Members", value=member_counter, inline=True)

        online_members = sum(1 for member in guild.members
                             if member.status == discord.Status.online)
        idle_members = sum(1 for member in guild.members
                           if member.status == discord.Status.idle)
        dnd_members = sum(1 for member in guild.members
                          if member.status == discord.Status.dnd)
        offline_members = sum(1 for member in guild.members
                              if member.status == discord.Status.offline)

        member_status = f"> Online: {online_members}\n> Idle: {idle_members}\n> Do Not Disturb: {dnd_members}\n> Offline: {offline_members}"

        embed.add_field(name="Member Status", value=member_status, inline=True)

        if guild.premium_subscription_count > 0:
            embed.add_field(
                name="Boost Information",
                value=
                f"Boosts: {guild.premium_subscription_count}\nBooster Tier: {guild.premium_tier}",
                inline=False)

        embed.add_field(name="Role Count", value=(len(guild.roles) - 1))
        danger_roles_mentions = [
            f"> {role.mention}"
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True)
            if role.permissions.administrator
        ]

        if danger_roles_mentions:
            embed.add_field(name="Dangerous Roles",
                            value="\n".join(danger_roles_mentions),
                            inline=True)
        embed.add_field(
            name="Channels",
            value=
            f"> Categories: {len(guild.categories)}\n> Text Channels: {len(guild.text_channels)}\n> Voice Channels: {len(guild.voice_channels)}",
            inline=True)
        static_emojis = sum(1 for emoji in guild.emojis if not emoji.animated)
        animated_emojis = sum(1 for emoji in guild.emojis if emoji.animated)
        sticker_count = len(guild.stickers)

        embed.add_field(
            name="Emote Count",
            value=
            f"> Static Emojis: {static_emojis}\n> Animated Emojis: {animated_emojis}\n> Stickers: {sticker_count}",
            inline=True)

        features = []

        if guild.features:
            for feature in guild.features:
                formatted_feature = feature.replace("_", " ").title()
                features.append(f"> {formatted_feature}")

        if features:
            embed.add_field(name="Server Features",
                            value="\n".join(features),
                            inline=False)

        message = await ctx.send(embed=embed,
                                 view=ViewRolesButton(self.bot, guild.roles))

    @commands.command(name="inviteinfo", aliases=["invinfo"], usage="<invite>" , description="Shows information about an invite.")
    @commands.has_permissions(manage_messages=True)
    async def inviteinfo(self, ctx, invite: discord.Invite):
        """Shows Information about an invite"""
        try:
            invite = await self.bot.fetch_invite(invite)
        except discord.errors.NotFound:
            await ctx.send("Invalid invite.")
            return

        embed = discord.Embed(title="Invite Information", color=0xf4424d)
        embed.add_field(name="Invite Code", value=invite.code)

        if invite.inviter:
            embed.add_field(name="Inviter", value=f"{invite.inviter.mention}, {invite.inviter.name} ({invite.inviter.id})")

        if invite.expires_at:
            embed.add_field(name="Expires At", value=f"<t:{int(invite.expires_at.timestamp())}:F>")
        else:
            embed.add_field(name="Expires At", value="Never")

        if invite.created_at:
            embed.add_field(name="Created At", value=f"<t:{int(invite.created_at.timestamp())}:F>")

        if invite.uses is not None:
            embed.add_field(name="Uses", value=invite.uses)

        if invite.max_uses is not None:
            embed.add_field(name="Max Uses", value=invite.max_uses)

        embed.add_field(name="Channel", value=f">>> **Name:** #{invite.channel.name}\n**ID:** {invite.channel.id}\n**Created At:** <t:{int(invite.channel.created_at.timestamp())}:F>" if invite.channel else "Unknown Channel")

        if invite.guild:
            embed.add_field(name="Guild", value=f">>> **Name:** {invite.guild.name}\n**ID:** {invite.guild.id}\n**Created At:** <t:{int(invite.guild.created_at.timestamp())}:F>")

            if invite.guild.icon:
                embed.set_thumbnail(url=invite.guild.icon.url)
        else:
            embed.add_field(name="Guild", value="Direct Message")

        await ctx.send(embed=embed)


    @commands.command(name="slowmode", usage="<channel> <duration>" , description="Sets the slowmode for a channel.")
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self,
                       ctx,
                       channel: discord.TextChannel = None,
                       *duration: str):
        """Sets the slowmode for a channel"""
        if channel is None:
            channel = ctx.channel

        current_slowmode = getattr(channel, 'slowmode_delay', 0)

        if not duration:
            if current_slowmode == 0:
                embed = discord.Embed(
                    title=None,
                    description=f"There is no slowmode in {channel.mention}.",
                    color=0xf4424d)
            else:
                embed = discord.Embed(
                    title=None,
                    description=
                    f"The current slowmode in {channel.mention} is: **{self.format_seconds(current_slowmode)}.**",
                    color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        if duration[0].lower() in ["off", "none", "zero", "remove"]:
            await channel.edit(slowmode_delay=0)
            embed = discord.Embed(
                title=None,
                description=f"Slowmode removed in {channel.mention}.",
                color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)')
        matches = pattern.findall(''.join(duration))

        if not matches:
            embed = discord.Embed(
                title=None,
                description=
                "⚠️ Please use a valid duration format!\nExample- 5s, 15 mins, 5h (you can use combination of these too.)",
                color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        total_seconds = 0

        for value, unit in matches:
            value = int(value)

            if unit.lower() in ['s', 'sec', 'secs', 'second', 'seconds']:
                total_seconds += value
            elif unit.lower() in ['m', 'min', 'mins', 'minute', 'minutes']:
                total_seconds += value * 60
            elif unit.lower() in ['h', 'hour', 'hours']:
                total_seconds += value * 3600
            else:
                raise InvalidDuration()

        if total_seconds < 0 or total_seconds > 21600:
            embed = discord.Embed(
                title=None,
                description="⚠️ Duration must be between 0 seconds and 6 hours!",
                color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        prev_slowmode = current_slowmode
        await channel.edit(slowmode_delay=total_seconds)

        formatted_time = self.format_seconds(total_seconds)

        embed = discord.Embed(
            title=None,
            description=
            f"Slowmode of {channel.mention} set from **{self.format_seconds(prev_slowmode)}** to **{formatted_time}**",
            color=0xf4424d)
        await ctx.message.reply(embed=embed, mention_author=False)

    def format_seconds(self, total_seconds):
        if total_seconds == 0:
            return "0 second"

        hours = total_seconds // 3600
        total_seconds %= 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        formatted_time = ""
        if hours > 0:
            formatted_time += f"{hours} hour{'s' if hours > 1 else ''}"
        if minutes > 0:
            formatted_time += f" {minutes} minute{'s' if minutes > 1 else ''}"
        if seconds > 0:
            formatted_time += f" {seconds} second{'s' if seconds > 1 else ''}"
        return formatted_time.strip()

    @commands.command(name="slowmodes", description="Shows the slowmodes of all channels.")
    @commands.has_permissions(manage_messages=True)
    async def slowmodes(self, ctx):
        """Shows the slowmodes of all channels"""
        slowmode_channels = [
            channel for channel in ctx.guild.channels
            if isinstance(channel, discord.TextChannel)
            and getattr(channel, 'slowmode_delay', 0) > 0
        ]

        if not slowmode_channels:
            embed = discord.Embed(title=None,
                                  description="‼️ No channels have slowmode enabled.",
                                  color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
            return

        description = ""
        for channel in slowmode_channels:
            description += f"> {channel.mention} has a slowmode of **{self.format_seconds(getattr(channel, 'slowmode_delay', 0))}**.\n"

        embed = discord.Embed(title="Channels with Slowmode Enabled",
                              description=description,
                              color=0xf4424d)

        await ctx.message.reply(embed=embed, mention_author=False)

    @slowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, ChannelNotFound):
            embed = discord.Embed(title=None,
                                  description="⚠️ The specified channel was not found.",
                                  color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)
        elif isinstance(error, InvalidDuration):
            embed = discord.Embed(title=None,
                                  description="⚠️ Invalid duration term provided.",
                                  color=0xf4424d)
            await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command(name="idinfo", aliases=["id"], usage= "<id>" , description="Shows information about an ID.")
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def id_info(self, ctx, id_value: str):
        """Shows information about an ID"""
        if not id_value.isdigit():
            await ctx.send("⚠️ Invalid ID format. Please provide a valid integer ID.")
            return

        async with global_semaphore:
            try:
                id_value = int(id_value)

                message = await ctx.channel.fetch_message(id_value)
                if message:
                    id_type = "Message ID"
                    created_at = message.created_at
                    description = f"This is a **{id_type}** created on <t:{int(message.created_at.timestamp())}:F>."
                    embed = discord.Embed(title="⚗️ ID Information", description=description, color=0xf4424d)
                    await ctx.send(embed=embed)
                    return

            except discord.errors.NotFound:
                pass

            try:
                channel = self.bot.get_channel(id_value)
                if channel:
                    id_type = "Channel ID"
                    created_at = channel.created_at
                    description = f"This is a **{id_type}** created on <t:{int(channel.created_at.timestamp())}:F>."
                    embed = discord.Embed(title="⚗️ ID Information", description=description, color=0xf4424d)
                    await ctx.send(embed=embed)
                    return

            except discord.errors.NotFound:
                pass

            try:
                server = self.bot.get_guild(id_value)
                if server:
                    id_type = "Server ID"
                    created_at = server.created_at
                    description = f"This is a **{id_type}** created on <t:{int(server.created_at.timestamp())}:F>."
                    embed = discord.Embed(title="⚗️ ID Information", description=description, color=0xf4424d)
                    await ctx.send(embed=embed)
                    return

            except discord.errors.NotFound:
                pass

            try:
                user = await self.bot.fetch_user(id_value)
                if user:
                    id_type = "User ID"
                    description = f"This is a **{id_type}** created on <t:{int(user.created_at.timestamp())}:F>."
                    embed = discord.Embed(title="⚗️ ID Information", description=description, color=0xf4424d)
                    await ctx.send(embed=embed)
                    return

            except discord.errors.NotFound:
                pass

            try:
                role = await ctx.guild.get_role(id_value)
                if role:
                    id_type = "Role ID"
                    description = f"This is a **{id_type}** created on <t:{int(role.created_at.timestamp())}:F>."
                    embed = discord.Embed(title="⚗️ ID Information", description=description, color=0xf4424d)
                    await ctx.send(embed=embed)
                    return

            except discord.errors.NotFound:
                pass

            await ctx.send("⚠️ Unable to find information for the provided ID.")

    @id_info.error
    async def id_info_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction("⏱️")
            await ctx.send(f"You're on cooldown. Please wait **{round(error.retry_after)} second(s)** before using this command again.")
            await self.clean_up(ctx)

    async def clean_up(self, ctx):
        await asyncio.sleep(3)
        await ctx.message.delete()
        async for msg in ctx.channel.history(limit=1):
            if msg.author == self.bot.user:
                await msg.delete()

    async def display_results(self, ctx, results, page):
        per_page = 15
        total_pages = (len(results) + per_page - 1) // per_page
        start_index = (page - 1) * per_page
        end_index = min(start_index + per_page, len(results))

        if not results:
            embed = discord.Embed(description="⚠️ No members found.", color=0xf4424d)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title=f"Search Results (Page {page}/{total_pages})", color=0xf4424d)
        for member in results[start_index:end_index]:
            embed.add_field(name=f"{member.name}#{member.discriminator}", value=f"{member.id} | {member.mention}", inline=False)

        message = await ctx.send(embed=embed)

        if total_pages > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                return

            if str(reaction.emoji) == "⬅️" and page > 1:
                await message.delete()
                await self.display_results(ctx, results, page - 1)
            elif str(reaction.emoji) == "➡️" and page < total_pages:
                await message.delete()
                await self.display_results(ctx, results, page + 1)
            else:
                await message.clear_reactions()

    @commands.command(name="search", aliases=["find", "s"], usage="<query> <page>", description="Search for a member by name or ID.")
    @commands.has_permissions(manage_messages=True)
    async def search(self, ctx, *, query_and_page: str = None):
        """Search for a member by name or ID"""
        if query_and_page is None:
            await ctx.send(f"Please provide a query to search for. Example: `{ctx.prefix}search <query>`")
            return

        query, *page_str = query_and_page.split()

        page = int(page_str[0]) if page_str else 1
        search_message = await ctx.send("Searching 🔎")

        args = shlex.split(query)

        matching_members = ctx.guild.members

        matching_members = [member for member in matching_members if query.lower() in member.name.lower() or query.lower() in member.display_name.lower()]

        await asyncio.sleep(2)
        await search_message.delete()

        await self.display_results(ctx, matching_members, page)


    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if message.author == self.bot.user:
            return

        if not message.channel.permissions_for(message.guild.me).manage_threads:
            return

        await self.create_thread_from_message(message)

    async def create_thread_from_message(self, message):
        thread_data = self.load_thread_data()
        for data in thread_data:
            if str(message.guild.id) == data["server_id"] and str(message.channel.id) == data["channel_id"]:
                if data["msg_type"] == "text":
                    thread = await message.create_thread(name=data["thread_name"])
                    if data["content"] != "":
                        await thread.send(data["content"])

                elif data["msg_type"] == "media":
                    if message.attachments:
                        thread = await message.create_thread(name=data["thread_name"])
                        if data["content"] != "":
                            await thread.send(content=data["content"])
                    else:
                        return

    @commands.command(name="autothread", description="Create threads automatically to messages sent in a specific channel.")
    @commands.has_permissions(manage_channels=True)
    async def autothread(self, ctx):
        """Create threads automatically to messages sent in a specific channel."""
        view = AutoThreadsButton(self.bot, ctx, self.save_thread_data)
        await ctx.reply("Configure your AutoThreads! Set channel ID, thread name, message content and type.", view=view, allowed_mentions=discord.AllowedMentions.none())

    async def save_thread_data(self, server_id, channel_id, msg_type, thread_name, content):
        thread_data = {
            "id": str(uuid.uuid4())[:8],  # Shorter unique ID
            "server_id": str(server_id),
            "channel_id": str(channel_id),
            "msg_type": msg_type,
            "content": content,
            "thread_name": thread_name
        }

        data = self.load_thread_data()
        updated = False
        for entry in data:
            if entry["server_id"] == str(server_id) and entry["channel_id"] == str(channel_id):
                entry.update(thread_data)
                updated = True
                break

        if not updated:
            data.append(thread_data)

        with open("data/threads.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_thread_data(self):
        try:
            with open("data/threads.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @commands.command(name="autothreads", description="List all configured AutoThreads.")
    @commands.has_permissions(manage_channels=True)
    async def autothreads(self, ctx):
        """List all configured AutoThreads."""
        data = self.load_thread_data()
        embeds = []

        # Filter data based on server ID where the command was run
        data = [entry for entry in data if entry['server_id'] == str(ctx.guild.id)]

        # Creating embeds for each page
        for i in range(0, len(data), 10):
            embed = discord.Embed(title="AutoThreads", color=0xf4424d)
            for entry in data[i:i + 10]:
                embed.add_field(name=f"ID: {entry['id']}", value=f"Channel ID: {entry['channel_id']}\nThread Name: {entry['thread_name']}\nType: {entry['msg_type']}", inline=False)
            embeds.append(embed)

        # Pagination logic
        if embeds:
            current_page = 0
            msg = await ctx.send(embed=embeds[current_page])

            # Reaction check
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

            # Add reactions
            await msg.add_reaction('⬅️')
            await msg.add_reaction('➡️')

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                    if str(reaction.emoji) == '➡️' and current_page < len(embeds) - 1:
                        current_page += 1
                        await msg.edit(embed=embeds[current_page])
                    elif str(reaction.emoji) == '⬅️' and current_page > 0:
                        current_page -= 1
                        await msg.edit(embed=embeds[current_page])

                    await msg.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    break

    @commands.command(name="autothreaddelete", aliases=["autothreaddel", "autothreadremove", "autothreadrm"], description="Delete an AutoThread by its ID.")
    @commands.has_permissions(manage_channels=True)
    async def delete_autothread(self, ctx, id: str):
        """Deletes an AutoThread by its ID."""
        data = self.load_thread_data()
        deleted = False

        for i, entry in enumerate(data):
            if entry['id'] == id:
                del data[i]
                deleted = True
                break

        if deleted:
            with open("data/threads.json", "w") as file:
                json.dump(data, file, indent=4)
            await ctx.send(f"Autothread with ID {id} has been deleted.")
        else:
            await ctx.send("Autothread not found with the given ID.")

    @commands.command(name="membercount", aliases=["members", "memberscount"], description="Get the member count of the server.")
    async def membercount(self, ctx):
        """Get the member count of the server."""
        total_members = ctx.guild.member_count
        total_bots = len([m for m in ctx.guild.members if m.bot])
        total_humans = total_members - total_bots
        online = len([m for m in ctx.guild.members if m.status == discord.Status.online])
        offline = len([m for m in ctx.guild.members if m.status == discord.Status.offline])
        idle = len([m for m in ctx.guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in ctx.guild.members if m.status == discord.Status.dnd])
        
        embed = discord.Embed(title="Member Count", description=f"**{total_humans} humans + {total_bots} bots = {total_members} members**\n\n<:online:1214806655766761482> **Online:** {online}\n<:idle:1214806735437697054> **Idle:** {idle}\n<:dnd:1214806804429807646> **DND:** {dnd}\n<:offline:1214807068574355467> **Offline:** {offline}", color=0xf4424d)

        
        await ctx.send(embed=embed)

async def setup(bot):
  await bot.add_cog(Utility(bot))
