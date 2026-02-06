import discord
from discord.ext import commands, tasks
import datetime
import os
import datastore

IST_OFFSET = datetime.timedelta(hours=5, minutes=30)  # Indian Standard Time
LOG_CHANNEL_ID = 1348989264976805928  

async def is_server_owner_or_admin(interaction: discord.Interaction) -> bool:
    if interaction.user.id == interaction.guild.owner_id:
        return True

    user_roles = [role.name for role in interaction.user.roles]
    if any(role in datastore.BOT_ADMINISTRATIVE for role in user_roles):
        return True

    return False

class DailyLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.normal_messages = []  # Stores normal messages
        self.deleted_and_edited = []  # Stores deleted/edited messages
        self.audit_logs = []  # Stores audit logs
        self.daily_log_task.start()  # Start the scheduled log task

    def cog_unload(self):
        self.daily_log_task.cancel()  # Stop the task when cog is unloaded

    # Log every message sent
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        log_entry = f"[{datetime.datetime.now() + IST_OFFSET}] 💬 {message.author}: {message.content}"
        self.normal_messages.append(log_entry)

    # Log deleted messages
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        log_entry = f"[{datetime.datetime.now() + IST_OFFSET}] 🗑️ Deleted by {message.author}: {message.content}"
        self.deleted_and_edited.append(log_entry)

    # Log edited messages
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        log_entry = f"[{datetime.datetime.now() + IST_OFFSET}] ✏️ Edited by {before.author}:\nBefore: {before.content}\nAfter: {after.content}"
        self.deleted_and_edited.append(log_entry)

    # Log audit logs 
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        action_type = entry.action.name.replace("_", " ").title()
        target = entry.target
        user = entry.user
        log_entry = f"[{datetime.datetime.now() + IST_OFFSET}] 📜 {action_type} | Target: {target} | By: {user}"
        self.audit_logs.append(log_entry)

    # Generate log file and send to log channel
    async def send_logs(self, forced=False):
        if not (self.normal_messages or self.deleted_and_edited or self.audit_logs):
            return  

        # Get today's date in IST
        today = (datetime.datetime.utcnow() + IST_OFFSET).date().strftime("%Y-%m-%d")
        log_filename = f"server_log_{today}.txt"

        # Write logs to the file
        with open(log_filename, "w", encoding="utf-8") as log_file:
            log_file.write("📜 SERVER AUDIT LOGS:\n")
            log_file.write("\n".join(self.audit_logs) + "\n\n" if self.audit_logs else "No audit logs today.\n\n")

            log_file.write("🗑️ DELETED & EDITED MESSAGES:\n")
            log_file.write("\n".join(self.deleted_and_edited) + "\n\n" if self.deleted_and_edited else "No deleted or edited messages today.\n\n")

            log_file.write("💬 NORMAL MESSAGES:\n")
            log_file.write("\n".join(self.normal_messages) + "\n" if self.normal_messages else "No messages today.\n")

        # Send log file to log channel
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            with open(log_filename, "rb") as file:
                msg = f"📜 **{'Force' if forced else 'Daily'} Log for {today}**"
                await log_channel.send(msg, file=discord.File(file, log_filename))

        # Cleanup
        os.remove(log_filename)
        self.normal_messages.clear()
        self.deleted_and_edited.clear()
        self.audit_logs.clear()

    # Runs at midnight IST (UTC +5:30)
    @tasks.loop(hours=24)
    async def daily_log_task(self):
        await self.send_logs()

    @daily_log_task.before_loop
    async def before_daily_log_task(self):
        await self.bot.wait_until_ready() 

        now = datetime.datetime.utcnow() + IST_OFFSET
        midnight_ist = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0, 0)) - IST_OFFSET
        wait_time = (midnight_ist - now).total_seconds()

        print(f"🕛 Daily logs scheduled in {wait_time:.2f} seconds.")
        await discord.utils.sleep_until(midnight_ist)

    # Manually trigger log sending before midnight
    @discord.app_commands.command(name="force_logs", description="Force send the current day's logs up to this point")
    @discord.app_commands.check(is_server_owner_or_admin)
    async def force_logs(self, interaction: discord.Interaction):
        await self.send_logs(forced=True)
        await interaction.response.send_message("✅ Logs sent manually!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DailyLog(bot))
