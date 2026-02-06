import discord
from discord.ext import commands, tasks
import asyncpraw
from datetime import datetime
from zoneinfo import ZoneInfo
import random
import asyncio

default_avatar = [
    "https://www.redditstatic.com/avatars/avatar_default_02_7E53C1.png",
    "https://www.redditstatic.com/avatars/avatar_default_02_FF8717.png",
    "https://www.redditstatic.com/avatars/avatar_default_02_25B79F.png",
    "https://www.redditstatic.com/avatars/avatar_default_02_FF66AC.png",
    "https://www.redditstatic.com/avatars/avatar_default_02_EA0027.png",
    "https://www.redditstatic.com/avatars/avatar_default_02_FFB000.png"
]

ist = ZoneInfo("Asia/Kolkata")

class RedditForumCog(commands.Cog):
    def __init__(self, bot, reddit_client_id, reddit_client_secret, reddit_user_agent, subreddit_name, alternates, forum_channel_id):
        self.bot = bot
        self.subreddit_name = subreddit_name
        self.forum_channel_id = forum_channel_id
        self.alternates = alternates

        self.reddit = asyncpraw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )

        # self.get_alt_sub.start()
        self.get_bms_sub.start()
        #self.cleanup_webhooks.start()

    def cog_unload(self): 
        self.get_alt_sub.cancel()
        self.get_bms_sub.cancel()
        if self.cleanup_webhooks.is_running():
            self.cleanup_webhooks.cancel()

    # @tasks.loop(hours=10)
    # async def get_alt_sub(self):
    #     await self.bot.wait_until_ready()
    #     for subreddit in self.alternates:
    #         await self.initiate_thread(subreddit)


    
    @tasks.loop(hours=1)
    async def get_bms_sub(self):
        await self.bot.wait_until_ready()
        await self.initiate_thread(self.subreddit_name)
   
    async def initiate_thread(self, sub):
        try:

            if sub == "BMSCE":
                freq = 3
            else:
                freq = 1

            subreddit = await self.reddit.subreddit(sub)
            forum_channel = self.bot.get_channel(self.forum_channel_id)

            if not isinstance(forum_channel, discord.ForumChannel):
                return

            existing_threads = forum_channel.threads
            existing_titles = [thread.name.lower().strip() for thread in existing_threads]

            async for post in subreddit.top(time_filter="day", limit=freq):
                title = (post.title.strip())[:80] + f" - r/{sub}"

                if title.lower() in existing_titles:
                    continue

                firstliner = f"[Post by {post.author}](<https://reddit.com{post.permalink}>)"
                now_ist = datetime.now(ist)
                timestamp = now_ist.strftime("%Y-%m-%d %H:%M:%S")
                info_1 = (f"Upvotes: {post.score}  |  Comments: {post.num_comments}  |  Last updated: {timestamp}")
                post_content = str((post.selftext[:2000] or post.url)) + '\n\n' + firstliner + '\n\n\n' + info_1

                the_thread = await forum_channel.create_thread(name=title, content=post_content, auto_archive_duration=10080)

                parent_channel = self.bot.get_channel(self.forum_channel_id)
                webhook = await parent_channel.create_webhook(name=f"Reddit-{title[:20]}")

                await post.load()
                await post.comments.replace_more(limit=0)
                comments = await post.comments.list()

                if not comments:
                    continue
                else:
                    for comment in comments:


                        if comment.author is None:
                            author = "[deleted]"
                            avatar = random.choice(default_avatar)
                        else:
                            await comment.author.load()
                            author = comment.author.name
                            avatar = comment.author.icon_img or random.choice(default_avatar)

                        body = comment.body[:1900]


                        await self.post_reddit_comment_as_webhook(
                            webhook=webhook,
                            comment_body=body,
                            reddit_username=author,
                            avatar_url=avatar,
                            thread=the_thread.thread
                        )
                        await asyncio.sleep(1)
                try:
                    await webhook.delete()
                except Exception as e:
                    print(f"Failed to delete webhook: {e}")

        except Exception as e:
            print(f"Error posting Reddit content: {e}")


    async def delayed_start(self):
        await asyncio.sleep(600)
        self.cleanup_webhooks.start()



    



    @get_bms_sub.before_loop
    # @get_alt_sub.before_loop
    async def before_posting(self):
        await self.bot.wait_until_ready()

    async def post_reddit_comment_as_webhook(self, webhook, comment_body: str, reddit_username: str, avatar_url: str | None, thread: discord.Thread):
        try:
            await webhook.send(
                content=comment_body,
                username=reddit_username,
                avatar_url=avatar_url,
                thread=thread
            )
        except Exception as e:
            print(f"Error sending webhook message for {reddit_username}: {e}")
    

    @tasks.loop(hours=24)
    async def cleanup_webhooks(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.forum_channel_id)

        if not isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
            print(f"[Webhook Cleanup] Invalid channel type.")
            return

        try:
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                try:
                    await asyncio.sleep(0.5) 
                    await webhook.delete()
                    print(f"[Webhook Cleanup] Deleted webhook: {webhook.name}")
                except discord.NotFound:
                    print(f"[Webhook Cleanup] Webhook already deleted: {webhook.name}")
                except discord.Forbidden:
                    print(f"[Webhook Cleanup] Missing permission to delete: {webhook.name}")
                except discord.HTTPException as e:
                    print(f"[Webhook Cleanup] Failed to delete {webhook.name}: {e}")
        except Exception as e:
            print(f"[Webhook Cleanup] General error: {e}")


async def setup(bot):
        cog =RedditForumCog(
        bot,
        reddit_client_id="AyAynnV5FJWqHMvh3xRb1w",
        reddit_client_secret="eRcQl1weL67R294qJ8kOVQTyvRL3Gw",
        reddit_user_agent="DiscordBot by u/Zestyclose-Notice175",
        subreddit_name="BMSCE",
        alternates=[],
        forum_channel_id=1375881468907225249 )

        await bot.add_cog(cog)
        bot.loop.create_task(cog.delayed_start()) 
