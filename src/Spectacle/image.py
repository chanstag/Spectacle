from typing import Protocol
from Spectacle.imageformat import FORMAT
from dataclasses import dataclass
from typing import Union, Literal, Self, Protocol

@dataclass
class Pixel:
    red: int
    green: int
    blue: int
    pixel_range: tuple[Literal[0], int]

class Image:
    """
        Properties:
        - Here we will have _Image object that we perform all the operations on
        - dimensions of image
        - image contents as RGB Pixels
        - image characteristics
    """

    def __init__(self, pixels: list[Pixel], title: str, width: int, height: int):
        """

        """
        self.pixels = pixels
        self.title = title
        self.width = width
        self.height = height
        pass

    def rotate(self, degrees: float) -> Self:
        raise NotImplemented

    def brighten(self, lumen: float) -> Self:
        raise NotImplemented

    def color_to_grayscale(self, ):
        raise NotImplemented

    def show(self):
        raise NotImplemented
