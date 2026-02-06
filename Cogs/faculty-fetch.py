import discord
from discord.ext import commands, tasks
from discord.ui import Select, View, Button
import datastore
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aiohttp
import io



spaced_departments = ["Civil Engineering",
"Mechanical Engineering",
"Electrical and Electronics Engineering",
"Electronics and Communication Engineering",
"Industrial Engineering and Management",
"Computer Science and Engineering",
"Electronics and Telecommunication Engineering",
"Information Science and Engineering",
"Electronics and Instrumentation Engineering",
"Medical Electronics Engineering",
"Chemical Engineering",
"Bio Technology",
"Computer Applications MCA",
"Management Studies and Research Centre",
"Mathematics Department",
"Physics Department",
"Chemistry Department",
"Aerospace Engineering",
"Machine Learning AI and ML",
"Computer Science and Engineering DS",
"Computer Science and Engineering IoT and CS",
"Artificial Intelligence and Data Science",
"Computer Science and Business Systems"
]
departments = [
    "Civil-Engineering",
    "Mechanical-Engineering",
    "Electrical-and-Electronics-Engineering",
    "Electronics-and-Communication-Engineering",
    "Industrial-Engineering-and-Management",
    "Computer-Science-and-Engineering",
    "Electronics-and-Telecommunication-Engineering",
    "Information-Science-and-Engineering",
    "Electronics-and-Instrumentation-Engineering",
    "Medical-Electronics-Engineering",
    "Chemical-Engineering",
    "Bio-Technology",
    "Computer-Applications-MCA",
    "Management-Studies-and-Research-Centre",
    "Mathematics-Department",
    "Physics-Department",
    "Chemistry-Department",
    "Aerospace-Engineering",
    "Machine-Learning-AI-and-ML",
    "Computer-Science-and-Engineering-DS",
    "Computer-Science-and-Engineering-IoT-and-CS",
    "Artificial-Intelligence-and-Data-Science",
    "Computer-Science-and-Business-Systems"
]

async def fetch_as_discord_file(url: str, filename: str = None) -> discord.File | None:
   # Downloading image here so we can send it as a discord file
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36",
        "Referer": "https://webcampus.bmsce.in/"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"❌ Failed to fetch {url}, status: {resp.status}")
                return None

            data = await resp.read()
            if not filename:
                if "." in url.split("/")[-1]:
                    filename = url.split("/")[-1]
                else:
                    filename = "file.png"

            return discord.File(io.BytesIO(data), filename=filename)

async def get_faculty_info_of(dept_index):
    if dept_index in [11,12,18,19,20]:
        link = f"https://bmsce.ac.in/home/{departments[dept_index]}-Faculty"
        response = requests.get(link)
        soup = BeautifulSoup(response.text,"html.parser")
        text = soup.get_text()
        import re
        text = re.sub(r'\n+', '\n', text).strip()
        text = text.replace('\uf0b7', '*')
        start_index,end_index = 0,0
        lines_list = text.splitlines()
        if dept_index == 20:
             match_exp = "Computer Science and Engineering (IoT and CS)"
        elif dept_index == 12:
             match_exp = "Computer Applications (MCA)"
        elif dept_index == 18:
             match_exp = "Machine Learning (AI and ML)"
        elif dept_index == 19:
             match_exp = "Computer Science and Engineering (DS)"
        else:
             match_exp = "Bio-Technology"
        
        for i in range(len(lines_list)):
            line = lines_list[i].strip()
            if line == f"FacultyHomeAcademics{match_exp}":
                    start_index = i
            elif line == f"{match_exp}":
                    end_index = i
    else:
        link = f"https://bmsce.ac.in/home/{departments[dept_index]}-Faculty"
        response = requests.get(link)
        soup = BeautifulSoup(response.text,"html.parser")
        text = soup.get_text()
        import re
        text = re.sub(r'\n+', '\n', text).strip()
        text = text.replace('\uf0b7', '*')
        start_index,end_index = 0,0
        lines_list = text.splitlines()
        for i in range(len(lines_list)):
            line = lines_list[i].strip()
            dept_name = departments[dept_index].replace("-", " ")
            if line == f"FacultyHomeAcademics{dept_name}":
                    start_index = i
            elif line == f"{dept_name}":
                    end_index = i
    k = 0
    images = soup.find_all('img')
    img_urls = []
    for img in images:
        img_url = img.get('src')
        if img_url:
            img_url = urljoin(link, img_url)
            img_urls.append(img_url)
    image_links = img_urls[3:]
    for i in range(start_index+1,end_index):
        line = (lines_list[i].strip()).lower()
        if line.endswith("@bmsce.ac.in"):
            proffessor_dict = {}
            
            if "professor" in (lines_list[i-2].lower()):
                designation = i-2
                name = i-3
                qualification = i-1
            else:
                 designation = i-1
                 name = i-2
                 qualification = None
            
            
            email = i
            research = i+1
            proffessor_dict["name"] = lines_list[name].strip()
            proffessor_dict["designation"] = lines_list[designation].strip()
            if qualification == None:
                 proffessor_dict["qualification"] = None
            else:
                proffessor_dict["qualification"] = lines_list[qualification].strip()
            proffessor_dict["email"] = lines_list[email].strip()
            proffessor_dict["research"] = lines_list[research].strip()
            proffessor_dict["department"] = departments[dept_index].replace("-"," ")
            proffessor_dict["images"] = image_links[k]
            datastore.department_list.append(proffessor_dict)
            k = k+1
    return True

