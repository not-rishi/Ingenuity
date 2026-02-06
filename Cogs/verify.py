from discord.ext import commands
import discord
from discord import app_commands
import email-otp
from datastore import blacklisted_roles
import datastore
import time
import asyncio

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Verify command
    @app_commands.command(name="verify", description="Verifies your BMSCE email ID and assigns you the suitable role")
    async def verify(self, interaction: discord.Interaction, email: str):
        member = interaction.user
        role = discord.utils.get(interaction.guild.roles, name="email verified")

        if role in member.roles:
            roles_to_remove = [r for r in member.roles if r.name in blacklisted_roles]
            if roles_to_remove:
                await interaction.response.send_message(
                    "Restricted roles found, will be removed shortly.\nContact a moderator if the restricted role is still not removed.",
                    ephemeral=True
                )
                await member.remove_roles(*roles_to_remove, reason="Email verified - Removing blacklisted roles")
                return
            else:
                await interaction.response.send_message("You are already verified.", ephemeral=True)
                return

        # Send initial GIF embed
        embed = discord.Embed().set_image(url=datastore.email_sending_gif)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            # Check for valid BMSCE email
            if "@" not in email or email.split("@")[1].lower() != "bmsce.ac.in":
                await interaction.edit_original_response(
                    content="Please enter a valid @bmsce.ac.in email ID.",
                    embeds=[],
                    attachments=[]
                )
                return

            otp = email-otp.add_otp(interaction.user)
            message = """
**OTP Sent Successfully!**

An OTP has been sent to your email address. Please use the `/validate` command to enter the OTP.

**⚠️ Important:**
- The OTP will expire in **10 minutes**.
- The email may end up in the **spam** bin, please check there.

If you didn't request this OTP, please ignore this message.
"""
            if email-otp.initiate_mail(email, otp):
                embed = discord.Embed().set_image(url=datastore.email_sent_gif)
                await interaction.edit_original_response(embed=embed)
                await asyncio.sleep(4) 
                await interaction.edit_original_response(
                    content=message,
                    embeds=[],
                    attachments=[]
                )
            else:
                await interaction.edit_original_response(
                    content="Email verification service is down or has been disabled.",
                    embeds=[],
                    attachments=[]
                )

        except Exception as e:
            print(f"Error in verify: {e}")
            await interaction.edit_original_response(
                content="An error occurred. Please try again later.",
                embeds=[],
                attachments=[]
            )



  
    #Validate
    @app_commands.command(name="validate", description="Validates the OTP")
    async def validate(self,interaction: discord.Interaction, otp: str):
        await interaction.response.defer(ephemeral=True)

        message = email-otp.validate_otp(interaction.user, otp)
        member = interaction.user
        role = discord.utils.get(interaction.guild.roles, name="email verified")

        try:
            if message == "OTP has been validated and the role has been assigned.":
                flag_removed = False

                roles_to_remove = [r for r in member.roles if r.name in blacklisted_roles]
                if roles_to_remove:
                    flag_removed = True
                    await member.remove_roles(*roles_to_remove, reason="Email verified - Removing blacklisted roles")

                if role in member.roles:
                    await interaction.followup.send("You are already verified.", ephemeral=True)
                else:
                    await member.add_roles(role, reason="Email Verification - ingenuity engine")
                    if flag_removed:
                        await interaction.followup.send("OTP has been validated and the role has been assigned.\nRestricted roles were found which are now removed.", ephemeral=True)

                    await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            print(f"Error in validate: {e}")
            await interaction.followup.send("An error occurred. Please try again.", ephemeral=True)
            
async def setup(bot):
    await bot.add_cog(Verify(bot))
