from discord.ext import commands
import discord
import datastore
import asyncio
from discord import app_commands
from datetime import timedelta
import fx_helper



class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Mute Command
    @app_commands.command(name="mute", description="Mute a member for a specific duration.")
    @app_commands.describe(member="The member to mute", time="Duration (e.g., 10m, 1h, 1d)", reason="Reason for mute")
    async def mute(self,interaction: discord.Interaction, member: discord.Member, time: str, reason: str = "No reason provided"):
        if not any(role.name in datastore.ALLOWED_ROLES_ADMINISTRATIVE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        duration = fx_helper.parse_time(time)
        if duration is None:
            await interaction.response.send_message("⚠️ Invalid time format! Use `Xm`, `Xh`, or `Xd` (e.g., 10m, 1h, 1d).", ephemeral=True)
            return
        await interaction.response.defer()

        decorative_role = discord.utils.get(interaction.guild.roles, name=datastore.MUTE_ROLE_NAME)
        if decorative_role is None:
            decorative_role = await interaction.guild.create_role(name=datastore.MUTE_ROLE_NAME, color=discord.Color.dark_red())

        try:
            await member.add_roles(decorative_role, reason="Muted by command")
            await member.timeout(timedelta(seconds=duration), reason=reason)

            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member.mention}** has been muted for **{fx_helper.format_time(duration)}**.\n**Reason:** {reason}",
                color=discord.Color.red()
            )
            if interaction.user.avatar:
                embed.set_footer(text=f"Muted by {interaction.user}", icon_url=interaction.user.avatar.url)
            else:
                embed.set_footer(text=f"Muted by {interaction.user}")

            await interaction.followup.send(embed=embed)

            await fx_helper.send_log(interaction.guild, f"**{member}** was muted by **{interaction.user}** for **{fx_helper.format_time(duration)}**.\nReason: {reason}")
            await asyncio.sleep(duration)
            await member.remove_roles(decorative_role, reason="Mute duration expired")
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to mute {member.mention}. Error: {e}", ephemeral=True)

    # Unmute Command
    @app_commands.command(name="unmute", description="Unmute a member.")
    @app_commands.describe(member="The member to unmute")
    async def unmute(self,interaction: discord.Interaction, member: discord.Member):
        if not any(role.name in datastore.ALLOWED_ROLES_ADMINISTRATIVE for role in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        decorative_role = discord.utils.get(interaction.guild.roles, name=datastore.MUTE_ROLE_NAME)

        if member.timed_out_until is None or member.timed_out_until < discord.utils.utcnow():
            await interaction.response.send_message(f"ℹ️ **{member.mention}** is not currently muted.", ephemeral=True)
            return

        try:
            await member.timeout(None, reason="Unmuted by command")
            if decorative_role in member.roles:
                await member.remove_roles(decorative_role, reason="Unmuted by command")

            embed = discord.Embed(
                title="🔓 Member Unmuted",
                description=f"**{member.mention}** has been unmuted.",
                color=discord.Color.green()
            )
            if interaction.user.avatar:
                embed.set_footer(text=f"Unmuted by {interaction.user}", icon_url=interaction.user.avatar.url)
            else:
                embed.set_footer(text=f"Unmuted by {interaction.user}")


            await interaction.response.send_message(embed=embed)

            await fx_helper.send_log(interaction.guild, f"**{member}** was unmuted by **{interaction.user}**.")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unmute {member.mention}. Error: {e}", ephemeral=True)



async def setup(bot):
    await bot.add_cog(Mute(bot))
    
