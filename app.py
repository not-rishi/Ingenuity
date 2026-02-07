import discord
import time
import threading
import asyncio
from flask import Flask,jsonify
from discord.ext import commands
import datastore

app = Flask(__name__)

@app.route("/")
def home():
    return "Discord bot is running!", 200

@app.route("/status")
def status():
    if bot.is_closed():
        return jsonify({"status": "offline"})
    return jsonify({"status": "online"})

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.presences = True 
bot = commands.Bot(command_prefix="/", intents=intents)
imported_latency = bot.latency
ALLOWED_DM_USERS = {1279851915596922941}

async def dm_block_check(interaction: discord.Interaction) -> bool:
    return interaction.guild is not None or interaction.user.id in ALLOWED_DM_USERS

statuses = [
    (discord.ActivityType.listening, "Listening to students cry"),
    (discord.ActivityType.playing, "Playing with your lives"),
    (discord.ActivityType.playing, "Playing hide and seek with attendance"),
    (discord.ActivityType.watching, "Watching your GPA drop"),
    (discord.ActivityType.playing, "Playing catch-up with CIEs"),
    (discord.ActivityType.playing, "Playing the game of lab submissions"),
    (discord.ActivityType.listening, "Listening to seniors share their 'one backlog only' stories"),
    (discord.ActivityType.watching, "Watching the server burn (metaphorically)"),
    (discord.ActivityType.listening, "Listening to ‘I’ll start tomorrow’ promises"),
    (discord.ActivityType.watching, "Watching you struggle with lab reports"),
    (discord.ActivityType.watching, "Watching students forge medical certificate"),
    (discord.ActivityType.playing, "Playing the waiting game for results"),
    (discord.ActivityType.playing, "Playing with the canteen cats"),
    (discord.ActivityType.watching, "Watching students making fake medical certificate"),
    (discord.ActivityType.listening, "Listening to your thoughts... creepy, right?"),
    (discord.ActivityType.watching, "Watching students panic before CIEs"),
    (discord.ActivityType.watching, "Watching students use AI in Lab exams"),
    (discord.ActivityType.listening, "Listening to the sound of silence, server dead again?"),
    (discord.ActivityType.listening, "Listening to rants over APS Block?"),
    (discord.ActivityType.watching, "Watching BMSCE canteen queues grow"),
    (discord.ActivityType.watching, "Watching the law canteen disappear"),
    (discord.ActivityType.listening, "Listening to the voices in my code"),
    (discord.ActivityType.watching, "Watching you rush to the 8 AM class"),
    (discord.ActivityType.watching, "Watching CSE intake increase to 999999+"),
    (discord.ActivityType.listening, "Listening to the sound of procrastination"),
    (discord.ActivityType.watching, "Watching you get a backlog")
]

async def change_status():
    while True:
        for activity_type, status_text in statuses:
            activity = discord.Activity(type=activity_type, name=status_text)
            await bot.change_presence(status=discord.Status.online, activity=activity)
            await asyncio.sleep(300)  # Change every 5 min

# Update status and sync commands
@bot.event
async def on_ready():
    datastore.start_time = time.time()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        k = 0
        for extention in datastore.cogs_extensions:
            await bot.load_extension(extention)
            k+=1
        print(f"{k}/{len(datastore.cogs_extensions)} cogs loaded successfully")
    except Exception as e:
        print(f"{e}")
        
     # Apply DM block check to all app commands
    for command in bot.tree.walk_commands():
        command.add_check(dm_block_check)
    await bot.tree.sync()
    asyncio.create_task(change_status())  # Start the status change coroutine

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Commands can only be used in the **BMSCE** server.",
                ephemeral=True)

def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start() 
    bot.run(datastore.BOT_TOKEN)
