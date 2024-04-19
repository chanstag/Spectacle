"""
    File Header
    - 0x89
    - 0x50 0x4E 0x47
    - 0x0D 0x0A
    - 0x1A
    - 0x0A

    Chunks
    +----+----+----+----+----+----+----+----+----+
    | length  |   Chunk Type |  data   |   CRC   |
    +----+----+----+----+----+----+----+----+----+
    | 4 bytes |     4 bytes  |  length |  4 bytes|
    +----+----+----+----+----+----+----+----+----+
"""
import copy
import math
import os.path

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Union, Literal, Self, Protocol, Optional, List, Final
from enum import Enum
import io
import zlib
from Spectacle.imageformat import ImageFormat
from Spectacle.image import Pixel, Image


class PNGHeader(Enum):  # 8 bytes
    transmission_bit = b'\x89'
    namesake = b'PNG'
    crlf = b'\r\n'
    eof = b'\x1a'
    lf = b'\n'

    # def __init__(self, *args, **kwargs):
    #     import pdb
    #     pdb.set_trace()
    #     if len(args) == 1 and len(args[0]) == 8:
    #         png_bytes = args[0]
    #         self.transmission_bit = png_bytes[0:1]
    #         self.namesake = png_bytes[1:4]
    #         self.crlf = png_bytes[4:6]
    #         self.eof = png_bytes[6:7]
    #         self.lf = png_bytes[7:8]
    def validate(byte_sequence: bytes):
        if len(byte_sequence) == 8:
            if byte_sequence[0:1] != PNGHeader.transmission_bit.value and byte_sequence[1:4] != PNGHeader.namesake.value and byte_sequence[4:6] != PNGHeader.crlf.value and byte_sequence[6:7] != PNGHeader.eof.value and byte_sequence[7:8] != PNGHeader.lf.value:
                return False
            else:
                return True
        else:
            return False

    # I want to define an __init__ method that can take a sequence and divide it up.


class BitDepth(Enum):
    one = b'\x01'
    two = b'\x02'
    four = b'\x04'
    eight = b'\x08'
    sixteen = b'\x10'


class ColorType(Enum):
    zero = b'\x00' #grayscale
    two = b'\x02' # RGB
    three = b'\x03' # indexed into palette
    four = b'\x04' # grayscale w/ alpha
    six = b'\x06' # RGB w/ alpha


@dataclass
class IHDR:
    width: bytes = Field(min_length=4, max_length=4)
    height: bytes = Field(min_length=4, max_length=4)
    bit_depth: BitDepth = Field()
    color_type: bytes = Field(min_length=1, max_length=1)
    compression_method: bytes = Field(min_length=1, max_length=1)
    filter_method: bytes = Field(min_length=1, max_length=1)
    interlace: bytes = Field(min_length=1, max_length=1)


def process_ihdr(contents, length) -> IHDR:
    if len(contents) < length:
        raise IndexError

    return IHDR(contents[0:4], contents[4:8], BitDepth(contents[8:9]), contents[9:10], contents[10:11], contents[11:12],
                contents[12:13])


@dataclass
class PLTE:
    var = None


def process_plte(contents, length):
    raise NotImplemented


@dataclass
class IDAT:
    compression_method: bytes = Field(min_length=1, max_length=1)
    fcheck: bytes = Field(min_length=1, max_length=1)
    data: bytes = Field()
    adler_checksum: bytes = Field(min_length=4, max_length=4)


@dataclass
class IEND:
    data: Optional[bytes] = Field(min_length=0, max_length=0)


@dataclass
class AUX:
    data: Optional[bytes] = Field()


class ChecksumException(Exception):
    pass


def process_idat(contents: bytes, length: int, *args):
    if len(contents) < length:
        raise IndexError
    idat = IDAT(contents[0:1], contents[1:2], contents[2:length - 4], contents[length - 4:length])
    return idat


def _process_scanline(line_before: bytes, current_line: bytes, bytes_per_pixel, filter_type) -> bytes:
    scanline = bytes()
    match filter_type:
        case b'\x00':  # None filter type, scanline is unmodified
            scanline = current_line[:]
        case b'\x01':  # sub filter type
            for index in range(0, len(current_line)):
                scanline += int.to_bytes((current_line[index] + scanline[index - bytes_per_pixel]) % 256) if index - bytes_per_pixel >= 0 else current_line[index:index+1]
        case b'\x02':  # up filter type
            for index in range(0, len(current_line)):
                scanline += int.to_bytes((current_line[index] + line_before[index]) % 256)
        case b'\x03':  # avg filter type Average(x) + floor((Raw(x-bpp)+Prior(x))/2)
            for index in range(0, len(current_line)):
                scanline += int.to_bytes((current_line[index] + math.floor((scanline[index - bytes_per_pixel] + line_before[
                        index]) / 2) % 256) % 256) if index - bytes_per_pixel >= 0 else int.to_bytes((current_line[index] + math.floor((0 + line_before[
                        index]) / 2) % 256) % 256)
        case b'\x04':  # Paeth filter type
            raise NotImplemented
    return scanline


