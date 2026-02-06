import discord
from discord import app_commands
from discord.ext import commands
import datastore

# BOT_ADMINISTRATIVE = ["Owner", "Co Owner"]

class TokenCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="update_token", description="Store/Update a refresh token securely.")
    async def set_token(self, interaction: discord.Interaction, token: str):
        if self.has_bot_administrative_permission(interaction.user):
            token = token.strip()
            datastore.COMMAND_ACCEPTED_REFRESH_TOKEN = token
            await interaction.response.send_message(
                "Refresh token stored successfully.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ You do not have permission to set the refresh token.", ephemeral=True
            )

    @app_commands.command(name="display_token", description="Get the stored refresh token.")
    async def get_token(self, interaction: discord.Interaction):
        if self.has_bot_administrative_permission(interaction.user):
            token = datastore.COMMAND_ACCEPTED_REFRESH_TOKEN
            if token:
                await interaction.response.send_message(
                    f"Stored token: {token}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "No token stored.", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ You do not have permission to view the refresh token.", ephemeral=True
            )

    @app_commands.command(name="clear_token", description="Clear the stored refresh token.")
    async def clear_token(self, interaction: discord.Interaction):
        if self.has_bot_administrative_permission(interaction.user):
            datastore.COMMAND_ACCEPTED_REFRESH_TOKEN = None
            await interaction.response.send_message(
                "Refresh token cleared successfully.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ You do not have permission to clear the refresh token.", ephemeral=True
            )

    def has_bot_administrative_permission(self, user: discord.User) -> bool:
        """Check if the user has one of the roles in the global BOT_ADMINISTRATIVE list."""
        if isinstance(user, discord.Member):
            # Accessing the global BOT_ADMINISTRATIVE list here
            from datastore import BOT_ADMINISTRATIVE
            return any(role.name in BOT_ADMINISTRATIVE for role in user.roles)
        return False

async def setup(bot: commands.Bot):
    await bot.add_cog(TokenCog(bot))
