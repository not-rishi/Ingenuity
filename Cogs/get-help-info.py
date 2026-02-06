import discord
import platform
import time
from discord.ext import commands
from discord import app_commands
import psutil
import os

start_time = time.time()

class InfoHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Help
    @app_commands.command(name="help", description="Displays a list of available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 **Available Commands**",
            description="Here’s what you can do:",
            color=discord.Color.purple()
        )

        embed.set_thumbnail(url=interaction.client.user.avatar.url if interaction.client.user.avatar else None)

        # Verification Commands
        embed.add_field(
            name="🔹 **Verification**",
            value="🔹 `/verify <email>` - Sends an OTP to your **@bmsce.ac.in** email.\n"
                  "🔹 `/validate <otp>` - Validates OTP and completes verification.",
            inline=False
        )

        # Sniping Command
        embed.add_field(
            name="🔹 **Message Recovery**",
            value="🔹 `/snipe` - Retrieves the last deleted message or image.",
            inline=False
        )

        # Utility Commands
        embed.add_field(
            name="🔹 **Utilities**",
            value="🔹 `/ping` - Check bot latency and system details.\n"
                  "🔹 `/get_status_info` - Checks if any commands have errors.\n"
                  "🔹 `/overview` - Server stats (members, owner, boosts, etc.).\n"
                  "🔹 `/info` - Displays information of developer,host system and language used.",
            inline=False
        )

        # Extra Commands
        embed.add_field(
            name="🔹 **Extras**",
            value="🔹 `@Bot_Mention` - Ask the bot anything by tagging it! (Use at your own risk 😈)\n"
                  "🔹 `/websearch` - Searches the web and returns the top results.\n"
                  "🔹 `/leaderboard` - Shows the member list of the server based on the joining date.\n"
                  "🔹 `/search_faculty` - Scrapes the college website and shows faculty data in a autocomplete search bar format (quick).\n"
                  "🔹 `/show_faculty_list` - Scrapes the college website and shows faculty data in a navigable system of drop-down lists.\n"
                  "🔹 `/get_rank` - Searches and gives the joining rank of the particular user.",
            inline=False
        )

        bot_commands_channel_id = 1280838038976725042
        embed.add_field(
            name="⚠️ **Where to Use Commands?**",
            value=f"🔹 Please use all commands in <#{bot_commands_channel_id}>.",
            inline=False
        )

        icon_url = interaction.client.user.avatar.url if interaction.client.user.avatar else None
        embed.set_footer(text="Use commands with `/` prefix. Happy commanding! 🚀", icon_url=icon_url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Info Command
    @app_commands.command(name="info", description="Shows detailed information about the bot.")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        uptime = time.time() - start_time
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
        latency = round(self.bot.latency * 1000)  

        developer_id = 1279851915596922941
        try:
            developer = await interaction.client.fetch_user(developer_id)
            developer_name = developer.name
            developer_link = f"[{developer_name}](https://discord.com/users/{developer_id})"
        except:
            developer_link = "Developer profile not found."

        process = psutil.Process(os.getpid())
        mem_usage_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_total = round(psutil.virtual_memory().total / (1024 ** 2), 2)

        embed = discord.Embed(
            title="🤖 **Bot Information**",
            description="Here’s everything you need to know:",
            color=discord.Color.gold()
        )

        embed.add_field(name="📌 **Bot Name**", value=f"```{self.bot.user.name}```", inline=True)
        embed.add_field(name="🆔 **Bot ID**", value=f"```{self.bot.user.id}```", inline=True)
        embed.add_field(name="🌍 **Servers**", value=f"```{len(self.bot.guilds)}```", inline=True)
        embed.add_field(name="👥 **Users**", value=f"```{sum(guild.member_count for guild in self.bot.guilds)}```", inline=True)
        embed.add_field(name="🛠️ **Commands**", value=f"```{len(self.bot.tree.get_commands())}```", inline=True)
        embed.add_field(name="🧠 **Memory Retainment**", value=f"```🕒 {uptime_str}```", inline=True)
        embed.add_field(name="📶 **Ping**", value=f"```⚡ {latency}ms```", inline=True)
        embed.add_field(name="⚙️ **Library**", value="```discord.py```", inline=True)
        embed.add_field(name="🐍 **Python Version**", value=f"```{platform.python_version()}```", inline=True)
        embed.add_field(name="🖥 **Host System**", value=f"```{platform.system()} {platform.release()}```", inline=True)
        embed.add_field(name="👤 **Developer**", value=developer_link, inline=True)
        embed.add_field(name="💾 **RAM Usage**", value=f"```{mem_usage_mb} MB / {ram_total} MB```", inline=True)
        embed.add_field(name="⚡ **CPU Usage**", value=f"```{cpu_percent}%```", inline=True)

        icon_url = self.bot.user.avatar.url if self.bot.user.avatar else None
        embed.set_footer(text="Powered by Ingenuity", icon_url=icon_url)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InfoHelp(bot))

