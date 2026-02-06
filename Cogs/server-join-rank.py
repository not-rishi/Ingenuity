import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View
import datastore
from PIL import Image, ImageDraw, ImageFont
import os
import io
import asyncio

class RankCardGenerator:
    def __init__(self):
        self.width = 900
        self.height = 300
        
        self.bg_color = (30, 30, 35) 
        self.text_color = (240, 240, 245) 

        self.font_paths = {
            'main': self._find_font('arial.ttf'),
            'emoji': self._find_font('seguiemj.ttf')
        }

        self.rank_settings = {
            1: {'color': (255, 204, 0), 'symbol': None, 'tag': "1st", 'symbol_size': 70, 'highlight': (255, 204, 0, 100)},
            2: {'color': (180, 180, 190), 'symbol': None, 'tag': "2nd", 'symbol_size': 70, 'highlight': (180, 180, 190, 100)},
            3: {'color': (200, 120, 60), 'symbol': None, 'tag': "3rd", 'symbol_size': 70, 'highlight': (200, 120, 60, 100)},
            range(4, 11): {'color': (0, 200, 200), 'symbol':None, 'tag': 'Top 10', 'symbol_size': 50, 'highlight': (0, 200, 200, 100)},
            range(11, 101): {'color': (255, 160, 50), 'symbol': None, 'tag': 'Top 100', 'symbol_size': 50, 'highlight': (255, 160, 50, 100)},
            'default': {'color': (100, 160, 240), 'symbol': None, 'tag': None, 'symbol_size': 50, 'highlight': (100, 160, 240, 100)}
        }
    
    def _find_font(self, font_name):
        if os.name == 'nt': 
            font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                return font_path
        return None
    
    def _get_rank_style(self, rank_number):
        for key, value in self.rank_settings.items():
            if (isinstance(key, range) and rank_number in key) or rank_number == key:
                return value
        return self.rank_settings['default']
    
    def _create_background(self):
        bg = Image.new("RGBA", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(bg)
        
        for i in range(self.width):
            r = min(30 + i // 15, 50)
            g = min(30 + i // 15, 50)
            b = min(40 + i // 10, 60)
            draw.line([(i, 0), (i, self.height)], fill=(r, g, b), width=1)
      
        draw.rectangle(
            [20, 20, self.width-20, self.height-20],
            outline=(255, 255, 255, 50),
            width=2
        )
        
        return bg
    
    def _load_font(self, name, size):
        try:
            if name == 'emoji' and self.font_paths['emoji']:
                return ImageFont.truetype(self.font_paths['emoji'], size)
            elif name == 'main' and self.font_paths['main']:
                return ImageFont.truetype(self.font_paths['main'], size)
            return ImageFont.load_default(size=size)
        except:
            return ImageFont.load_default(size=size)
    
    def _add_rank_text(self, draw, rank_number, style):
        rank_font = self._load_font('main', 90)
        rank_text = f"Rank #{rank_number}"
        draw.text((205, 55), rank_text, font=rank_font, fill=(0, 0, 0, 100))
        draw.text((200, 50), rank_text, font=rank_font, fill=style['color'])
    
    def _add_award_symbol(self, draw, style):
        if style['symbol']:
            symbol_font = self._load_font('emoji', style['symbol_size'])
            draw.text((655, 65), style['symbol'], font=symbol_font, fill=(0, 0, 0, 100))
            draw.text((650, 60), style['symbol'], font=symbol_font, fill=style['color'])
    
    def _add_top_tag(self, draw, style):
        if style['tag']:
            tag_font = self._load_font('main', 35)
            tag_text = style['tag']
            text_bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x, y = 650, 150
            padding = 15
            draw.rounded_rectangle(
                [x-padding, y-padding, x+text_width+padding, y+text_height+padding],
                radius=10,
                fill=style['highlight'],
                outline=style['color'],
                width=3
            )
            draw.text((x, y), tag_text, font=tag_font, fill=style['color'])
    
    def _add_username(self, draw, username="ExampleUser#1234"):
        username_font = self._load_font('main', 35)
        # Shadow
        draw.text((205, 205), username, font=username_font, fill=(0, 0, 0, 100))
        # Main text
        draw.text((200, 200), username, font=username_font, fill=self.text_color)
    
    def _add_avatar(self, card, avatar_image):
        avatar_size = 150
        avatar = avatar_image.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
        mask = Image.new('L', (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        avatar = avatar.convert('RGBA')
        avatar.putalpha(mask)
        avatar_x = 30
        avatar_y = (self.height - avatar_size) // 2
        card.paste(avatar, (avatar_x, avatar_y), avatar)
        draw = ImageDraw.Draw(card)
        draw.ellipse(
            [avatar_x-2, avatar_y-2, avatar_x+avatar_size+2, avatar_y+avatar_size+2],
            outline=(255, 255, 255, 100),
            width=2
        )
    
    def generate_rank_card(self, rank_number, username="ExampleUser#1234", avatar_image=None):
        style = self._get_rank_style(rank_number)
        card = self._create_background()
        draw = ImageDraw.Draw(card)
        if avatar_image:
            self._add_avatar(card, avatar_image)
        
        self._add_rank_text(draw, rank_number, style)
        self._add_award_symbol(draw, style)
        self._add_top_tag(draw, style)
        self._add_username(draw, username)
        
        return card

class RankJoinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_per_page = 10
        self.sorted_members = []
        self.rank_card_generator = RankCardGenerator()
        self.update_rank_cache.start()

    @tasks.loop(hours=1)
    async def update_rank_cache(self):
        print("Updating rank cache...")
        guild = self.bot.get_guild(datastore.YOUR_GUILD_ID)
        if guild:
            members = guild.members
            self.sorted_members = sorted(members, key=lambda m: m.joined_at)
            print(f"Cache updated with {len(self.sorted_members)} members.")

    @update_rank_cache.before_loop
    async def before_update_rank_cache(self):
        await self.bot.wait_until_ready()

    async def generate_rank_card(self, user: discord.Member, rank: int):
        avatar_asset = user.display_avatar.replace(size=128)
        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)
        avatar_img = Image.open(buffer_avatar).convert("RGBA")

        card = self.rank_card_generator.generate_rank_card(
            rank_number=rank,
            username=f"{user.display_name}",
            avatar_image=avatar_img
        )

        buffer = io.BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)

        return discord.File(buffer, filename="rank_card.png")

    @app_commands.command(name="get_rank", description="Get the rank of a specific user based on their join date.")
    async def get_rank(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()

        if not self.sorted_members:
            await interaction.followup.send("Please wait, the bot is still loading data...", ephemeral=True)
            return
        
        loading_embed = discord.Embed(
            color=discord.Color.blurple())
        loading_embed.set_image(url=datastore.alternate_loading_gif)

        loading_msg = await interaction.followup.send(embed=loading_embed)

        await asyncio.sleep(4)
        rank = next((index + 1 for index, member in enumerate(self.sorted_members) if member.id == user.id), None)

        if rank is None:
            await interaction.followup.send(f"Could not find {user.name}#{user.discriminator} in the server.", ephemeral=True)
            return
        rank_card_file = await self.generate_rank_card(user, rank)

        embed = discord.Embed(
            title=f"{user.display_name}'s Rank",
            description=f"**Joined:** {self.sorted_members[rank - 1].joined_at.strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://rank_card.png")

        await loading_msg.edit(embed=embed, attachments=[rank_card_file])

    @app_commands.command(name="leaderboard", description="Show the leaderboard of oldest members in the server!")
    async def leaderboard(self, interaction: discord.Interaction):
        if not self.sorted_members:
            await interaction.response.send_message("Please wait, the bot is still loading data...", ephemeral=True)
            return

        await interaction.response.defer()  

        loading_embed = discord.Embed(
            title="Loading Leaderboard...",
            description="Please wait while I fetch the data 🔄",
            color=discord.Color.blurple()
        )
        loading_embed.set_image(url=datastore.alternate_loading_gif)  

        loading_msg = await interaction.followup.send(embed=loading_embed)
        await asyncio.sleep(4)
        view = RankPaginationView(self.sorted_members, self.users_per_page)
        view.message = await loading_msg.edit(content=None, embed=view.generate_embed(0), view=view)

class RankPaginationView(View):
    def __init__(self, sorted_members, users_per_page):
        super().__init__(timeout=60)
        self.sorted_members = sorted_members
        self.users_per_page = users_per_page
        self.page = 0
        self.total_pages = len(sorted_members) // users_per_page
        self.message = None

        self.previous_button = Button(label="Previous", style=discord.ButtonStyle.primary)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        self.update_button_states()

    def generate_embed(self, page):
        embed = discord.Embed(
            title="🏅 Server Join Leaderboard",
            description="Ranking of users based on when they joined the server.",
            color=discord.Color.blue()
        )

        start_idx = page * self.users_per_page
        end_idx = start_idx + self.users_per_page
        for idx, member in enumerate(self.sorted_members[start_idx:end_idx], start=start_idx + 1):
            embed.add_field(
                name=f"{idx}. {member.display_name}", 
                value=f"Joined: {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )

        embed.set_footer(text=f"Page {page + 1} of {self.total_pages + 1}")
        return embed

    def update_button_states(self):
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = self.page == self.total_pages

    async def previous_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page > 0:
            self.page -= 1
            self.update_button_states()
            await self.message.edit(embed=self.generate_embed(self.page), view=self)

    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page < self.total_pages:
            self.page += 1
            self.update_button_states()
            await self.message.edit(embed=self.generate_embed(self.page), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

async def setup(bot):
    await bot.add_cog(RankJoinCog(bot))
