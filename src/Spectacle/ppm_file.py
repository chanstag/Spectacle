"""
PPM image format:
P3
3 2
255
0 0 255
0 255 0
255 0 0
255 0 0
0 255 0
0 0 255
"""

from image import Image, Pixel
from imageformat import FORMAT
from typing import Union, Literal, Self, Protocol
from pathlib import Path
import io

def load_ppm_file(file: Union[io.TextIOBase, str]):
    # check for file type here
    import pdb
    pdb.set_trace()
    pixels: list[Pixel] = []
    if isinstance(file, str):
        try:
            with open(file, 'r', encoding='utf-8') as ppm_file:
                try:
                    magic_bit: str = ppm_file.readline().strip()
                    width, height = [int(x) for x in ppm_file.readline().split(" ")]
                    num_pixels = width * height
                    max_pixel_range = int(ppm_file.readline().strip())
                    for i in range(0, num_pixels):
                        line = ppm_file.readline().split()
                        pixels.append(Pixel(*[int(x) for x in line], pixel_range=(0, max_pixel_range)))
                except IOError:
                    raise
                ppm: PPM = PPM(width, height, 255, pixels, magic_bit)
        except OSError:
            raise OSError("file not found")
        return ppm
    else:
        raise Exception


def convert_png_to_ppm(image: Image):
    pass


def convert_jpg_to_ppm(image: Image):
    pass


convert_to_function = {FORMAT.JPG: convert_jpg_to_ppm, FORMAT.PNG: convert_png_to_ppm}


def convert_to_ppm(image: Image):
    if image.type in convert_to_function:
        return convert_to_function[image.type]


class PPM(Image):
    '''
        creates PPM objects. Should not be called directly.
    '''


    def __init__(self, width: int, height: int, max_color_range: int, pixels: list[Pixel], magic_value='P3'):
        self.width: int = width
        assert self.width > 0
        self.height: int = height
        assert self.height > 0
        self.max_color_range: int = max_color_range
        self.pixels = pixels
        self.magic_value = magic_value
        # assert self.max_color_range

    def __eq__(self, other):
        if isinstance(other, PPM):
            if len(self.pixels) != len(other.pixels):
                return False
            if other.pixels != self.pixels:
                return False
            return True
        else:
            return False

