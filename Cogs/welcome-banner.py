import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 300
PROFILE_SIZE = 150
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BACKGROUND_PATH = "../Assets/Images/Welcome-Background.png"

WELCOME_CHANNEL_ID = 1281127167387762693

class WelcomeMessagePIL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_welcome_image( self,user_image_url, username, background_path, join_rank):
        background = Image.open(background_path).convert("RGBA")
        if background.size != (CANVAS_WIDTH, CANVAS_HEIGHT):
            background = background.resize((CANVAS_WIDTH, CANVAS_HEIGHT))

        draw = ImageDraw.Draw(background)

        try:
            response = requests.get(user_image_url)
            avatar = Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            print("Failed to load user image:", e)
            return

        avatar = avatar.resize((PROFILE_SIZE, PROFILE_SIZE))
        mask = Image.new("L", (PROFILE_SIZE, PROFILE_SIZE), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, PROFILE_SIZE, PROFILE_SIZE), fill=255)
        avatar.putalpha(mask)

        avatar_pos = (50, (CANVAS_HEIGHT - PROFILE_SIZE) // 2)
        background.paste(avatar, avatar_pos, avatar)

        try:
            font_large = ImageFont.truetype(FONT_PATH, 25)
            font_small = ImageFont.truetype(FONT_PATH, 30)
            font_rank = ImageFont.truetype(FONT_PATH,10)
        except IOError:
            print("Font not found. Check FONT_PATH.")
            return

        welcome_text = "Welcome to the Server"
        if len(username) > 22:
            username = username[:21] + "..."
        username_text = username

        join_rank_text = f"Member Code : {join_rank}"
        text_color = (208, 205, 205, 255)

        draw.text((230, 115), welcome_text, font=font_small, fill=text_color)
        draw.text((230, 160), username_text, font=font_large, fill=text_color)
        draw.text((5, 285), join_rank_text, font=font_rank, fill=text_color)
        buffer = BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)
        buffer
        return buffer

    @app_commands.command(name="test_welcome_image", description="Sends a test welcome message image")
    async def test_join(self, interaction: discord.Interaction):
        avatar_url = interaction.user.display_avatar.replace(format="png", size=256).url
        username = interaction.user.display_name

        await interaction.response.defer(ephemeral=True, thinking=True)
        image_buffer = self.generate_welcome_image(avatar_url, username, BACKGROUND_PATH,self.get_join_rank(interaction.user))

        file = discord.File(fp=image_buffer, filename="welcome.png")
        await interaction.followup.send(content="Here is your welcome message!", file=file, ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if channel is None:
            print(f"Welcome channel with ID {WELCOME_CHANNEL_ID} not found!")
            return

        avatar_url = member.display_avatar.replace(format="png", size=256).url
        username = member.display_name

        image_buffer = self.generate_welcome_image(avatar_url, username, BACKGROUND_PATH,self.get_join_rank(member))
        if image_buffer is None:
            print("Failed to generate welcome image.")
            return

        file = discord.File(fp=image_buffer, filename="welcome.png")
        await channel.send(content=f"{member.mention}", file=file)

    def get_join_rank(self, member: discord.Member) -> int:
        guild = member.guild
        if not member.joined_at:
            return -1 
        sorted_members = sorted(
            (m for m in guild.members if m.joined_at),
            key=lambda m: m.joined_at
        )
        try:
            return sorted_members.index(member) + 1 
        except ValueError:
            return -1


async def setup(bot):
    await bot.add_cog(WelcomeMessagePIL(bot))
