import discord
import asyncio

import os


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


def create_discord_bot_for_moving_channels():
    client = DiscordClientForMovingChannels()
    asyncio.run(client.start(os.environ.get("DISCORD_TOKEN_2")))