def _defilter(data: bytes, height: int, width: int, bytes_per_pixel=1) -> List[bytes]:
    num_row = 0
    scanlines = list()
    while num_row < height:
        line_before = bytes(width*bytes_per_pixel) if num_row == 0 else current_scanline  # make a special exception for first scanline
        current_line = data[slice(num_row * (width * bytes_per_pixel + 1), num_row * (width * bytes_per_pixel + 1) + width * bytes_per_pixel + 1)][:]
        filter_type = current_line[0:1]
        current_scanline = _process_scanline(line_before, current_line[1:], bytes_per_pixel, filter_type=filter_type)
        scanlines.append(current_scanline)
        num_row += 1
    return scanlines

def process_iend(contents: bytes, length: int) -> IEND:
    return IEND(contents[:length])


def process_aux(contents: bytes, length: int) -> AUX:
    return AUX(contents[:length])


class ChunkTypes(Enum):
    IHDR = b'IHDR'
    PLTE = b'PLTE'
    IDAT = b'IDAT'
    IEND = b'IEND'
    AUX = b'AUX'

    @classmethod
    def _missing_(cls, value):
        return cls.AUX


critical_types = Union[IHDR, PLTE, IDAT, IEND]
non_critical_types = Union[AUX]
# chunk_types = Literal[b'IHDR', b'PLTE', b'IDAT', b'IEND', b'AUX']

typename_to_chunk_type = {b'IHDR': process_ihdr, b'PLTE': process_plte, b'IDAT': process_idat, b'IEND': process_iend,
                          b'AUX': process_aux}


@dataclass
class Chunk:
    chunk_type: ChunkTypes
    length: bytes = Field(min_length=4, max_length=4)
    chunk_data: Union[critical_types, non_critical_types] = Field()
    crc: bytes = Field(min_length=4, max_length=4)


def decompress_data(chunks: List[Chunk]) -> bytes:
    total_length = 0
    contents = bytes()
    for chunk in chunks:
        contents += chunk.chunk_data.compression_method + chunk.chunk_data.fcheck + chunk.chunk_data.data + chunk.chunk_data.adler_checksum
    total_length = len(contents)
    zobj = zlib.decompressobj()
    data = zobj.decompress(contents[:])
    checksum = zlib.adler32(data)
    if int.from_bytes(contents[total_length - 4:total_length]) != checksum:
        raise ChecksumException
    return data


def process_chunks(contents: bytes):
    i = 0
    idat_chunk = False
    idat_data = bytes()
    image_width = 0
    image_height = 0
    while i < len(contents):
        length_bytes = contents[i:i + 4]
        length = int.from_bytes(length_bytes)
        chunk_type = contents[i + 4:i + 8]
        data = contents[i + 8:i + 8 + length]
        crc = contents[i + 8 + length:i + 8 + length + 4]
        if chunk_type == b'IDAT':
            # idat_data += data
            idata = typename_to_chunk_type[chunk_type](data, length)
            idat = Chunk(ChunkTypes(chunk_type), length_bytes, idata, crc)
            yield chunk_type, idat
        elif chunk_type == b'IEND':
            chunk = Chunk(ChunkTypes(chunk_type), length_bytes, typename_to_chunk_type[chunk_type](data, length), crc)
            yield chunk_type, chunk
        else:
            chunk = Chunk(ChunkTypes(chunk_type), length_bytes,
                          typename_to_chunk_type.get(chunk_type, process_aux)(data, length), crc)
            yield chunk_type, chunk
        i += 8 + length + 4


@dataclass
class PNGData:
    var = None


def load_png_file(file: Union[io.TextIOBase, str]) -> Image:
    """function to load a given png file into an Image object.

    Parameters
    ----------
    file : Union[io.TextIOBase, str]

    Returns
    -------
    image : Image
        an image object is created from the png
    """
    chunks = {}
    with open(file, 'rb') as png_file:
        contents: bytes = png_file.read()
        try:
            header_data = [PNGHeader(contents[0:1]), PNGHeader(contents[1:4]), PNGHeader(contents[4:6]),
                           PNGHeader(contents[6:7]), PNGHeader(contents[7:8])]
            for key, chunk in process_chunks(contents[8:]):
                if not key in chunks:
                    chunks[key] = list()
                chunks[key].append(chunk)
        except ValueError as e:
            raise e
    # process idat data here
    decompressed_idat = decompress_data(chunks[b'IDAT'])
    # defilter idat data
    height = int.from_bytes(chunks[b'IHDR'][0].chunk_data.height)
    width = int.from_bytes(chunks[b'IHDR'][0].chunk_data.width)
    bit_depth = chunks[b'IHDR'][0].chunk_data.bit_depth
    color_type = chunks[b'IHDR'][0].chunk_data.color_type

    color_type_enum = ColorType(color_type)
    if color_type_enum is ColorType.two:
        bytes_per_pixel = (3 * int.from_bytes(bit_depth.value)) // 8
    if color_type_enum is ColorType.six:
        bytes_per_pixel = (4 * int.from_bytes(bit_depth.value)) // 8
    scanlines = _defilter(decompressed_idat, height, width, bytes_per_pixel)

    pixels = []
    for scanline in scanlines:
        for index in range(0, len(scanline)//bytes_per_pixel):
            pix = tuple(scanline[index*bytes_per_pixel:index*bytes_per_pixel+bytes_per_pixel])
            if color_type_enum is ColorType.two:
                pixels.append(Pixel(*pix, 0, (0, 255)))
            elif color_type_enum is ColorType.six:
                pixels.append(Pixel(*pix, (0, 255)))
    return Image(pixels, os.path.basename(os.path.splitext(file)[0]), height, width)
