from enum import Enum, auto
from typing import Protocol

class FORMAT(Enum):
    PNG = auto()
    JPG = auto()
    PPM = auto()


class ImageFormat(Protocol):

    def convert_image(self, convert_to: str):
        formats = {
            'PNG': FORMAT.PNG,
            'JPG': FORMAT.JPG,
            'PPM': FORMAT.PPM
        }
        conversion_function = {
            (FORMAT.PPM, FORMAT.PNG): "placeholder for ppm_to_png function",
            (FORMAT.PNG, FORMAT.PPM): "placeholder for png_to_ppm function"
        }

        if convert_to in formats:
            new_format = formats[convert_to]
        else:
            raise ValueError(convert_to)
        return
