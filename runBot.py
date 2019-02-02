import os.path
import sys
from urllib.request import Request, urlopen

import cv2
import discord
import numpy as np
from discord.ext import commands
from discord.ext.commands import Bot
from PIL import Image

import animeface
from url_to_image import ImageConverter


# https://github.com/nagadomi/animeface-2009
# https://github.com/nya3jp/python-animeface
def detect2009(pilImage):
    faces = animeface.detect(pilImage)
    likelihood = 0
    for face in faces:
        if(likelihood < face.likelihood):
            likelihood = face.likelihood
    return len(faces), likelihood

# def detect(image):
# 	if not os.path.isfile(cascade_file):
# 		raise RuntimeError("%s: not found" % cascade_file)

# 	cascade = cv2.CascadeClassifier(cascade_file)
# 	# image = cv2.imread(filename, cv2.IMREAD_COLOR)
# 	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 	gray = cv2.equalizeHist(gray)

# 	faces = cascade.detectMultiScale(gray,
# 									 # detector options
# 									 scaleFactor=1.1,
# 									 minNeighbors=5,
# 									 minSize=(24, 24))
# 	return len(faces)

# def gif_detect(url):
# 	clip = VideoFileClip(url)
# 	for frame in clip.iter_frames(): # Each Frame in gif Clip
# 		number_of_faces = detect(frame)
# 		if (number_of_faces > 0):
# 			return number_of_faces
# 	return 0 # None Found Case

# Discord


descr = 'An open source solution to the anime epidemic on Discord.'

bot = commands.Bot(command_prefix='ak!',
                   description=descr)

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
    for role in message.author.roles:
        if role.name.lower == 'unkilled':
            return
    for ext in picEXT:
        # Looks at each attatchment
        for attachment in message.attachments:
            if attachment.url.endswith(ext):
                url = attachment.url
                number_of_faces, likelihood = detect2009(
                    ImageConverter.url_to_pilImage(url))
                if number_of_faces > 0:
                    await delete_message(number_of_faces, likelihood, message)
        # Looks at URLS
        if message.content.lower().endswith(ext):
            url = message.content[message.content.lower().index("http"):]
            number_of_faces, likelihood = detect2009(
                ImageConverter.url_to_pilImage(url))
            if number_of_faces > 0:
                await delete_message(number_of_faces, likelihood, message)


async def delete_message(number_of_faces, likelihood, message):
    await message.delete()
    await message.channel.send(
        "Image containing {0} anime faces was deleted with {1}% accuracy".format(
            number_of_faces, '{0:.2f}'.format(likelihood*100))
    )
# Run Discord
# Gets token from 'token.secret' file or Heroku
if (os.environ.get('IS_HEROKU', None)):
    token = os.environ.get('TOKEN', None)
else:
    token = open('token.secret', 'r').read()
bot.run(token)
