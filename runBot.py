import json
import os.path
import sys
from urllib.request import Request, urlopen

import cv2
import discord
import imageio
import numpy as np
from discord.ext import commands
from discord.ext.commands import Bot
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account
from PIL import Image

import animeface
from url_to_image import ImageConverter

cascade_file = 'lbpcascade_animeface.xml'
google_credentials = service_account.Credentials.from_service_account_info(
    json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
visionary = vision.ImageAnnotatorClient(
    credentials=google_credentials)

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


def gif_detect(url):  # Testing google cloud for gifs to reduce slow downs
    total_number_of_faces = 0
    likelihood = 0

    total_number_of_faces, likelihood = vision_detect(url)
    if likelihood > 0.0:
        return total_number_of_faces, likelihood
    gif = ImageConverter.url_to_gif(url)
    images = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif]
    for image in images:
        (nof, lh) = detect2009(Image.fromarray(image))
        total_number_of_faces += nof
        likelihood += lh
    if likelihood == 0:
        for image in images:
            total_number_of_faces += detect2011(image)
        likelihood = 0.75
    if likelihood > 1:
        likelihood = 1
    return total_number_of_faces/len(images), likelihood


def vision_detect(url):
    image = types.image(
        content=cv2.imencode('.jpg', ImageConverter.url_to_cv(url))[1].tostring())
    #image = types.Image()
    #image.source.image_uri = url
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
        print(0)
    else:  # Non-Gif
        # Google Vision Detection
        number_of_faces, likelihood = vision_detect(url)
        print(likelihood)
        if likelihood < 0.0:  # 2009 detection
            img = ImageConverter.url_to_pilImage(url)
            number_of_faces, likelihood = detect2009(img)
            if likelihood < 0.0:  # 2011 detection
                number_of_faces = detect2011(img)
    # check if anime is present
    print(likelihood)
    if likelihood > 0.0 or number_of_faces > 1.0:
        print(1)
        await delete_message(number_of_faces, likelihood, message, is_gif)


async def delete_message(number_of_faces, likelihood, message, is_gif=False):
    if likelihood == 0:  # Checks if uses 2011 detection
        likelihood = 0.75
    gif = ''  # not gif
    print(2)
    if is_gif:
        gif = 'per frame '
    await message.delete()
    if type(number_of_faces) is not str:
        number_of_faces = '{0:.2f}'.format(number_of_faces)
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
