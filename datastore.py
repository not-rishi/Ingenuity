BOT_TOKEN = 
YOUR_GUILD_ID =
BOT_COMMANDS_ID = 

ANNOUNCEMENT_PERMISSION = ["Administrator","Owner", "Co Owner", "Announcement Permission","Moderator"]
ALLOWED_ROLES_ADMINISTRATIVE = ["Owner","Co Owner","Moderator","Administrator","Temporary Mod"] # Mute/Unmute/Ping
BOT_ADMINISTRATIVE = ["Owner","Co Owner"]
MUTE_ROLE_NAME = "Abused by Mod"

LOG_CHANNEL_NAME = "dump-log"  # Channel for logs


auto_delete_enabled = False  # Global flag for enabling/disabling auto-delete
blacklisted_roles = ["Restricted 1"]  # List of role names to blacklist
exception_channels = []  # List of channel IDs where messages won't be deleted
cache_autodelete_userlog = [] #List to store temparory IDs to prevent over DMing

# Enabled Cogs
cogs_extensions = ['cogs.mute', 'cogs.dm_delete', 'cogs.ping','cogs.join_message', 'cogs.verify','cogs.announce','cogs.snipe','cogs.routine_check','cogs.refresh_token','cogs.dailylog','cogs.overview','cogs.button_role','cogs.websearch','cogs.infohelp','cogs.aireply','cogs.ranking','cogs.faculty','cogs.redditposter','cogs.pilwelcome','cogs.raid']

# Email Verification 
CLIENT_ID = 
CLIENT_SECRET = 
REFRESH_TOKEN = 
TOKEN_URI = 'https://oauth2.googleapis.com/token'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
COMMAND_ACCEPTED_REFRESH_TOKEN = None

# WEB Search
GOOGLE_WEB_SEARCH_API_KEY= 
CUSTOM_SEARCH_ENGINE_KEY=

# Configure ALL Loading GIFs here
ping_loading_gif = 
email_sending_gif = 
email_sent_gif = 
joining_gif = 
logo_rotating = 
routine_check_gif =
genral_loading_gif = 
anime_loading = 
alternate_loading_gif = 

# Join Module
JOIN_MESSAGE_MODE = "default" # Mode options: "default", "custom", "disabled"
CUSTOM_JOIN_MESSAGE = "⚠️Error in Loading the Message"


# AI Support
PERSONA = "richie" 
reply_model = "mistral" # gemini or mistral
GEMINI_API_KEY = 
MISTRAL_API_URL=
MISTRAL_API_KEY = 
ai_restricted_channel = []
ai_restricted_role = []


# Live Scraping for Faculty List
department_list = []
use_live_scraping = False


