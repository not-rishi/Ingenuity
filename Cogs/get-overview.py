import discord
from discord import app_commands
from discord.ext import commands

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="overview", description="Displays an overview of the server.")
    async def serverstats(self, interaction: discord.Interaction):

        guild = interaction.guild
        owner = guild.owner

        # Member Stats
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])

        # Server Details
        created_at = guild.created_at.strftime('%d %B %Y')
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        category_count = len(guild.categories)

        # Server Boosts
        boost_count = guild.premium_subscription_count
        boosters = [member.mention for member in guild.members if member.premium_since]
        booster_list = " • ".join(boosters) if boosters else "*No Boosters 💔*"

        if boost_count >= 15:
            embed_color = discord.Color.purple()
        elif boost_count >= 5:
            embed_color = discord.Color.magenta()
        else:
            embed_color = discord.Color.gold()

        server_icon = guild.icon.url if guild.icon else None
        owner_avatar = owner.avatar.url if owner.avatar else None
        embed = discord.Embed(
            title=f"🏰 **{guild.name}** – Server Overview",
            description="╭━━━━━━━ 🌍 **Server Information** ━━━━━━━╮",
            color=embed_color
        )

        embed.set_thumbnail(url=server_icon)  
        embed.set_footer(text=f"📌 Requested by {interaction.user}", icon_url=interaction.user.avatar.url)

        # Server Owner
        embed.add_field(
            name="👑 **Owner**",
            value=f"[{owner.display_name}](https://discord.com/users/{owner.id})",
            inline=True
        )

        # Members Section
        embed.add_field(
            name="👥 **Total Members**",
            value=f"`{total_members}`",
            inline=True
        )
        embed.add_field(
            name="🟢 **Online Members**",
            value=f"`{online_members}`",
            inline=True
        )

        # Channels & Categories
        embed.add_field(
            name="💬 **Text Channels**",
            value=f"`{text_channels}`",
            inline=True
        )
        embed.add_field(
            name="🔊 **Voice Channels**",
            value=f"`{voice_channels}`",
            inline=True
        )
        embed.add_field(
            name="📂 **Categories**",
            value=f"`{category_count}`",
            inline=True
        )

        # Server Creation Date
        embed.add_field(
            name="📅 **Created On**",
            value=f"`{created_at}`",
            inline=True
        )

        # Server Boost Section
        boost_section = "╭━━━━━━ 🚀 **Boost Status** ━━━━━━╮\n"
        embed.add_field(
            name=boost_section,
            value=f"✨ **Boost Count:** `{boost_count}`\n💎 **Boosters:** {booster_list}",
            inline=False
        )
        await interaction.response.send_message(embed=embed)
async def setup(bot):
    await bot.add_cog(ServerStats(bot))
