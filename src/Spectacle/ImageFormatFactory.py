from image import Image
from typing import Protocol

class ImageFormatFactory(Protocol):

    def load_image_from_file(self, file_path: str) -> Image:
        """
        Says what it does. Load image from file path.
        """
        raise NotImplemented

    def convert_image_format(self, image_format: str) -> Image:
        """

        """
        raise NotImplemented


class PPMFactory:

    def load_image_from_file(self, file_path) -> Image:
        """
        call load_ppm_file function
        """
        pass

    def convert_image_format(self, image_format: FORMAT) -> Image:
        """

        """
        pass


class JPGFactory:
    """

    """

    def load_image_from_file(self, file_path) -> Image:
        """
        call JPG load_image function
        """
        pass

    def convert_image_format(self, image_format) -> Image:
        """
        call convert_to_png function
        """
        pass