class FacultyView(View):
    def __init__(self, faculty_data, faculty_list, selected_department, parent_cog, department_select):
        super().__init__(timeout=180)
        self.faculty_data = faculty_data
        self.faculty_list = faculty_list
        self.selected_department = selected_department
        self.parent_cog = parent_cog
        self.current_page = 0
        self.page_size = 25
        self.department_select = department_select

        self.professor_select = Select(
            placeholder=f"Select a professor from {self.selected_department}",
            options=[]
        )
        self.professor_select.callback = self.professor_select_callback
        self.add_item(self.department_select)
        self.add_item(self.professor_select)

        self.prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="previous")
        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next")
        self.prev_button.callback = self.update_select_options
        self.next_button.callback = self.update_select_options
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.update_options()


    def update_options(self):
        paginated_faculty, _ = self.parent_cog.paginate_faculty(self.faculty_list, self.current_page)
        self.professor_select.options = [discord.SelectOption(label=prof, value=prof) for prof in paginated_faculty]
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = (self.current_page + 1) * self.page_size >= len(self.faculty_list)

    async def update_select_options(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] == "next":
            if (self.current_page + 1) * self.page_size < len(self.faculty_list):
                self.current_page += 1
        elif interaction.data["custom_id"] == "previous" and self.current_page > 0:
            self.current_page -= 1

        self.update_options()
        await interaction.response.edit_message(view=self)

    async def professor_select_callback(self, interaction: discord.Interaction):
        selected_professor = self.professor_select.values[0]
        faculty = next((f for f in self.faculty_data if f['name'] == selected_professor), None)

        file = await fetch_as_discord_file(faculty["images"], "image.png")
        if not file:
            print(f"❌ Could not fetch image for {faculty['name']}")
            return


        if faculty:
            embed = discord.Embed(
                title=f"**{faculty['name']}**",
                description=f"``{faculty['designation']}``",
                color=0x00FFFF
            )
            embed.add_field(name="Department", value=faculty['department'], inline=False)
            embed.add_field(name="Qualification", value=faculty['qualification'], inline=False)
            embed.add_field(name="Email", value=faculty['email'], inline=False)
            embed.add_field(name="Research Interests", value=faculty['research'], inline=False)

            if interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.set_image(url="attachment://image.png")
            footer_url = interaction.client.user.avatar.url if interaction.client.user.avatar else None
            embed.set_footer(text="Generated by Ingenuity", icon_url=footer_url)
            self.professor_select.placeholder = f"{faculty['name']}"
            self.professor_select.disabled = True
            self.next_button.disabled = True
            self.prev_button.disabled = True

            await interaction.message.edit(view=self)


            await interaction.response.send_message(embed=embed,files=[file])
        else:
            await interaction.response.send_message("Faculty not found!", ephemeral=True)


class FacultySearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faculty_data = datastore.department_list
        self.departments = departments
        self.spaced_departments = spaced_departments
        if datastore.use_live_scraping:
            self.update_list.start()
        else:
            self.load_from_file()


    async def is_server_owner_or_admin(interaction: discord.Interaction) -> bool:
        if interaction.user.id == interaction.guild.owner_id:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        if any(role in datastore.BOT_ADMINISTRATIVE for role in user_roles):
            return True
        return False


    def load_from_file(self):
        try:
            with open("../Assets/Documents/faculty-list.txt", "r", encoding="utf-8") as f:
                datastore.department_list.clear()
                datastore.department_list.extend(json.load(f))
            print(f"Faculty data loaded from local file with {len(datastore.department_list)} members.")
        except Exception as e:
            print(f"Error loading faculty data from file: {e}")

    

    @tasks.loop(hours=1)
    async def update_list(self):
        print("Updating Department Information")
        datastore.department_list.clear()
        try:
            for i in range(len(departments)):
                await get_faculty_info_of(i)
            print(f"Department list updated with {len(datastore.department_list)} members")
        except Exception as e:
            print(f"[ERROR] Scraping failed: {e}")
            print("Falling back to offline faculty list.")
            self.load_from_file()

    async def scrape_all_departments(self):
        datastore.department_list.clear()
        for i in range(len(departments)):
            await get_faculty_info_of(i)
        print("Department list updated")
        

    @update_list.before_loop
    async def before_update_list(self):
        await self.bot.wait_until_ready()

    async def faculty_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=faculty['name'], value=faculty['name'])
            for faculty in self.faculty_data
            if current.lower() in faculty['name'].lower()
        ][:25]

    @discord.app_commands.command(name="search_faculty", description="Supports Auto-complete and suggestions, search for faculty members!")
    @discord.app_commands.describe(name="Start typing the faculty name")
    @discord.app_commands.autocomplete(name=faculty_autocomplete)
    async def search_faculty(self, interaction: discord.Interaction, name: str):
        embed = discord.Embed().set_image(url=datastore.alternate_loading_gif)
        await interaction.response.send_message(embed=embed)

        faculty = next((f for f in self.faculty_data if f['name'] == name), None)
        file = await fetch_as_discord_file(faculty["images"], "image.png")
        if not file:
            print(f"❌ Could not fetch image for {faculty['name']}")
            return

        if faculty:
            embed = discord.Embed(
                title=f"**{faculty['name']}**",
                description=f"``{faculty['designation']}``",
                color=0x00FFFF
            )
            embed.add_field(name="Department", value=faculty['department'], inline=False)
            embed.add_field(name="Qualification", value=faculty['qualification'], inline=False)
            embed.add_field(name="Email", value=faculty['email'], inline=False)
            embed.add_field(name="Research Interests", value=faculty['research'], inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.set_image(url="attachment://image.png")
            footer_url = interaction.client.user.avatar.url if interaction.client.user.avatar else None
            embed.set_footer(text="Generated by Ingenuity", icon_url=footer_url)

            await interaction.edit_original_response(embed=embed,attachments=[file])
        else:
            await interaction.response.send_message("Faculty not found!", ephemeral=True)

    @discord.app_commands.command(name="toggle_faculty_source", description="Changes Faculty data source between live scrapping and offline saved backup file.")
    @discord.app_commands.check(is_server_owner_or_admin)
    async def change_source(self,interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        datastore.use_live_scraping = not datastore.use_live_scraping
        status = "live scrapping" if datastore.use_live_scraping else "local backup"
        await interaction.followup.send(f"File sourcing method has been changed to {status}.", ephemeral=True)
        if datastore.use_live_scraping:
            try:
                await self.scrape_all_departments()
            except:
                print("Error Live Scrapping, falling back to backup")
                self.load_from_file()
        else:
            self.load_from_file()
        await interaction.followup.send(f"datastore updated with {(len(datastore.department_list)*7)-11} unique field entries",ephemeral=True)
    




    @discord.app_commands.command(name="show_faculty_list", description="Select department and faculty from drop down")
    async def show_faculty_list(self, interaction: discord.Interaction):
        department_select = Select(
            placeholder="Choose a department...",
            options=[discord.SelectOption(label=dept, value=dept) for dept in (self.spaced_departments)]
        )

        async def department_select_callback(interaction: discord.Interaction):
            selected_department = department_select.values[0]
            faculty_list = [faculty['name'] for faculty in self.faculty_data if faculty['department'] == selected_department.replace("-", " ")]

            if not faculty_list:
                await interaction.response.send_message(f"No faculty found in {selected_department}.", ephemeral=True)
                return

            view = FacultyView(self.faculty_data, faculty_list, selected_department, self, department_select)
            department_select.placeholder = f"{selected_department}"
            department_select.disabled = True
            await interaction.response.edit_message(view=view)

        department_select.callback = department_select_callback

        view = View()
        view.add_item(department_select)

        await interaction.response.send_message("Please select a department:", view=view)

    def paginate_faculty(self, faculty_list, page=0):
        start = page * 25
        end = start + 25
        paginated_list = faculty_list[start:end]
        return paginated_list, page
    
    @change_source.error
    async def on_command_error(self,interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CheckFailure):
            await interaction.response.send_message(
                "You do not have permission to use this command. Only selected users can use it.", ephemeral=True
            )
        else:
            await interaction.response.send_message("An unexpected error occurred. Please try again.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(FacultySearch(bot))
