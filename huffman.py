"""Codage de Huffman pédagogique avec arbre déterministe."""
import heapq
from collections import Counter


def construire_codes(frequencies):
    """Construit un arbre de Huffman et retourne les codes par octet."""
    if not frequencies:
        return {}
    heap = []
    order = 0
    for symbol, count in sorted(frequencies.items()):
        heapq.heappush(heap, (count, order, symbol))
        order += 1
    if len(heap) == 1:
        return {heap[0][2]: "0"}
    while len(heap) > 1:
        count_a, _, a = heapq.heappop(heap)
        count_b, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (count_a + count_b, order, (a, b)))
        order += 1
    codes = {}
    def parcourir(node, prefix):
        if isinstance(node, int):
            codes[node] = prefix
        else:
            parcourir(node[0], prefix + "0")
            parcourir(node[1], prefix + "1")
    parcourir(heap[0][2], "")
    return codes


def huffman_encode(data):
    frequencies = Counter(data)
    codes = construire_codes(frequencies)
    bits = "".join(codes[symbol] for symbol in data)
    bit_count = len(bits)
    bits += "0" * ((8 - len(bits) % 8) % 8)
    packed = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return packed, frequencies, bit_count


def huffman_decode(packed, frequencies, bit_count):
    expected = sum(frequencies.values())
    if expected == 0:
        return b""
    codes = construire_codes(frequencies)
    reverse = {code: symbol for symbol, code in codes.items()}
    bits = "".join(f"{value:08b}" for value in packed)[:bit_count]
    if len(codes) == 1:
        symbol = next(iter(codes))
        if bit_count != expected:
            raise ValueError("Flux Huffman invalide")
        return bytes((symbol,)) * expected
    result = bytearray()
    code = ""
    for bit in bits:
        code += bit
        if code in reverse:
            result.append(reverse[code])
            code = ""
    if code or len(result) != expected:
        raise ValueError("Flux Huffman incomplet ou corrompu")
    return bytes(result)
