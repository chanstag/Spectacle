import pytest
from Spectacle import ppm
from Spectacle.ppm import _PPM, Pixel, load_ppm_file


def test_ppm_load():
    valid_ppm = _PPM(3, 2, 255,
                     [Pixel(0, 0, 255, (0, 255)),
                      Pixel(0, 255, 0, (0, 255)),
                      Pixel(255, 0, 0, (0, 255)),
                      Pixel(255, 0, 0, (0, 255)),
                      Pixel(0, 255, 0, (0, 255)),
                      Pixel(0, 0, 255, (0, 255))
                      ])
    ppm_to_test = load_ppm_file("/Users/chanstag/projects/image_lib/tests/file.txt")
    assert valid_ppm == ppm_to_test

