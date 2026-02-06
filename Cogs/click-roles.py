import discord
from discord.ext import commands

class RoleButtonView(discord.ui.View):
    def __init__(self, bot, role_map, single_role):
        super().__init__(timeout=None)
        self.bot = bot
        self.role_map = role_map 
        self.single_role = single_role
      
        for role_id, role_name in role_map.items():
            self.add_item(RoleButton(role_id, role_name, single_role))

class RoleButton(discord.ui.Button):
    def __init__(self, role_id, role_name, single_role):
        super().__init__(label=role_name, style=discord.ButtonStyle.primary)
        self.role_id = role_id
        self.single_role = single_role

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        old_role = None

        if self.single_role:
            current_roles = [button.role_id for button in self.view.children]
            assigned_roles = [r for r in member.roles if r.id in current_roles]

            if assigned_roles:
                old_role = assigned_roles[0] 
                await member.remove_roles(old_role)

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed `{role.name}`", ephemeral=True)
        else:
            await member.add_roles(role)
            if old_role:
                await interaction.response.send_message(f"🔄 Switched `{old_role.name}` → `{role.name}`", ephemeral=True)
            else:
                await interaction.response.send_message(f"✅ Added `{role.name}`", ephemeral=True)

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Reaction Role Cog Loaded!")

    @discord.app_commands.command(name="button_role", description="Create a button-based reaction role message")
    @commands.has_permissions(administrator=True)
    async def button_role(self, interaction: discord.Interaction, 
                          channel: discord.TextChannel, 
                          title: str, 
                          description: str, 
                          single_role: bool, 
                          role1: discord.Role,
                          role2: discord.Role = None,
                          role3: discord.Role = None,
                          role4: discord.Role = None,
                          role5: discord.Role = None,
                          role6: discord.Role = None,
                          role7: discord.Role = None,
                          role8: discord.Role = None,
                          role9: discord.Role = None,
                          role10: discord.Role = None,
                          role11: discord.Role = None,
                          role12: discord.Role = None,
                          role13: discord.Role = None,
                          role14: discord.Role = None,
                          role15: discord.Role = None,
                          role16: discord.Role = None,
                          role17: discord.Role = None,
                          role18: discord.Role = None,
                          role19: discord.Role = None,
                          role20: discord.Role = None):

        roles = [role1, role2, role3, role4, role5, role6, role7, role8, role9, role10, 
                 role11, role12, role13, role14, role15, role16, role17, role18, role19, role20]
        
        role_map = {role.id: role.name for role in roles if role}

        embed = discord.Embed(title=f"🎭 {title}", description=f"{description}", color=discord.Color.purple())
        embed.set_footer(text="✨ Click a button below to get your role!")
                            
        await channel.send(embed=embed, view=RoleButtonView(self.bot, role_map, single_role))
        await interaction.response.send_message(f"✅ Reaction role message sent in {channel.mention}!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
