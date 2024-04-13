import discord
from discord.ext import commands
from discord.ui import Select, View, Button

version = '0.2'

class Help(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.original_embed = None

  @commands.command()
  async def help(self, ctx):
    prefix = ctx.prefix

    emb = discord.Embed(
        title=
        f'Commands & Modules (Prefix: {prefix})',
        color=0xf4424d)

    emb.add_field(
        name="About",
        value=
        f"> I'm **F.R.I.D.A.Y.**, the official utility bot for **The Citadel**.",
        inline=False)
    emb.add_field(name="Library", value="> discord.py (latest)", inline=True)
    emb.set_footer(text=f"version {version}",
                   icon_url=self.bot.user.avatar.url)

    module_dropdown = ModuleDropdown(self.bot, ctx)
    view = View()
    view.add_item(module_dropdown)

    await ctx.send(embed=emb, view=view)
    self.original_embed = emb


class ModuleDropdown(Select):

  def __init__(self, bot, ctx):
    self.bot = bot
    self.ctx = ctx

    options = [discord.SelectOption(label=cog, value=cog) for cog in bot.cogs]
    super().__init__(placeholder="Select a module...", options=options)

  async def callback(self, interaction: discord.Interaction):
    selected_cog = interaction.data['values'][0]

    cog = self.bot.get_cog(selected_cog)
    if cog:
      emb = discord.Embed(title=f'{selected_cog} - Commands', color=0xf4424d)

      prefix = self.ctx.prefix
      for command in cog.walk_commands():
        if not command.hidden:
          emb.add_field(name=f"`{prefix}{command.name}`",
                        value=command.description if command.description else "No description provided.",
                        inline=False)
      self.module_embed = emb
      command_dropdown = CommandDropdown(self.ctx, self.bot, cog,
                                         self.module_embed)
      back_button = ModuleBackButton(self.bot, self.ctx)
      view = View()
      view.add_item(back_button)
      view.add_item(command_dropdown)
      await interaction.response.edit_message(embed=emb, view=view)
    else:
      emb = discord.Embed(
          title="What's that?",
          description=(
              f"I've never heard of a module called `{selected_cog}` before."),
          color=0xf4424d)

      await interaction.response.edit_message(embed=emb)


class CommandDropdown(Select):

  def __init__(self, ctx, bot, cog, module_embed):
    self.ctx = ctx
    self.bot = bot
    self.module_embed = module_embed

    options = [
        discord.SelectOption(label=command.name, value=command.name)
        for command in cog.walk_commands()
    ]
    super().__init__(placeholder="Select a command...", options=options)

  async def callback(self, interaction: discord.Interaction):
    selected_command = interaction.data['values'][0]

    command = self.bot.get_command(selected_command)

    if command:
      emb = discord.Embed(title=f'Command: {command.name}',
                          description=command.description,
                          color=0xf4424d)
      usage = command.usage if command.usage else ""
      emb.add_field(name="Usage",
                    value=f"`{self.ctx.prefix}{command.name} {usage}`"
                    if usage else f"`{self.ctx.prefix}{command.name}`",
                    inline=False)
      if command.aliases:
        emb.add_field(name="Aliases",
                      value=", ".join(command.aliases),
                      inline=False)

      back_button = CommandBackButton(self.bot, self.ctx, self.module_embed)
      view = View()
      view.add_item(back_button)

      await interaction.response.edit_message(embed=emb, view=view)
    else:
      emb = discord.Embed(
          title="Command Not Found",
          description=f"The command `{selected_command}` does not exist.",
          color=0xf4424d)
      await interaction.response.edit_message(embed=emb)


class ModuleBackButton(Button):

  def __init__(self, bot, ctx):
    super().__init__(emoji="<:denzelleft:1225291941596364852>",
                     style=discord.ButtonStyle.gray,
                     custom_id="module_back")
    self.bot = bot
    self.ctx = ctx

  async def callback(self, interaction: discord.Interaction):

    prefix = self.ctx.prefix

    emb1 = discord.Embed(
        title=
        f'Commands & Modules (Prefix: {prefix})',
        color=0xf4424d)

    emb1.add_field(
        name="About",
        value=
      f"> I'm **F.R.I.D.A.Y.**, the official utility bot for **The Citadel**.",
        inline=False)
    emb1.add_field(name="Library", value="> discord.py (latest)", inline=True)
    emb1.set_footer(text=f"version {version}",
                    icon_url=self.bot.user.avatar.url)

    view = View()
    view.add_item(ModuleDropdown(self.bot, self.ctx))
    await interaction.response.edit_message(embed=emb1, view=view)


class CommandBackButton(Button):

  def __init__(self, bot, ctx, module_embed):
    super().__init__(emoji="<:denzelleft:1225291941596364852>",
                     style=discord.ButtonStyle.gray,
                     custom_id="command_back")
    self.bot = bot
    self.ctx = ctx
    self.module_embed = module_embed

  async def callback(self, interaction: discord.Interaction):
    selected_cog = self.module_embed.title.split(" - ")[0]
    cog = self.bot.get_cog(selected_cog)

    if cog:
      command_dropdown = CommandDropdown(self.ctx, self.bot, cog,
                                         self.module_embed)
      back_button = ModuleBackButton(self.bot, self.ctx)
      view = View()
      view.add_item(back_button)
      view.add_item(command_dropdown)
      await interaction.response.edit_message(embed=self.module_embed,
                                              view=view)
    else:
      await interaction.response.edit_message(
          content="Couldn't find the module. Please try again.")


async def setup(bot):
  await bot.add_cog(Help(bot))
