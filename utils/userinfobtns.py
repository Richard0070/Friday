import discord

class UserInfoBtns(discord.ui.View):

    def __init__(self, bot, target_member_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.target_member_id = target_member_id

    @discord.ui.button(label="View User Roles",
                       style=discord.ButtonStyle.green,
                       custom_id="view_user_roles")
    async def view_user_roles_callback(self, interaction: discord.Interaction,
                                       button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.target_member_id)

        sorted_roles = sorted(member.roles, key=lambda r: r.position, reverse=True)
        role_mentions = [
            f"> `-` {role.mention}" for role in sorted_roles
            if role.name != "@everyone"
        ]
        role_display = "\n".join(role_mentions)
        role_chunks = [
            role_display[i:i + 2048] for i in range(0, len(role_display), 2048)
        ]
        for chunk in role_chunks:
            embed = discord.Embed(title=f"Roles of {member.display_name}",
                                  description=chunk,
                                  color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        if not role_mentions:
            embed = discord.Embed(title=f"Roles of {member.display_name}",
                                  description="User doesn't have any roles.",
                                  color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    @discord.ui.button(label="View User Permissions",
                       style=discord.ButtonStyle.blurple,
                       custom_id="view_user_perms")
    async def view_user_perms_callback(self, interaction: discord.Interaction,
                                       button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.target_member_id)
        if not member:
            return
        permissions = "\n".join([
            f"> `-` {perm.replace('_', ' ').title()}"
            for perm, value in member.guild_permissions if value
        ])
        perm_chunks = [
            permissions[i:i + 2048] for i in range(0, len(permissions), 2048)
        ]
        for chunk in perm_chunks:
            embed = discord.Embed(title=f"Permissions of {member.display_name}",
                                  description=chunk,
                                  color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
