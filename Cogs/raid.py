import discord
import random
import asyncio
from discord.ext import commands
from discord import app_commands

class RaiderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.raiders = set()
        self.mode = "punish"
        self.enabled = False  
        self.loser_channels = {}  
        self.recent_moves = {}     

        self.custom_messages = [
            "I fail before I even start",
            "I trip over flat ground more than I walk straight",
            "My life strategy is constant panic",
            "My mom hates me",
            "Even my cat ignores me",
            "Teachers laugh when I try",
            "I ruin everything before it begins",
            "I can’t even handle life properly",
            "I exist just to embarrass myself",
            "I live like I study… poorly",
            "I’m a walking meme",
            "I wake up just to embarrass myself",
            "My life plan is pure chaos",
            "I can’t even type properly",
            "I fail at everything I attempt",
            "I escaped from diddy’s party",
            "I am gay",
            "I cry myself to sleep every night",
            "I surprise myself by being this broken",
            "Fast typing doesn’t make me smart",
            "I scream more than I accomplish",
            "I always send the wrong message",
            "Even the bots pity me",
            "I am as desperate as a first year",
            "I live like a sleep-deprived mess",
            "I forget what’s important constantly",
            "I wrote an essay and no one cared",
            "My reputation dies with me",
            "I spam emojis instead of making sense",
            "I support things I never follow through on",
            "I fight chaos with more chaos",
            "I can’t even find my own direction",
            "My life collapses faster than I can blink",
            "I mute myself out of embarrassment",
            "I’m the reason rules were invented",
            "My morale is lower than my GPA",
            "I ping the wrong people and die inside",
            "I move like procrastination incarnate",
            "I join things just to immediately leave",
            "I wear failure like a badge of honor",
            "I get lost reading simple instructions",
            "I act confident but have zero skill",
            "My plan is blind hope and bad timing",
            "I laugh, I cry, mostly I fail",
            "I show up in the wrong place every time",
            "I mistype everything and wreck it",
            "I wrote a whole paragraph to be ignored",
            "I forget what I’m even supposed to be",
            "My schedule is a cruel joke",
            "I am a walking tutorial for losing",
            "I signed up for chaos, not success",
            "My plans dissolve in under ten seconds",
            "I bring enthusiasm with negative IQ",
            "I walk with fake confidence and zero clue",
            "I try to help and make things worse",
            "My reputation precedes me…and it trips",
            "No wonder I have no friends, I actively sabotage it",
            "I hate being single and I'm bad at dating",
            "I am sooooo jobless and proud of nothing",
            "My GPA is less impressive than my apathy",
            "I ruin group work by existing",
            "My parents whisper about me like a weird myth",
            "The cafeteria food has more personality than I do",
            "I collect rejection like unwanted trophies",
            "My reflection looks at me with pity",
            "I'm a permanent understudy for my own life",
            "I am the human equivalent of a software bug",
            "People remember me as a cautionary tale",
            "My confidence is smoke and mirrors — mostly smoke",
            "I am emotionally understocked and on backorder",
            "I keep mistaking my life for a test I didn't study for",
            "I am a walking disappointment with good Wi-Fi",
            "Hope stops by once and never returns",
            "I have mastered the art of spectacularly small disasters",
            "My personality is buffering forever",
            "I apologize preemptively for being me",
            "My ego lives in a cardboard box",
            "I am the plot twist nobody asked for",
            "I am outclassed by average people",
            "I am a one-person circus with broken acts",
            "I am a leftover thought at the end of a bad day",
            "I specialize in making things quietly worse",
            "My standards are low and I still fail to hit them",
            "I am allergic to competence",
            "I am the static between someone's favorite song",
            "I am the least fun part of any story",
            "My dignity left a forwarding address and it's gone",
            "I'm great at self-sabotage — an expert, really",
            "I radiate 'try again later' energy",
            "My charm expired years ago",
            "I am the unpaid internship of relationships",
            "I cameo in my own life as the punchline",
            "I get ghosted by optimism",
            "I am a masterpiece of missed opportunities",
            "I am permanently outmatched by basic responsibilities",
            "I file my ambitions under 'maybe never'",
            "I am the background error log of society",
            "I flunk at normal functioning like it’s an art",
            "My presence is the minor inconvenience everyone tolerates",
            "I am a slow-motion disaster in HD",
            "I am built from awkward moments and bad timing",
            "I am better at catastrophes than comebacks",
            "I am an unpaid reminder to check your expectations",
            "I underdeliver spectacularly and consistently",
            "My life is a draft with no save button",
            "I am the emergency exit everyone avoids",
            "I am a cautionary meme in human form"
        ]
        self.message_pool = []
        self._reshuffle_messages()

        self.allowed_users = {1279851915596922941}
    def _reshuffle_messages(self):
        self.message_pool = self.custom_messages.copy()
        random.shuffle(self.message_pool)

    def get_next_message(self) -> str:
        if not self.message_pool:
            self._reshuffle_messages()
        return self.message_pool.pop()

    async def _check_perms(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in self.allowed_users:
            await interaction.response.send_message("🚫 You are not authorized to use this command.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="add_raiders", description="Add a user to the raider list")
    async def add_raiders(self, interaction: discord.Interaction, member: discord.Member):
        if not await self._check_perms(interaction): return
        self.raiders.add(member.id)
        await interaction.response.send_message(f"✅ {member.mention} added to raider list.", ephemeral=True)

    @app_commands.command(name="remove_raiders", description="Remove a user from the raider list")
    async def remove_raiders(self, interaction: discord.Interaction, member: discord.Member):
        if not await self._check_perms(interaction): return
        if member.id in self.raiders:
            self.raiders.remove(member.id)
            await interaction.response.send_message(f"❌ {member.mention} removed from raider list.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{member.mention} is not in raider list.", ephemeral=True)

    @app_commands.command(name="view_raiders", description="View all raiders")
    async def view_raiders(self, interaction: discord.Interaction):
        if not await self._check_perms(interaction): return
        if not self.raiders:
            await interaction.response.send_message("No raiders in the list.", ephemeral=True)
        else:
            raider_mentions = [f"<@{uid}>" for uid in self.raiders]
            await interaction.response.send_message("👥 Raiders:\n" + "\n".join(raider_mentions), ephemeral=True)

    @app_commands.command(name="clear_raiders", description="Clear all raiders from the list")
    async def clear_raiders(self, interaction: discord.Interaction):
        if not await self._check_perms(interaction): return
        count = len(self.raiders)
        self.raiders.clear()
        await interaction.response.send_message(f"🧹 Cleared **{count}** raiders from the list.", ephemeral=True)

    @app_commands.command(name="toggle_raid_mode", description="Toggle between punish and delete mode")
    async def toggle_mode(self, interaction: discord.Interaction):
        if not await self._check_perms(interaction): return
        self.mode = "delete" if self.mode == "punish" else "punish"
        await interaction.response.send_message(f"🔄 Mode changed to **{self.mode}**", ephemeral=True)

    @app_commands.command(name="start_raid_module", description="Enable or disable the raid module")
    async def toggle_raid(self, interaction: discord.Interaction):
        if not await self._check_perms(interaction): return
        self.enabled = not self.enabled
        status = "ENABLED ✅" if self.enabled else "DISABLED ⛔"
        await interaction.response.send_message(f"Raid module is now **{status}**", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not self.enabled:
            return

        if message.author.id in self.raiders:
            try:
                await message.delete()
            except discord.Forbidden:
                return

            if self.mode == "punish":
                webhooks = await message.channel.webhooks()
                webhook = discord.utils.get(webhooks, name="RaiderPunishHook")

                if webhook is None:
                    webhook = await message.channel.create_webhook(name="RaiderPunishHook")
                chosen_message = self.get_next_message()

                await webhook.send(
                    content=chosen_message,
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url
                )
              
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        
        if not self.enabled:
            return

        if member.id in self.raiders and after.channel is not None:
            guild = member.guild

            loser_channel = self.loser_channels.get(guild.id)
            if loser_channel is None or not guild.get_channel(loser_channel.id):
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=True, speak=False),
                    guild.me: discord.PermissionOverwrite(connect=True, speak=True, move_members=True)
                }

                loser_channel = await guild.create_voice_channel(
                    "Loser's Lounge",
                    overwrites=overwrites
                )
                self.loser_channels[guild.id] = loser_channel
                self.bot.loop.create_task(self.cleanup_loser_channel(guild.id, loser_channel))
            now = asyncio.get_event_loop().time()
            last_move = self.recent_moves.get(member.id, 0)
            if now - last_move > 2:
                self.recent_moves[member.id] = now

                if (
                    member.voice
                    and member.voice.channel
                    and member.voice.channel.id != loser_channel.id
                ):
                    try:
                        await member.move_to(loser_channel)
                    except discord.Forbidden:
                        print(f"⚠️ Missing permissions to move {member} in {guild.name}")
                    except discord.HTTPException as e:
                        print(f"⚠️ Failed to move {member} in {guild.name}: {e}")

    async def cleanup_loser_channel(self, guild_id: int, channel: discord.VoiceChannel):
        await asyncio.sleep(20)
        if len(channel.members) == 0:
            try:
                await channel.delete()
                self.loser_channels.pop(guild_id, None)
                print(f"✅ Deleted empty Loser's Lounge in {channel.guild.name}")
            except discord.NotFound:
                pass
            except discord.Forbidden:
                print(f"⚠️ Missing permissions to delete {channel.name} in {channel.guild.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(RaiderCog(bot))
