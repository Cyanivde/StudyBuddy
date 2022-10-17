import discord
import asyncio
from datetime import datetime
import os
from app.utils import _update_resource_num_comments_and_time


class DiscordClientForMovingChannels(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guild_messages = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.do = False

    async def on_message(self, message):
        channel = message.channel
        if channel.position != 0:
            await channel.edit(position=0)

        resource_id = channel.topic.split('/')[-1][:-1]

        count = 0
        async for _ in channel.history(limit=None):
            count += 1

        _update_resource_num_comments_and_time(resource_id, count, datetime.now())


def create_discord_bot_for_moving_channels():
    client = DiscordClientForMovingChannels()
    asyncio.run(client.start(os.environ.get("DISCORD_TOKEN_2")))
