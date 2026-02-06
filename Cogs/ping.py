from discord.ext import commands
import discord
from discord import app_commands
import asyncio
import datastore
import time
import time-parser

def create_purple_progress_bar(latency, max_latency=500):
    bar_length = 10
    filled_blocks = int(((max_latency-latency) / max_latency) * bar_length)
    filled_blocks = min(filled_blocks, bar_length) 

    gradient = ["🟪", "🟨", "🟥", "⬛"]
    progress_bar = ""

    for i in range(bar_length):
        if i < filled_blocks:
            if latency < 150:
                progress_bar += gradient[0]  # Light Purple
            elif latency < 300:
                progress_bar += gradient[1]  # Medium Purple
            elif latency < 450:
                progress_bar += gradient[2]  # Dark Purple
            else:
                progress_bar += gradient[3]  # Black 
        else:
            progress_bar += "⬛"  # Empty block

    return progress_bar
        


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="ping", description="Check the bot's ping.")
    async def ping(self,interaction: discord.Interaction):
        api_start = time.time()
        embed = discord.Embed().set_image(url=datastore.ping_loading_gif)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)

        # Compute uptime & latency
        uptime_str = time-parser.get_uptime()
        latency = round(self.bot.latency * 1000)  # Convert to ms
        progress_bar = create_purple_progress_bar(latency)

        # Determine latency status
        if latency < 100:
            status = "💜 Ultra Fast"
        elif latency < 250:
            status = "🔮 Smooth"
        elif latency < 400:
            status = "🟣 Lagging"
        else:
            status = "🖤 Critical"

        # Create the final ping embed
        embed = discord.Embed(
            title="🔮 **Ping!**",
            description="",
            color=0x800080
        )
        embed.add_field(name="⏳ **Service running for** 🔻", value=f"```{uptime_str}```",inline=False)
        embed.add_field(name="🛰️ **API Response Latency** 🔻",value=f"```{((time.time()-api_start)*1000):.0f}ms```",inline=False)
        embed.add_field(name="📡 **WebSocket Latency**  🔻", value=f"```{latency}ms | {status}```", inline=False)
        embed.add_field(name="📶 **Latency Bar** 🔻", value=f"```{progress_bar}```", inline=False)

        if interaction.client.user.avatar:
            icon_url = interaction.client.user.avatar.url
        else:
            icon_url = None

        embed.set_footer(text=" Powered by Ingenuity", icon_url=icon_url)
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))

