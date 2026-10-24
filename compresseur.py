#!/usr/bin/env python3
"""Commandes du terminal pour le compresseur pédagogique P7EDU."""
import argparse
from archive_p7edu import compresser_fichier, decompresser_fichier


def main():
    parser = argparse.ArgumentParser(description="Compresseur pédagogique BWT + RLE + Huffman")
    parser.add_argument("action", choices=("compresser", "decompresser"))
    parser.add_argument("fichier", help="Fichier source ou archive .p7edu")
    args = parser.parse_args()
    if args.action == "compresser":
        result = compresser_fichier(args.fichier)
        print(f"Archive créée : {result} ({result.stat().st_size} octets)")
    else:
        result = decompresser_fichier(args.fichier)
        print(f"Fichier restauré : {result} ({result.stat().st_size} octets)")


if __name__ == "__main__":
    main()
