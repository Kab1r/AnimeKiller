import discord
from discord.ext import commands
from discord.ext.commands import Bot

import animeface
from PIL import Image
import cv2
import sys
import os.path
import numpy as np
from urllib.request import Request, urlopen
# from moviepy.editor import VideoFileClip

# import os

# cascade_file = "lbpcascade_animeface.xml"


def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    print(url)
    req = Request(url)
    req.add_header(
        'accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    )
    req.add_header(
        'user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.53 Safari/537.36'
    )
    resp = urlopen(req)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # return the image
    return image


def detect(cv2image):
    cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    faces = animeface.detect(img)
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
    for ext in picEXT:
        for attachment in message.attachments:
            if attachment.url.endswith(ext):
                url = attachment.url
                number_of_faces, likelihood = detect(url_to_image(url))
                if number_of_faces > 0:
                    await message.delete()
                    await message.channel.send(
                        "Image containing {0} anime faces was deleted with {1}%% accuracy".format(
                            number_of_faces, likelihood)
                    )
        if message.content.lower().endswith(ext):
            url = message.content[
                message.content.lower().index("http"):]
            number_of_faces, likelihood = detect(url_to_image(url))
            if number_of_faces > 0:
                await message.delete()
                await message.channel.send(
                    "Image containing {0} anime faces was deleted with {1}%% accuracy".format(
                        number_of_faces, likelihood)
                )


# Run Discord
# Gets token from 'token.secret' file or Heroku
if (os.environ.get('IS_HEROKU', None)):
    token = os.environ.get('TOKEN', None)
else:
    token = open('token.secret', 'r').read()
bot.run(token)
