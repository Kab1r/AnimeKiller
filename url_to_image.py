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

from urllib.request import Request, urlopen

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
    def url_to_cv(url):
        img_file = ImageConverter.url_to_request(url)
        npArrayImg = np.asarray(bytearray(img_file.read()), dtype="uint8")
        cvImage = cv2.imdecode(npArrayImg, cv2.IMREAD_COLOR)
        # return the image
        return cvImage
