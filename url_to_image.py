from io import StringIO
from urllib.request import Request, urlopen
from matplotlib import cm
from PIL import Image
import cv2
import numpy as np


class ImageConverter:

    @staticmethod
    def url_to_request(url):
        req = Request(url)
        req.add_header(
            'accept',
            ('text/html,application/xhtml+xml,application/xml;'
             'q=0.9,image/webp,image/apng,*/*;q=0.8')
        )
        req.add_header(
            'user-agent',
            ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
             '(KHTML, like Gecko) Chrome/72.0.3626.53 Safari/537.36')
        )
        return urlopen(req)

    @staticmethod
    def url_to_pilImage(url):
        cv2Image = ImageConverter.url_to_cv(url)
        img_file = Image.fromarray(cv2Image)
        return img_file

    @staticmethod
    def url_to_cv(url):
        img_file = ImageConverter.url_to_request(url)
        npArrayImg = np.asarray(bytearray(img_file.read()), dtype="uint8")
        cvImage = cv2.imdecode(npArrayImg, cv2.IMREAD_COLOR)
        # return the image
        return cvImage
