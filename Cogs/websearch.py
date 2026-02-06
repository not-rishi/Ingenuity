import discord
from discord import app_commands
from discord.ext import commands
import requests
import datastore
import asyncio

GOOGLE_API_KEY = datastore.GOOGLE_WEB_SEARCH_API_KEY
GOOGLE_CSE_ID = datastore.CUSTOM_SEARCH_ENGINE_KEY

class WebCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def google_search(self, query):
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])[:3]  # Top 3 results
        return None

    @app_commands.command(name="websearch", description="Searches the web and returns the top results.")
    async def search_command(self, interaction: discord.Interaction, query: str):

        await interaction.response.defer(thinking=True)

        results = self.google_search(query)

        if not results:
            await interaction.followup.send("❌ No results found.", ephemeral=True)
            return

        # Typing indicator for 1 second
        async with interaction.channel.typing():
            await asyncio.sleep(1)

        response_text = f"🌐 **Search Results for:** {query}\n\n"
        response_text += "\n".join([f"{result['link']}" for result in results])  

        await interaction.followup.send(response_text)

async def setup(bot):
    await bot.add_cog(WebCog(bot))
