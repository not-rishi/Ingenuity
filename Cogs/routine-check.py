import discord
import datastore
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import discord.ext
import time-parser
import email-otp
import discord
from discord.ext import commands
import asyncio
import google.generativeai as genai
import requests


def check_reply_status():

    if datastore.reply_model == "gemini":
        try:
            gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            response = gemini_model.generate_content("Test message for AI status.")
            if response and response.text:
                return "Primary G-2.0"
            else:
                return "⚫ Disabled"
        except:
            return "⚫ Disabled"

    elif datastore.reply_model == "mistral":
        try:
            API_URL = datastore.MISTRAL_API_URL
            MISTRAL_API_KEY = datastore.MISTRAL_API_KEY
            HEADERS = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            formatted_prompt = "This is a test message. Please respond."

            response = requests.post(API_URL, headers=HEADERS, json={"inputs": formatted_prompt})
            data = response.json()

            if isinstance(data, dict) and "error" in data:
                return f"❌ Mistral Error: {data['error']}"
            if data and isinstance(data, list) and "generated_text" in data[0]:
                return "Secondary I-7.B"
            else:
                return "⚫ Disabled"
        except:
            return "⚫ Disabled"

    else:
        return "⚫ Disabled"


def get_embed(choice, bot: commands.Bot) -> discord.Embed:
    bot_avatar_url = bot.user.display_avatar.url if bot.user.display_avatar else None

    if choice == "initial":
        embed = discord.Embed(
            title="Routine Check in Progress...",
            description="Task running in the background, please ignore.",
            color=0x3498db,
        )
        embed.set_image(url=datastore.routine_check_gif)
        embed.set_footer(text="Ingenuity Bot", icon_url=bot_avatar_url)
        return embed
    
    elif choice == "status report":
        ai_reply = check_reply_status()
        if datastore.JOIN_MESSAGE_MODE == "default":
            join_module = "⚪ Enabled"
        elif datastore.JOIN_MESSAGE_MODE == "custom":
            join_module = "🔵 Alternate"
        else:
            join_module ="⚫ Disabled"

        email_module_status = "⚪ Online" if email-otp.check_access_token() else "⚫ Offline"
        cogs_module = f"{len(bot.cogs)}/{len(datastore.cogs_extensions)}"
        auto_delete_status = "⚪ Enabled" if datastore.auto_delete_enabled else "⚫ Disabled"
        latency = round(bot.latency * 1000)
        if latency < 100:
            status = "🌕 Ultra Fast"
        elif latency < 250:
            status = "🌔 Smooth"
        elif latency < 400:
            status = "🌘 Lagging"
        else:
            status = "🌑 Critical"
        
        # Uptime
        uptime_str = time-parser.get_uptime()

        embed = discord.Embed(
            title="📊 Requested Check Results",
            color=0xFFC0CB
        )
        embed.add_field(name="🕒 Uptime", value=f"```{uptime_str}```", inline=False)
        embed.add_field(name="📥 Join Module", value=f"```{join_module}```", inline=True)
        embed.add_field(name="📧 Verification System", value=f"```{email_module_status}```", inline=True)
        embed.add_field(name="⚙️ Cogs Online", value=f"```{cogs_module}```", inline=True)
        embed.add_field(name="🗑️ Delete Module", value=f"```{auto_delete_status}```", inline=True)
        embed.add_field(name="📡 Latency",value=f"```{latency}ms | {status}```", inline=True)
        embed.add_field(name="🤖 AI Reply",value=f"```{ai_reply}```", inline=True)
        
        

        if email_module_status == "⚫ Offline":
            embed.add_field(
                name="⚠️ **Error(s) Found : Verification System**",
                value="```Error : Access Token unavailable```",
                inline=False,
            )
        else:
            embed.add_field(
                name="⚠️ **Error(s) Found : None**",
                value="```No anomaly found```",
                inline=False,
            )

        embed.set_footer(text="Generated check result by Ingenuity Bot", icon_url=bot_avatar_url)
        return embed

    # Status indicators
    ai_reply = check_reply_status()
    if datastore.JOIN_MESSAGE_MODE == "default":
            join_module = "⚪ Enabled"
    elif datastore.JOIN_MESSAGE_MODE == "custom":
            join_module = "🔵 Alternate"
    else:
            join_module ="⚫ Disabled"
    email_module_status = "⚪ Online" if email-otp.check_access_token() else "⚫ Offline"
    cogs_module = f"{len(bot.cogs)}/{len(datastore.cogs_extensions)}"
    auto_delete_status = "⚪ Enabled" if datastore.auto_delete_enabled else "⚫ Disabled"
    latency = round(bot.latency * 1000)
    if latency < 100:
        status = "🌕 Ultra Fast"
    elif latency < 250:
        status = "🌔 Smooth"
    elif latency < 400:
        status = "🌘 Lagging"
    else:
        status = "🌑 Critical"
    
    # Uptime
    uptime_str = time-parser.get_uptime()

    embed = discord.Embed(
        title="📊 Routine Check Results",
        color=0xFF00FF
    )
    embed.add_field(name="🕒 Uptime", value=f"```{uptime_str}```", inline=False)
    embed.add_field(name="📥 Join Module", value=f"```{join_module}```", inline=True)
    embed.add_field(name="📧 Verification System", value=f"```{email_module_status}```", inline=True)
    embed.add_field(name="⚙️ Cogs Online", value=f"```{cogs_module}```", inline=True)
    embed.add_field(name="🗑️ Delete Module", value=f"```{auto_delete_status}```", inline=True)
    embed.add_field(name="📡 Latency",value=f"```{latency}ms | {status}```", inline=True)
    embed.add_field(name="🤖 AI Reply",value=f"```{ai_reply}```", inline=True)
    

    if email_module_status == "⚫ Offline":
        embed.add_field(
            name="⚠️ **Error(s) Found : Verification System**",
            value="```Error : Access Token unavailable```",
            inline=False,
        )
    else:
        embed.add_field(
            name="⚠️ **Error(s) Found : None**",
            value="```No anomaly found```",
            inline=False,
        )

    embed.set_footer(text="Routine check by Ingenuity Bot", icon_url=bot_avatar_url)
    return embed



class DailyEmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.daily_embed_task.start()


    @discord.app_commands.command(name="get_status_report", description="Get the current status report of the bot.")
    async def get_status_report(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        loading_embed = discord.Embed().set_image(url=datastore.genral_loading_gif)
        message = await interaction.followup.send(embed=loading_embed, ephemeral=True)

        await asyncio.sleep(3)

        final_embed = get_embed("status report", self.bot)
        await message.edit(embed=final_embed)


    def cog_unload(self):
        self.daily_embed_task.cancel()

    @tasks.loop(minutes=1)
    async def daily_embed_task(self):
        now = datetime.now(self.timezone)
        if now.time().hour == 15 and now.time().minute == 00:  
            channel = self.bot.get_channel(datastore.BOT_COMMANDS_ID)
            if channel:
                initial_embed = get_embed("initial",self.bot)
                message = await channel.send(embed=initial_embed)
                await self.update_embed_after_delay(message)

    async def update_embed_after_delay(self, message: discord.Message):
        await discord.utils.sleep_until(datetime.now() + timedelta(seconds=30))
        final_embed = get_embed("final",self.bot)
        await message.edit(embed=final_embed)

    @daily_embed_task.before_loop
    async def before_daily_embed_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DailyEmbedCog(bot))
