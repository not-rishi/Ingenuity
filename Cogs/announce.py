import asyncio
from discord.ext import commands
import discord
from discord import app_commands
import datastore

LOADING_GIF_URL = datastore.anime_loading  

class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Announce a message to a specific channel")
    @app_commands.describe(
        channel="The channel to send the announcement to",
        message="The message content (use \\n for new lines)",
        file1="Optional attachment 1",
        file2="Optional attachment 2",
        file3="Optional attachment 3",
        file4="Optional attachment 4",
        file5="Optional attachment 5"
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        file1: discord.Attachment = None,
        file2: discord.Attachment = None,
        file3: discord.Attachment = None,
        file4: discord.Attachment = None,
        file5: discord.Attachment = None
    ):
        message = message.replace("\\n", "\n")

        user_roles = [role.name for role in interaction.user.roles]
        if not any(role in datastore.ANNOUNCEMENT_PERMISSION for role in user_roles):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.response.send_message(
            content="Sending your announcement... please wait.",
            embed=discord.Embed().set_image(url=LOADING_GIF_URL),
            ephemeral=True
        )
        await asyncio.sleep(7)
        try:
            attachments = [file1, file2, file3, file4, file5]
            files = [await f.to_file() for f in attachments if f is not None]

            await channel.send(content=message, files=files if files else None)

            await interaction.edit_original_response(content=f"✅ Announcement sent to {channel.mention}!", embed=None)

        except Exception as e:
            print(f"Error in announce: {e}")
            await interaction.edit_original_response(content="❌ Failed to send the announcement. Please try again.", embed=None)


async def setup(bot):
    await bot.add_cog(Announce(bot))
