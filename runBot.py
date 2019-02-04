import os.path
import sys
from urllib.request import Request, urlopen

import cv2
import discord
import numpy as np
from discord.ext import commands
from discord.ext.commands import Bot
from PIL import Image, GifImagePlugin

import animeface
from url_to_image import ImageConverter

cascade_file = 'lbpcascade_animeface.xml'

# https://github.com/nagadomi/animeface-2009
# https://github.com/nya3jp/python-animeface


def detect2009(pilImage):
    faces = animeface.detect(pilImage)
    likelihood = 0
    for face in faces:
        if(likelihood < face.likelihood):
            likelihood = face.likelihood
    return len(faces), likelihood

# https://github.com/nagadomi/lbpcascade_animeface


def detect2011(image):
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)
    cascade = cv2.CascadeClassifier(cascade_file)
    # image = cv2.imread(filename, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor=1.1,
                                     minNeighbors=5,
                                     minSize=(24, 24))
    return len(faces)


def gif_detect(url):  # uses 2009 detection only
    gif = ImageConverter.url_to_pilGif(url)
    total_number_of_faces = 0
    likelihood = 0
    for frameIndex in range(0, gif.n_frames):
        tnof, ld = detect2009(
            gif.seek(frameIndex))
        total_number_of_faces += tnof
        likelihood += ld
    if likelihood > 1:
        likelihood = 1
    return total_number_of_faces/gif.n_frame, likelihood


# Discord

descr = 'An open source solution to the anime epidemic on Discord.'

bot = commands.Bot(command_prefix='ak!',
                   description=descr)

picEXT = ['.jpeg', '.png', '.jpg', '.gif']

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
            return  # Breaks out of function

    for ext in picEXT:
        await check_message(message, ext)


async def check_message(message, ext):
    # Looks at each attatchment's URL
    for attachment in message.attachments:
        if attachment.url.endswith(ext):
            await check_url(attachment.url, message, (ext == '.gif'))

    # Looks at URLS
    if message.content.lower().find(ext) != -1:
        await check_url(
            message.content[message.content.lower().index(
                "http"):message.content.lower().index(ext) + len(ext)],
            message,
            (ext == '.gif')
        )


async def check_url(url, message, is_gif=False):
    if(is_gif):
        number_of_faces, likelihood = gif_detect(url)
    else:  # Non-Gif
        img = ImageConverter.url_to_pilImage(url)
        number_of_faces, likelihood = detect2009(img)
        if number_of_faces < 0:  # check with 2011 detection
            number_of_faces = detect2011(img)
    if number_of_faces > 0:  # check if anime is present
        await delete_message(number_of_faces, likelihood, message, is_gif)


async def delete_message(number_of_faces, likelihood, message, is_gif=False):
    if likelihood == 0:  # Checks if uses 2011 detection
        likelihood = 0.75
    gif = ''  # not gif
    if is_gif:
        gif = 'per frame '
    await message.delete()
    await message.channel.send(
        "Image containing {0} anime faces {1}was deleted with {2}% certainty".format(
            number_of_faces, gif, '{0:.2f}'.format(likelihood*100))
    )
# Run Discord
# Gets token from 'token.secret' file or Heroku
if (os.environ.get('IS_HEROKU', None)):
    token = os.environ.get('TOKEN', None)
else:
    token = open('token.secret', 'r').read()
bot.run(token)
