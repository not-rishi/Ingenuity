import re
import discord
from database import LOG_CHANNEL_NAME
from datetime import datetime,timezone

start_time = datetime.now(timezone.utc)


def parse_time(time_str):
    match = re.match(r"(\d+)([mhd])", time_str.lower())
    if not match:
        return None
    value, unit = int(match[1]), match[2]
    return value * {"m": 60, "h": 3600, "d": 86400}[unit]

def format_time(seconds):
    if seconds < 3600:
        return f"{seconds // 60} minute(s)"
    elif seconds < 86400:
        return f"{seconds // 3600} hour(s)"
    else:
        return f"{seconds // 86400} day(s)"
    
async def send_log(guild: discord.Guild, message: str):
    log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel is None:
        log_channel = await guild.create_text_channel(LOG_CHANNEL_NAME)
    await log_channel.send(message)

def get_uptime() -> str:
    current_time = datetime.now(timezone.utc)
    uptime_duration = current_time - start_time

    days, remainder = divmod(uptime_duration.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
