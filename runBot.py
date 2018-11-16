import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot

import tensorflow as tf
import numpy as np
import cv2
import urllib

# Dataset Imports

# Train Models

# Test Image
def isAnime(url):
	req = urllib.request.Request(url)
	image = urllib.request.urlopen(req).read()
	#pool3_features = sess.run(pool3,{'incept/DecodeJpeg/contents:0': image.read()})
	image.resize((299, 299), image.ANTIALIAS)
	image_array = np.array(image)[:, :, 0:3] # RGB only

# Discord

descr = 'An open source solution to the anime epidemic on Discord.'

bot = commands.Bot(command_prefix = 'ak!',
    description = descr)

picEXT = ['.jpeg', '.png', '.jpg']

# On Ready Function
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print('ID:')
	print(bot.user.id)

@bot.event
async def on_message(message):
    for ext in picEXT:
        if message.content.endswith(ext):
            url = message.attachments[0]['url']
            if isAnime(url):
            	await bot.delete_message(message)
# Run Discord
# Gets token from 'token.secret' file
token = open('token.secret', 'r').read()
bot.run(token)
