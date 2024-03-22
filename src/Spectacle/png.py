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

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Union, Literal, Self, Protocol, Optional, List, Final
from enum import Enum
import io
import zlib
from Spectacle.imageformat import ImageFormat


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

    # I want to define an __init__ method that can take a sequence and divide it up.


class BitDepth(Enum):
    one = b'\x01'
    two = b'\x02'
    four = b'\x04'
    eight = b'\x08'
    sixteen = b'\x10'


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
    zobj = zlib.decompressobj()
    data = zobj.decompress(contents[:length])
    checksum = zlib.adler32(data)
    if int.from_bytes(contents[length - 4:length]) != checksum:
        raise ChecksumException
    try:
        # I need to defilter the data here
        idat = IDAT(contents[0:1], contents[1:2], data, contents[length - 4:length])
    except ValueError:
        raise ValueError
    return idat


def defilter(data: bytes) -> bytes:
    raise NotImplemented


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


def process_chunks(contents: bytes):
    i = 0
    idat_chunk = False
    idat_data = bytes()
    image_width = 0
    image_height = 0
    while i < len(contents):
        length_bytes = contents[i:i + 4]
        length = int.from_bytes(length_bytes)
        chunk_type= contents[i + 4:i + 8]
        data = contents[i + 8:i + 8 + length]
        crc = contents[i + 8 + length:i + 8 + length + 4]
        if chunk_type == b'IDAT':
            # idat_data += data
            idata = typename_to_chunk_type[b'IDAT'](data, len(data))
            idat = Chunk(ChunkTypes(b'IDAT'), len(data).to_bytes(4), idata, crc)
            yield b'IDAT', idat
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


def load_png_file(file: Union[io.TextIOBase, str]):
    import pdb
    pdb.set_trace()
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

    for chunk_types in chunks:
        pass

# class PNG(ImageFormat):
#
#     def __init__(self):
#         pass
