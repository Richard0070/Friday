import discord
from discord.ext import commands
import json

class AutoThreadsButton(discord.ui.View):
    def __init__(self, bot, ctx, save_data_method):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.save_data_method = save_data_method

    @discord.ui.button(label='Configure', style=discord.ButtonStyle.primary, custom_id='config', row=1)
    async def open_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.ctx.author:
            await interaction.response.send_modal(AutoThreadsModal(self.bot, self.ctx, self.save_data_method))
        else:
            await interaction.response.send_message("You can't control these buttons!", ephemeral=True)


class AutoThreadsModal(discord.ui.Modal, title='AutoThreads Configuration'):
    def __init__(self, bot, ctx, save_data_method):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.save_data_method = save_data_method
        self.channelid = discord.ui.TextInput(label='Channel ID', required=True, style=discord.TextStyle.short)
        self.name = discord.ui.TextInput(label='Thread Name', required=True, style=discord.TextStyle.short, max_length=64)
        self.msg = discord.ui.TextInput(label='Message Content', required=False, style=discord.TextStyle.long, max_length=2000)
        self.type = discord.ui.TextInput(label='Make threads for text/media only?', required=True, style=discord.TextStyle.short, min_length=4, max_length=5, default="text", placeholder="text/media")

        self.add_item(self.channelid)
        self.add_item(self.name)
        self.add_item(self.msg)
        self.add_item(self.type)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = self.ctx.guild.id if self.ctx.guild else None

        await self.save_data_method(guild_id, self.channelid.value, self.type.value, self.name.value, self.msg.value)
        await interaction.response.send_message('Saved configuration successfully!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

    async def save_thread_data(self, server_id, channel_id, msg_type, content, thread_name):
        if not thread_name:
            thread_name = "Untitled Thread"

        thread_data = {
            "id": str(hash((server_id, channel_id, thread_name))),  # Assign a unique ID
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

        with open("threads.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_thread_data(self):
        try:
            with open("threads.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    async def save_data(self, thread_name, content, msg_type, channel_id):
        await self.save_thread_data(self.ctx.guild.id, channel_id, msg_type, content, thread_name)

    async def on_dropdown(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.channel = channel
