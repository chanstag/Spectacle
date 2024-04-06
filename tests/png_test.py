import pytest
from Spectacle.png import load_png_file, PNGHeader
from Spectacle.image import Image, Pixel


def test_PNGHeader():
    png_bytes = bytes.fromhex('89504e470d0a1a0a')
    assert PNGHeader.validate(png_bytes) == True  # add assertion here


def test_single_pixel():
    pixel = load_png_file("../media/pixel.png")
    defiltered_pixel = [b'\xff\x00\x00']
    bytes_per_pixel = 3
    pixels = []
    for row in defiltered_pixel:
        for pix in zip((first for first in row[0:len(row):3]), (first for first in row[1:len(row):3]),
                       (first for first in row[2:len(row):3])):
            pixels.append(Pixel(*pix, 255, (0, 255)))
    assert pixel == Image(pixels, 'pixel', 1, 1)


def test_quilt():
    png = load_png_file("../media/quilt.png")
    defiltered_pixels = [b'P\x08\x0c\xact\\\x88\x98\xac\xcc\xb8\x98', b'\xa0\xa8\xb8pL<\x18\x08(\x8c\x1cL',
                         b'\x94(\x0c\x88PL,HP\\XT', b'\x94\\,pL<\xb0\x1c\x08\x88\x98\xac']
    pixels = []
    bytes_per_pixel = 3
    for row in defiltered_pixels:
        for pix in zip((first for first in row[0:len(row):3]), (first for first in row[1:len(row):3]),
                       (first for first in row[2:len(row):3])):
            pixels.append(Pixel(*pix, 255, (0, 255)))

    assert png == Image(pixels, "quilt", 4, 4)
