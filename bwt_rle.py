"""Transformations pédagogiques BWT et RLE."""
from collections import Counter


def bwt(data):
    """Retourne la dernière colonne de la BWT et la ligne d’origine."""
    if not data:
        return b"", 0
    rotations = [(data[i:] + data[:i], i) for i in range(len(data))]
    rotations.sort(key=lambda item: item[0])
    last_column = bytes(row[-1] for row, _ in rotations)
    original_row = next(row for row, (_, start) in enumerate(rotations) if start == 0)
    return last_column, original_row


def inverse_bwt(last_column, original_row):
    """Reconstruit les données à partir de la dernière colonne BWT."""
    if not last_column:
        return b""
    counts = Counter(last_column)
    first_position = {}
    total = 0
    for symbol in sorted(counts):
        first_position[symbol] = total
        total += counts[symbol]
    seen = Counter()
    next_row = []
    for symbol in last_column:
        next_row.append(first_position[symbol] + seen[symbol])
        seen[symbol] += 1
    result = bytearray(len(last_column))
    row = original_row
    for i in range(len(last_column) - 1, -1, -1):
        result[i] = last_column[row]
        row = next_row[row]
    return bytes(result)


def rle_encode(data):
    """Encode les octets identiques consécutifs en paires compteur/valeur."""
    out = bytearray()
    i = 0
    while i < len(data):
        count = 1
        while i + count < len(data) and data[i + count] == data[i] and count < 255:
            count += 1
        out.extend((count, data[i]))
        i += count
    return bytes(out)


def rle_decode(data):
    """Décode les paires compteur/valeur produites par rle_encode."""
    if len(data) % 2:
        raise ValueError("Données RLE incomplètes")
    out = bytearray()
    for i in range(0, len(data), 2):
        count, symbol = data[i], data[i + 1]
        if count == 0:
            raise ValueError("Répétition RLE invalide")
        out.extend(bytes((symbol,)) * count)
    return bytes(out)
