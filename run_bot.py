"""
    AnimeKiller deletes images and urls
    in discord messages if they are marked
    as anime by Google Cloud Vision. The
    "run_bot" module is the main file.
"""
# Copyright (C) 2019  Kabir Kwatra
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
# 
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os.path

import cv2
from discord.ext import commands
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account

from url_to_image import ImageConverter

DESCRIPTION = 'An open source solution to the anime epidemic on Discord.'

BOT = commands.Bot(command_prefix='ak!',
                   description=DESCRIPTION)

PICTURE_EXT = ['.jpeg', '.png', '.jpg', '.gif']


@BOT.event
async def on_ready():
    """
        Displays a simple
        message on boot
    """
    print('Logged in as')
    print(BOT.user.name)
    print('ID:')
    print(BOT.user.id)


@BOT.event
async def on_message(message):
    """
        Main trigger for bot,
        checks message 'unkilled'
        role. Messages sent by those
        with the role are ignored
        from the anime removal.
    """
    for role in message.author.roles:
        if role.name.lower == 'unkilled':
            return  # Breaks out of function
    
    await check_embeds(message)
    for ext in PICTURE_EXT:
        await check_message(message, ext)


async def check_embeds(message):
    for embed in message.embeds:
        check_url(embed.image.url, message)

async def check_message(message, ext):
    """
        Checks each message for urls
        and each attachment for picture
        extentions. Sends urls to checker
    """
    for attachment in message.attachments:
        if attachment.url.endswith(ext):
            await check_url(attachment.url, message)

    # Looks at URLS
    urls = message.content.lower().split()
    for url in urls:
        await check_url(url, message)


async def check_url(url, message):
    """String url -> vission_detect -> delete_message"""
    likelihood = vision_detect(url)
    if likelihood > 0.0:
        await delete_message(likelihood, message)


def vision_detect(url):
    """String url -> Google Cloud -> Anime Score"""
    image = types.Image(
        content=cv2.imencode('.jpg', ImageConverter.url_to_cv(url))[1].tostring())
    response = VISIONARY.label_detection(image=image)
    labels = response.label_annotations
    for label in labels:
        if label.description.lower() == 'anime':
            return label.score
    return vision_detect_url(url)

def vision_detect_url(url):
    image = types.Image()
    image.source.image_uri = url
    response = VISIONARY.label_detection(image=image)
    labels = response.label_annotations
    for label in labels:
        if label.description.lower() == 'anime':
            return label.score
    return 0

async def delete_message(likelihood, message):
    """
        Deletes given message,
        sends alert with likelihood
    """
    await message.delete()
    await message.channel.send(
        "Image containing anime was deleted with {0}% certainty".format(
            '{0:.2f}'.format(likelihood*100))
    )
# Creates Vission Client
# Gets token and credentials from Env Var

VISIONARY = vision.ImageAnnotatorClient(
    credentials=service_account.Credentials.from_service_account_info(
        json.loads(
            os.environ.get(
                'GOOGLE_APPLICATION_CREDENTIALS'
            )
        )
    )
)

TOKEN = os.environ.get('TOKEN')
BOT.run(TOKEN)
