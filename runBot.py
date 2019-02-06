import json
import os.path
import re

import cv2
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account

from url_to_image import ImageConverter

google_credentials = service_account.Credentials.from_service_account_info(
    json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
visionary = vision.ImageAnnotatorClient(
    credentials=google_credentials)


def vision_detect(url):
    image = types.Image(
        content=cv2.imencode('.jpg', ImageConverter.url_to_cv(url))[1].tostring())
    response = visionary.label_detection(image=image)
    labels = response.label_annotations
    for label in labels:
        if(label.description.lower() == 'anime'):
            return 'a number of', label.score
    return 0, 0
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
            await check_url(attachment.url, message)

    # Looks at URLS
    urls = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        , message.content.lower())
    for url in urls:
        await check_url(url, message)


async def check_url(url, message):
    likelihood = vision_detect(url)
    if likelihood > 0.0:
        await delete_message(likelihood, message)


async def delete_message(likelihood, message):
    await message.delete()
    await message.channel.send(
        "Image containing anime was deleted with {0}% certainty".format(
            '{0:.2f}'.format(likelihood*100))
    )
# Run Discord
# Gets token from 'token.secret' file or Heroku
if (os.environ.get('IS_HEROKU', None)):
    token = os.environ.get('TOKEN', None)
else:
    token = open('token.secret', 'r').read()
bot.run(token)
