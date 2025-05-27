#!/usr/bin/env python3
"""
addr_alias — generate a human-friendly alias and small ASCII identicon
for a cryptocurrency address (Ethereum-style hex). No network calls, works offline.

Usage:
    python addr_alias.py 0xDEADBEEF...              # print alias + identicon
    python addr_alias.py --seed "optional text"     # deterministic different alias
    python addr_alias.py --format json 0x...        # JSON output
"""

from __future__ import annotations
import argparse
import hashlib
import sys
from typing import List

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

def hex_normalize(addr: str) -> str:
    a = addr.strip()
    if a.startswith("0x") or a.startswith("0X"):
        a = a[2:]
    return a.lower()

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make_pronounceable_alias(hexstr: str, seed: str = "") -> str:
    """
    Turn a hex fingerprint into a short pronounceable alias.
    Algorithm: take bytes from SHA256(hex+seed) and map to C-V-C-V-... pattern.
    """
    h = sha256_hex(hexstr + "|" + seed)
    # take first 10 bytes => 20 hex chars => we'll map to 5 syllables CVCVC
    # produce alias length ~10 characters
    out = []
    for i in range(5):
        # take two hex chars -> integer 0..255
        byte = int(h[i*2:(i*2)+2], 16)
        c = CONSONANTS[byte % len(CONSONANTS)]
        v = VOWELS[(byte >> 3) % len(VOWELS)]
        # optional final consonant influenced by next nibble
        c2 = CONSONANTS[(byte >> 5) % len(CONSONANTS)]
        out.append(c + v + c2)
    alias = "".join(out)
    # trim to readable length and capitalize first letter
    return alias[:12].capitalize()

def ascii_identicon(hexstr: str, size: int = 7) -> List[str]:
    """
    Create a small symmetric ASCII identicon (size x size), using bits of hash.
    Symmetric on vertical axis (left mirrored to right).
    """
    h = sha256_hex(hexstr)
    bits = bin(int(h, 16))[2:].zfill(256)
    grid = [[" " for _ in range(size)] for _ in range(size)]
    bit_idx = 0
    # pattern: fill left half+center (if odd), mirror to right
    half = (size + 1) // 2
    for r in range(size):
        for c in range(half):
            if bit_idx >= len(bits):
                bit_idx = 0
            grid[r][c] = "█" if bits[bit_idx] == "1" else " "
            # mirror
            grid[r][size - 1 - c] = grid[r][c]
            bit_idx += 1
    return ["".join(row) for row in grid]

def entropy_score_from_hex(hexstr: str) -> float:
    """
    Rough entropy estimate: calculate Shannon-like score of hex nibble distribution.
    Returns score 0..100 (higher == more uniform / more entropy).
    """
    from collections import Counter
    s = hexstr.lower()
    cnt = Counter(s)
    total = sum(cnt.values()) if cnt else 1
    import math
    ent = 0.0
    for v in cnt.values():
        p = v / total
        ent -= p * (math.log(p, 2) if p > 0 else 0)
    # max entropy for hex nibble distribution (16 symbols) is 4 bits
    # normalize to 0..100:
    normalized = min(100.0, (ent / 4.0) * 100.0)
    return round(normalized, 1)

def main():
    p = argparse.ArgumentParser(prog="addr_alias", description="Generate alias + identicon for an address")
    p.add_argument("address", nargs="?", help="Hex address (0x...) or raw hex fingerprint. If omitted, reads stdin.")
    p.add_argument("--seed", "-s", default="", help="Optional seed to vary alias deterministically")
    p.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    args = p.parse_args()

    addr = args.address
    if not addr:
        # try read from stdin
        addr = sys.stdin.read().strip()
        if not addr:
            print("Error: address required (positional or from stdin).", file=sys.stderr)
            sys.exit(2)

    hexaddr = hex_normalize(addr)
    # basic validation: hex chars only
    if any(c not in "0123456789abcdef" for c in hexaddr):
        print("Warning: address contains non-hex characters; proceeding with hashing anyway.", file=sys.stderr)

    fingerprint = sha256_hex(hexaddr)
    alias = make_pronounceable_alias(hexaddr, args.seed)
    identicon = ascii_identicon(hexaddr, size=7)
    entropy = entropy_score_from_hex(hexaddr)
    # short id (first 8 chars)
    short = fingerprint[:8]

    report = {
        "input": addr,
        "normalized": hexaddr,
        "fingerprint": fingerprint,
        "short_id": short,
        "alias": alias,
        "entropy_score": entropy,
        "identicon_lines": identicon,
    }

    if args.format == "json":
        import json
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Address: {addr}")
        print(f"Short id: {short}")
        print(f"Alias: {alias}")
        print(f"Entropy score (0..100): {entropy}")
        print("\nIdenticon:")
        for line in identicon:
            print(line)
        print("\nFingerprint (sha256):", fingerprint)

if __name__ == "__main__":
    main()
