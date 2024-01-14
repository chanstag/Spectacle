from imageformat import ImageFormat

class JPG(ImageFormat):
    """
    jpg are converted from RGB to Y'CBCR
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.709_conversion
    https://en.wikipedia.org/wiki/JPEG#JPEG_codec_example
    """
