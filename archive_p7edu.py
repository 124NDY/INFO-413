"""Format d’archive maison P7EDU : BWT, RLE, Huffman et contrôle SHA-256."""
import hashlib
import struct
from pathlib import Path
from bwt_rle import bwt, inverse_bwt, rle_encode, rle_decode
from huffman import huffman_encode, huffman_decode

MAGIC = b"P7EDU01\n"
BLOCK_SIZE = 256
EXTENSION = ".p7edu"


def compresser_octets(original):
    """Applique BWT/RLE par blocs, puis Huffman au flux RLE complet."""
    rle_stream = bytearray()
    blocks = []
    for start in range(0, len(original), BLOCK_SIZE):
        block = original[start:start + BLOCK_SIZE]
        transformed, row = bwt(block)
        encoded = rle_encode(transformed)
        blocks.append((len(block), row, len(encoded)))
        rle_stream.extend(encoded)
    packed, frequencies, bit_count = huffman_encode(bytes(rle_stream))
    output = bytearray(MAGIC)
    output.extend(struct.pack(">QHI", len(original), BLOCK_SIZE, len(blocks)))
    for original_length, row, rle_length in blocks:
        output.extend(struct.pack(">HHI", original_length, row, rle_length))
    output.extend(struct.pack(">H", len(frequencies)))
    for symbol, count in sorted(frequencies.items()):
        output.extend(struct.pack(">BQ", symbol, count))
    output.extend(struct.pack(">Q", bit_count))
    output.extend(packed)
    output.extend(hashlib.sha256(original).digest())
    return bytes(output)


def decompresser_octets(archive):
    """Décode .p7edu et vérifie tailles et empreinte du fichier restauré."""
    view = memoryview(archive)
    position = 0
    def take(size):
        nonlocal position
        if position + size > len(view):
            raise ValueError("Archive incomplète ou endommagée")
        result = view[position:position + size]
        position += size
        return result
    if bytes(take(len(MAGIC))) != MAGIC:
        raise ValueError("Ce fichier n’est pas une archive pédagogique P7EDU")
    original_size, block_size, block_count = struct.unpack(">QHI", take(14))
    if block_size != BLOCK_SIZE:
        raise ValueError("Taille de bloc non reconnue")
    blocks = [struct.unpack(">HHI", take(8)) for _ in range(block_count)]
    symbol_count = struct.unpack(">H", take(2))[0]
    frequencies = {}
    for _ in range(symbol_count):
        symbol, count = struct.unpack(">BQ", take(9))
        frequencies[symbol] = count
    bit_count = struct.unpack(">Q", take(8))[0]
    packed = bytes(take((bit_count + 7) // 8))
    expected_hash = bytes(take(32))
    if position != len(view):
        raise ValueError("Données supplémentaires après la fin de l’archive")
    rle_stream = huffman_decode(packed, frequencies, bit_count)
    output = bytearray()
    cursor = 0
    for original_length, row, rle_length in blocks:
        encoded = rle_stream[cursor:cursor + rle_length]
        if len(encoded) != rle_length:
            raise ValueError("Bloc incomplet")
        cursor += rle_length
        transformed = rle_decode(encoded)
        if len(transformed) != original_length:
            raise ValueError("Taille du bloc restauré incorrecte")
        output.extend(inverse_bwt(transformed, row))
    if cursor != len(rle_stream) or len(output) != original_size:
        raise ValueError("Taille totale restaurée incorrecte")
    if hashlib.sha256(output).digest() != expected_hash:
        raise ValueError("Vérification échouée : archive endommagée")
    return bytes(output)


def compresser_fichier(source):
    source = Path(source)
    destination = Path(str(source) + EXTENSION)
    destination.write_bytes(compresser_octets(source.read_bytes()))
    return destination


def decompresser_fichier(source):
    source = Path(source)
    original = decompresser_octets(source.read_bytes())
    name = source.name[:-len(EXTENSION)] if source.name.endswith(EXTENSION) else source.name + ".restaure"
    destination = source.with_name(name)
    if destination.exists():
        path = Path(name)
        destination = source.with_name(path.stem + ".restaure" + path.suffix)
    destination.write_bytes(original)
    return destination
