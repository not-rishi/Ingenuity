from discord.ext import commands
import discord
from discord import app_commands
import datastore


class Dm_Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def is_server_owner(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id
    
    async def is_server_owner_or_admin(interaction: discord.Interaction) -> bool:
        if interaction.user.id == interaction.guild.owner_id:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        if any(role in datastore.BOT_ADMINISTRATIVE for role in user_roles):
            return True

        return False

    
    @app_commands.command(name="dm_all", description="DM all members in a specified role.")
    @app_commands.describe(role="The role to DM", message="The message to send")
    @app_commands.check(is_server_owner)
    async def dm_all(self,interaction: discord.Interaction, role: discord.Role, message: str):
        message = message.replace("\\n", "\n")
        count = 0
        failed = 0

        await interaction.response.send_message(f"Starting to DM members in the role: {role.name}...", ephemeral=True)

        for member in role.members:
            if not member.bot: 
                try:
                    await member.send(message)
                    count += 1
                except discord.Forbidden:
                    failed += 1

        await interaction.followup.send(f"✅ Successfully sent DMs to {count} members in the role '{role.name}'. 🚫 Failed to send DMs to {failed} members.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.bot.user:
            return 

        if not datastore.auto_delete_enabled:
            return 

        if message.channel.id in datastore.exception_channels:
            return

        if any(role.name in datastore.blacklisted_roles for role in message.author.roles):
            try:
                await message.delete()
                if message.author not in datastore.cache_autodelete_userlog:
                    datastore.cache_autodelete_userlog.append(message.author)
                    await message.author.send(
                        f"Your message in {message.channel.mention} was deleted because you do not have permission to send messages there.\nPlease use /verify or contact any of the `Moderator`/`Administrator`/`Co Owner` of the Server."
                )
                print(f"Deleted message from {message.author.name} with blacklisted role.")
            except discord.Forbidden:
                print("Bot lacks permission to delete the message.")
            except discord.HTTPException as e:
                print(f"Failed to delete message: {e}")

        await self.bot.process_commands(message)


    @app_commands.command(name="toggle_autodelete", description="Enable or disable auto-deletion of messages from blacklisted roles.")
    @app_commands.check(is_server_owner_or_admin)
    async def toggle_autodelete(self,interaction: discord.Interaction):
        datastore.auto_delete_enabled = not datastore.auto_delete_enabled
        status = "enabled" if datastore.auto_delete_enabled else "disabled"
        await interaction.response.send_message(f"Auto-delete has been {status}.", ephemeral=True)


    @app_commands.command(name="add_exception_channel", description="Add a channel where messages will not be auto-deleted.")
    @app_commands.describe(channel="The channel to add as an exception.")
    @app_commands.check(is_server_owner_or_admin)
    async def add_exception_channel(self,interaction: discord.Interaction, channel: discord.TextChannel):
        if channel.id not in datastore.exception_channels:
            datastore.exception_channels.append(channel.id)
            await interaction.response.send_message(f"Added {channel.mention} to the exception list.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{channel.mention} is already in the exception list.", ephemeral=True)


    @app_commands.command(name="add_blacklisted_role", description="Add a role to the blacklist for auto-deletion.")
    @app_commands.describe(role="The role to add to the blacklist.")
    @app_commands.check(is_server_owner_or_admin)
    async def add_blacklisted_role(self,interaction: discord.Interaction, role: discord.Role):
        if role.name not in datastore.blacklisted_roles:
            datastore.blacklisted_roles.append(role.name)
            await interaction.response.send_message(f"Added `{role.name}` to the blacklist.", ephemeral=True)
        else:
            await interaction.response.send_message(f"`{role.name}` is already in the blacklist.", ephemeral=True)


    @app_commands.command(name="clear_settings", description="Clear all blacklisted roles and exception channels.")
    @app_commands.check(is_server_owner_or_admin)
    async def clear_settings(self,interaction: discord.Interaction):
        datastore.blacklisted_roles.clear()
        datastore.exception_channels.clear()
        datastore.cache_autodelete_userlog.clear()
        await interaction.response.send_message("All blacklisted roles and exception channels have been cleared.", ephemeral=True)

    @dm_all.error
    @toggle_autodelete.error
    @add_exception_channel.error
    @add_blacklisted_role.error
    @clear_settings.error
    async def on_command_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "You do not have permission to use this command. Only selected users can use it.", ephemeral=True
            )
        else:
            await interaction.response.send_message("An unexpected error occurred. Please try again.", ephemeral=True)

    

async def setup(bot):
    await bot.add_cog(Dm_Delete(bot))
