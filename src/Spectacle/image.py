from typing import Protocol
from Spectacle.imageformat import FORMAT
from dataclasses import dataclass
from typing import Union, Literal, Self, Protocol

@dataclass
class Pixel:
    red: int
    green: int
    blue: int
    alpha: int
    pixel_range: tuple[Literal[0], int]

    def to_hex(self):
        return int.to_bytes(self.red) + int.to_bytes(self.green) + int.to_bytes(self.blue) + int.to_bytes(self.alpha)




class Image:
    """
        Properties:
        - Here we will have _Image object that we perform all the operations on
        - dimensions of image
        - image contents as RGB Pixels
        - image characteristics
    """
    def __init__(self, pixels: list[Pixel], title: str, height: int, width: int):
        """

        """
        self.pixels = pixels
        self.title = title
        self.width = width
        self.height = height
        pass

    def __eq__(self, other):
        return self.pixels == other.pixels and self.width == other.width and self.height == other.height

    def rotate(self, degrees: float) -> Self:
        """

        Parameters
        ----------
        degrees

        Returns
        -------

        """

        raise NotImplemented

    def brighten(self, lumen: float) -> Self:
        raise NotImplemented

    def color_to_grayscale(self, ):
        raise NotImplemented

    def show(self):
        raise NotImplemented
