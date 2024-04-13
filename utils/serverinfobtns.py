import discord
from discord.ui import Button, View

class ViewRolesButton(View):

  def __init__(self, bot, roles):
    super().__init__(timeout=None)
    self.bot = bot
    self.roles = roles
    self.chunk_size = 2048

  @discord.ui.button(label="View Roles",
                     style=discord.ButtonStyle.blurple,
                     custom_id="view_roles")
  async def view_roles_callback(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
    roles = self.roles
    chunk_size = 2048
    max_embed_size = 6000

    sorted_roles = sorted(interaction.guild.roles,
                          key=lambda r: r.position,
                          reverse=True)

    role_mentions = [
        f"> `-` {role.mention}" for role in sorted_roles
        if role.name != "@everyone"
    ]

    embeds = []
    current_embed = discord.Embed(
        title=
        f"Roles of {interaction.guild.name} ({len(interaction.guild.roles)-1})",
        color=discord.Color.blurple())

    current_embed.description = ""
    for mention in role_mentions:
      if len(current_embed.description) + len(mention) > chunk_size or len(
          current_embed) > max_embed_size:
        embeds.append(current_embed)
        current_embed = discord.Embed(
            title=f"Roles of {interaction.guild.name} - Continued",
            color=discord.Color.blurple())
        current_embed.description = ""
      current_embed.description += mention + "\n"

    if current_embed.description:
      embeds.append(current_embed)

    for embed in embeds:
      await interaction.response.send_message(embed=embed, ephemeral=True)

  @discord.ui.button(label="View Channels",
                     style=discord.ButtonStyle.red,
                     custom_id="view_channels")
  async def view_channels_callback(self, interaction: discord.Interaction,
                                   button: discord.ui.Button):
    guild = interaction.guild

    total_channels_count = sum(
        1 for channel in guild.channels
        if not isinstance(channel, discord.CategoryChannel))

    all_channels_mentions = []

    for channel in guild.channels:
      if isinstance(channel, discord.TextChannel) and not channel.category:
        all_channels_mentions.append(f"> {channel.mention}")

    for category in guild.categories:
      all_channels_mentions.append(f"> ----------")
      for channel in category.channels:
        all_channels_mentions.append(f"> {channel.mention}")

    embed = discord.Embed(
        title=f"Channels in {interaction.guild.name} ({total_channels_count})",
        color=discord.Color.red())

    description = "\n".join(all_channels_mentions)
    embed.description = description

    await interaction.response.send_message(embed=embed, ephemeral=True)

  @discord.ui.button(label="View Emojis",
                     style=discord.ButtonStyle.green,
                     custom_id="view_emojis")
  async def view_emojis_callback(self, interaction: discord.Interaction,
                                 button: discord.ui.Button):
    guild = interaction.guild

    static_emojis = [emoji for emoji in guild.emojis if not emoji.animated]
    animated_emojis = [emoji for emoji in guild.emojis if emoji.animated]

    if not static_emojis and not animated_emojis:
      embed = discord.Embed(title="Emoji List",
                            description="This server has no emojis.",
                            color=discord.Color.green())
      await interaction.response.send_message(embed=embed, ephemeral=True)
      return

    static_emojis_chunks = self.chunk_emojis(static_emojis)
    animated_emojis_chunks = self.chunk_emojis(animated_emojis)

    static_emojis_embed = discord.Embed(
        title=f"Static Emojis ({len(static_emojis)})",
        color=discord.Color.green())
    animated_emojis_embed = discord.Embed(
        title=f"Animated Emojis ({len(animated_emojis)})",
        color=discord.Color.green())

    static_emojis_embed.description = ''
    animated_emojis_embed.description = ''

    all_static_embeds = []
    all_animated_embeds = []

    for chunk in static_emojis_chunks:
      if len(static_emojis_embed.description) + len(chunk) > self.chunk_size:
        all_static_embeds.append(static_emojis_embed)
        static_emojis_embed = discord.Embed(
            title=f"Static Emojis ({len(static_emojis)})",
            color=discord.Color.green())
        static_emojis_embed.description = ''
      static_emojis_embed.description += chunk + "\n"
    all_static_embeds.append(static_emojis_embed)

    for chunk in animated_emojis_chunks:
      if len(animated_emojis_embed.description) + len(chunk) > self.chunk_size:
        all_animated_embeds.append(animated_emojis_embed)
        animated_emojis_embed = discord.Embed(
            title=f"Animated Emojis ({len(animated_emojis)})",
            color=discord.Color.green())
        animated_emojis_embed.description = ''
      animated_emojis_embed.description += chunk + "\n"
    all_animated_embeds.append(animated_emojis_embed)

    await interaction.response.send_message(embeds=all_static_embeds +
                                            all_animated_embeds,
                                            ephemeral=True)

  def chunk_emojis(self, emojis):
    chunks = []
    current_chunk = ""
    for emoji in emojis:
      if emoji.animated:
        emoji_str = f"> {emoji} (`<a:{emoji.name}:{emoji.id}>`)\n"
      else:
        emoji_str = f"> {emoji} (`<:{emoji.name}:{emoji.id}>`)\n"
      if len(current_chunk) + len(emoji_str) > self.chunk_size:
        chunks.append(current_chunk)
        current_chunk = ""
      current_chunk += emoji_str
    if current_chunk:
      chunks.append(current_chunk)
    return chunks

