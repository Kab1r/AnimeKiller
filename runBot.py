import discord, requests
from discord.ext import commands
from discord.ext.commands import Bot
from PIL import Image
from io import BytesIO

import tensorflow as tf

# Dataset Imports

# Train Models

# Test Image

# Discord

description = '''An open source solution
to the anime epidemic on Discord.'''
bot = commands.Bot(command_prefix = 'ak!',
    description = description)

picEXT = ['.jpeg', '.png', '.jpg']

# On Ready Function
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name + ", " + bot.user.id)

@bot.event
async def on_message(message):
    for ext in picEXT:
        if message.content.endswith(ext):
            url = message.attachments[0]['url']
            img = Image.open(
                BytesIO(requests.get(url).content))

# Run Discord
# Gets token from 'token.secret' file
with open(token.secret) as f:
    token = f.readlines()
client.run(token)
