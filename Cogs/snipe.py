import discord
from discord.ext import commands
from typing import Optional

protected_id = 1279851915596922941

class SnipeView(discord.ui.View):
    def __init__(self, messages, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = messages
        self.index = 0
        self.author = author

    async def update_message(self, interaction: discord.Interaction, no_message: Optional[str] = None):
        if no_message:
            embed = discord.Embed(
                description=no_message,
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Message {self.index + 1} of {len(self.messages)}")
        else:
            msg = self.messages[self.index]
            embed = discord.Embed(
                description=msg["content"],
                color=discord.Color.blue(),
                timestamp=msg["created_at"]
            )
            embed.set_author(
                name=str(msg["author"]),
                icon_url=msg["avatar_url"]
            )
            embed.set_footer(text=f"Message {self.index + 1} of {len(self.messages)}")

            # Handle image attachments
            if msg["attachments"]:
                for attachment in msg["attachments"]:
                    if attachment.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')):
                        embed.set_image(url=attachment)
                        break
                else:
                    attachment_urls = "\n".join(msg["attachments"])
                    embed.add_field(name="Attachments", value=attachment_urls, inline=False)

        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your snipe session!", ephemeral=True)
            return
        await interaction.response.defer()

        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)
        else:
            await self.update_message(interaction, "No `previous` message available!")

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your snipe session!", ephemeral=True)
            return
        await interaction.response.defer()

        if self.index < len(self.messages) - 1:
            self.index += 1
            await self.update_message(interaction)
        else:
            await self.update_message(interaction, "No `next` message available!")

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id not in self.sniped_messages:
            self.sniped_messages[message.channel.id] = []

        if message.author.id == protected_id:
            placeholder_message = {
                "content": "💔",
                "author": message.author,
                "created_at": message.created_at,
                "avatar_url": message.author.avatar.url if message.author.avatar else None,
                "attachments": [att.url for att in message.attachments]
            }
            self.sniped_messages[message.channel.id].append(placeholder_message)
        else:
            stored_message = {
                "content": message.content if message.content else "No text content.",
                "author": message.author,
                "created_at": message.created_at,
                "avatar_url": message.author.avatar.url if message.author.avatar else None,
                "attachments": [att.url for att in message.attachments]
            }
            self.sniped_messages[message.channel.id].append(stored_message)

        if len(self.sniped_messages[message.channel.id]) > 20:
            self.sniped_messages[message.channel.id].pop(0)

    @discord.app_commands.command(name="snipe", description="Snipe the last deleted message or messages from a specific user.")
    async def snipe(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        await interaction.response.defer()

        messages = self.sniped_messages.get(interaction.channel.id, [])

        if not messages:
            await interaction.followup.send("There's nothing to snipe!", ephemeral=True)
            return

        if user:
            messages = [msg for msg in messages if msg["author"].id == user.id]
            if not messages:
                await interaction.followup.send(f"No sniped messages found for {user.mention}", ephemeral=True)
                return

        view = SnipeView(messages=messages, author=interaction.user)
        await view.update_message(interaction)

    @discord.app_commands.command(name="snipe_clear", description="Clear the sniped messages.")
    async def clear(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.sniped_messages.pop(interaction.channel.id, None)
        await interaction.followup.send("Cleared the sniped messages!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Snipe(bot))
