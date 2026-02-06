import discord
from discord import app_commands
from discord.ext import commands
import requests
import random
import google.generativeai as genai
from collections import deque
import datastore  

GEMINI_API_KEY = datastore.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


async def get_display_name(guild, user_id):
    try:
        member = await guild.fetch_member(user_id)
        return member.display_name 
    except Exception:
        return "Unknown User"


class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.friends = [1279851915596922941]
        self.chat_history = {}
        self.bot_reply_ids = deque(maxlen=750)



    @staticmethod
    async def is_server_owner_or_admin(interaction: discord.Interaction) -> bool:
        if interaction.user.id == interaction.guild.owner_id:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in datastore.BOT_ADMINISTRATIVE for role in user_roles)

    async def generate_ai_response(self, prompt, user_id, user_name):
        model = datastore.reply_model
        prompt = prompt.replace(f"<@{self.bot.user.id}>", "").strip()
        if model == "gemini":
            return self.use_gemini(prompt, user_id,user_name)
        elif model == "mistral":
            return self.use_mistral(prompt)
        else:
            return "I have been instructed to keep my mouth shut for the time being."

    def use_gemini(self, prompt, user_id, user_name):
        if datastore.PERSONA == "hybris":
            instructions = """Instructions 1"""
        elif datastore.PERSONA == "eros":
            instructions = """Instructions 2"""
        elif datastore.PERSONA == "athena":
            instructions = """Instructions 3"""
        else:
            if (int(user_id)) in self.friends:
                instructions = "Friendly Instructions"
            else:
                instructions = "Default Instructions"

        history = self.chat_history.get(user_id, deque())
        history_prompt = "\n".join(history)
        full_prompt = f"{instructions}\n Here is the history of your previous chat use it as a reference:{history_prompt}\n the person interacting with you is named {user_name} \n User: {prompt}\nAI:"

        try:
            response = gemini_model.generate_content(full_prompt)
            return response.text if response else "⚠️ No response from AI model."
        except:
            return "I have been instructed to keep my mouth shut for the time being."

    def use_mistral(self, prompt):
        try:
            API_URL = datastore.MISTRAL_API_URL
            MISTRAL_API_KEY = datastore.MISTRAL_API_KEY
            HEADERS = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            formatted_prompt = f"### Instruction:\nYou are a helpful bot. Answer briefly and accurately.\n\n### User:\n{prompt}\n\n### Assistant:\n"

            response = requests.post(API_URL, headers=HEADERS, json={"inputs": formatted_prompt})
            data = response.json()

            if isinstance(data, dict) and "error" in data:
                return "⚠️ Error: " + data["error"]
            return data[0]["generated_text"].split("### Assistant:\n")[-1].strip() if data else "⚠️ No response from Mistral."
        except:
            return "I have been instructed to keep my mouth shut for the time being."
        return "Current Model has expanded from 14 GB and cannot be hosted so no response was generated."

    async def send_typing_reply(self, message, response):
        async with message.channel.typing():
           sent_msg = await message.reply(response)
           self.bot_reply_ids.append(sent_msg.id)


  
    @app_commands.command(name="ai_loves", description="Add a user as an special user (test purpose only).")
    @app_commands.check(is_server_owner_or_admin)
    async def add_friends(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        try:
            if user.id not in self.friends:
                self.friends.append(user.id)
                await interaction.followup.send(f"User {user.display_name} has been added as an special user!", ephemeral=True)
            else:
                await interaction.followup.send(f"User {user.display_name} is already an special user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An internal error occurred: {e}", ephemeral=True)
    @app_commands.command(name="ai_does_not_loves", description="removes the user from special program (test purpose only).")
    @app_commands.check(is_server_owner_or_admin)
    async def remove_friends(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        try:
            if user.id not in self.friends:
                await interaction.followup.send(f"No user named {user.display_name} found in special program!", ephemeral=True)
            else:
                self.friends.remove(user.id)
                await interaction.followup.send(f"User {user.display_name} has been removed from special program.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An internal error occurred: {e}", ephemeral=True)


    @app_commands.command(name="view_persona", description="Displays the current persona of the bot")
    async def view_persona(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if datastore.PERSONA == "hybris":
            persona_description = ""
            persona_colour = discord.Color.gold()
            persona_title = "AI Persona Overview : Hybris"
        elif datastore.PERSONA == "eros":
            persona_description = ""
            persona_colour = discord.Color.gold()
            persona_title = "AI Persona Overview : Eros"
        elif datastore.PERSONA == "richie":
            persona_description = ""
            persona_colour = discord.Color.gold()
            persona_title = "AI Persona Overview : Richie"
        else:
            persona_description = ""
            persona_colour = discord.Color.gold()
            persona_title = "AI Persona Overview : Athena"

        embed = discord.Embed(title=persona_title, description=persona_description, color=persona_colour)
        embed.set_image(url="")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="change_persona", description="Switch between Eros, Hybris, Athena and Richie")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Eros - flirty", value="eros"),
        app_commands.Choice(name="Athena - wise", value="athena"),
        app_commands.Choice(name="Hybris - arrogant", value="hybris"),
        app_commands.Choice(name="Richie - spoiled", value="richie"),
    ])
    @app_commands.check(is_server_owner_or_admin)
    async def change_persona(self, interaction: discord.Interaction, persona: app_commands.Choice[str]):
        datastore.PERSONA = persona.value
        await interaction.response.send_message(f"🧙🏻‍♀️↔️🧙‍♂️ Persona switched to **{persona.name}**.", ephemeral=True)

    @app_commands.command(name="toggle_reply_model", description="Switch between Gemini, Mistral, or disable AI replies.")
    @app_commands.choices(model=[
        app_commands.Choice(name="Gemini", value="gemini"),
        app_commands.Choice(name="Mistral", value="mistral"),
        app_commands.Choice(name="Disabled", value="disabled"),
    ])
    @app_commands.check(is_server_owner_or_admin)
    async def toggle_reply_model(self, interaction: discord.Interaction, model: app_commands.Choice[str]):
        datastore.reply_model = model.value
        await interaction.response.send_message(f"✅ AI reply model switched to **{model.name}**.", ephemeral=True)

    @app_commands.command(name="add_ai_restricted_roles", description="Add a role that cannot interact with the AI.")
    @app_commands.describe(role="Select the role to restrict from AI interaction.")
    @app_commands.check(is_server_owner_or_admin)
    async def add_ai_restricted_roles(self, interaction: discord.Interaction, role: discord.Role):
        if role.name not in datastore.ai_restricted_role:
            datastore.ai_restricted_role.append(role.name)
            await interaction.response.send_message(f"✅ Role **{role.name}** has been restricted from AI interaction.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Role **{role.name}** is already restricted.", ephemeral=True)

    @app_commands.command(name="add_ai_restricted_channels", description="Add a channel where AI will not respond.")
    @app_commands.describe(channel="Select the channel to restrict from AI interaction.")
    @app_commands.check(is_server_owner_or_admin)
    async def add_ai_restricted_channels(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if channel.id not in datastore.ai_restricted_channel:
            datastore.ai_restricted_channel.append(channel.id)
            await interaction.response.send_message(f"✅ AI will no longer respond in {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ AI is already restricted in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="view_ai_restricted_roles", description="View all roles restricted from AI interaction.")
    @app_commands.check(is_server_owner_or_admin)
    async def view_ai_restricted_roles(self, interaction: discord.Interaction):
        roles = ", ".join(datastore.ai_restricted_role) or "No restricted roles."
        await interaction.response.send_message(f"🔹 **AI Restricted Roles:**\n{roles}", ephemeral=True)

    @app_commands.command(name="view_ai_restricted_channels", description="View all channels where AI is restricted.")
    @app_commands.check(is_server_owner_or_admin)
    async def view_ai_restricted_channels(self, interaction: discord.Interaction):
        channels = ", ".join(f"<#{cid}>" for cid in datastore.ai_restricted_channel) or "No restricted channels."
        await interaction.response.send_message(f"🔹 **AI Restricted Channels:**\n{channels}", ephemeral=True)

    @app_commands.command(name="clear_ai_restrictions", description="Remove all AI restrictions (roles & channels).")
    @app_commands.check(is_server_owner_or_admin)
    async def clear_ai_restrictions(self, interaction: discord.Interaction):
        datastore.ai_restricted_role.clear()
        datastore.ai_restricted_channel.clear()
        await interaction.response.send_message("✅ All AI restrictions have been cleared!", ephemeral=True)

    @add_friends.error
    @remove_friends.error
    @clear_ai_restrictions.error
    @add_ai_restricted_roles.error
    @add_ai_restricted_channels.error
    @view_ai_restricted_roles.error
    @view_ai_restricted_channels.error
    async def restricted_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("⚠️ You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ An error occurred. Please try again.", ephemeral=True)

    @toggle_reply_model.error
    async def on_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("⚠️ You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ An unexpected error occurred. Please try again.", ephemeral=True)
    async def should_respond_to(self, message):
        if (self.bot.user in message.mentions) and (str(self.bot.user.id) in str(message.content)):
            return True
        if message.reference and message.reference.resolved:
            ref_message = message.reference.resolved
            if ref_message.id in self.bot_reply_ids:
                return True
            return False


    @commands.Cog.listener()
    async def on_message(self, message):

        if datastore.reply_model == "disabled":
            return
        if message.author == self.bot.user:
            return
        if message.channel.id in datastore.ai_restricted_channel:
            return
        
        user_roles = [role.name for role in message.author.roles] if isinstance(message.author, discord.Member) else []

        if any(role in datastore.ai_restricted_role for role in user_roles):
            return
        
        if not await self.should_respond_to(message):
            return
        
        user_id = str(message.author.id)

        if self.bot.user in message.mentions or (message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user):
            if user_id not in self.chat_history:
                self.chat_history[user_id] = deque(maxlen=5)


            self.chat_history[user_id].append(f"User: {message.content}")
            display_name = await get_display_name(message.guild, message.author.id)
            response =await self.generate_ai_response(message.content, user_id, display_name)
            self.chat_history[user_id].append(f"AI: {response}")
            await self.send_typing_reply(message, response)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))
