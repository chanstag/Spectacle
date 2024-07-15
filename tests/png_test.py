import binascii

import pytest
from Spectacle.png import load_png_file, PNGHeader, save_file, IHDR, _create_ihdr
from Spectacle.image import Image, Pixel


def test_png_header():
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


def test_quilt_w_alpha():
    png = load_png_file("../media/quilt_alpha.png")

    defiltered_pixels = [b'iJJ\xff\xba\x91\x82\xff\x9f\xaa\xba\xff\xd4\xc3\xaa\xff',
                         b'\xb0\xb7\xc3\xff\x8ezs\xffhfl\xff\xa2iz\xff', b'\xa7lf\xff\x9f|z\xffmx|\xff\x82\x80~\xff',
                         b'\xa7\x82m\xff\x8ezs\xff\xbdif\xff\x9f\xaa\xba\xff']
    pixels = []
    bytes_per_pixel = 4

    for row in defiltered_pixels:
        for pix in zip((first for first in row[0:len(row):4]), (first for first in row[1:len(row):4]),
                       (first for first in row[2:len(row):4]), (first for first in row[3:len(row):4])):
            pixels.append(Pixel(*pix, (0, 255)))

    assert png == Image(pixels, "quilt", 4, 4)


def test_save_png():
    png = load_png_file("../media/quilt.png")
    save_file(png, "tmp_path.png")


def test_create_ihdr():
    ihdr_hex_bytes_raw = '00 00 00 01 00 00 00 01 08 06 00 00 00'
    ihdr_bytes = binascii.unhexlify("".join(ihdr_hex_bytes_raw.split(" ")))

    ihdr = IHDR()
    ihdr.width = ihdr_bytes[:4]
    ihdr.height = ihdr_bytes[4:8]
    ihdr.bit_depth = ihdr_bytes[8:9]
    ihdr.color_type = ihdr_bytes[9:10]
    ihdr.compression_method = ihdr_bytes[10:11]
    ihdr.filter_method = ihdr_bytes[11:12]
    ihdr.interlace = ihdr_bytes[12:13]

    expected_ihdr_bytes = b''.join(ihdr)

    img = Image([Pixel(255, 0, 0, 0, (0, 255))], 'Red Pixel', 1, 1)
    actual_ihdr_bytes, chunk_type =  _create_ihdr(img)

    assert actual_ihdr_bytes == expected_ihdr_bytes
