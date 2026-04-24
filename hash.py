#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║           HashHunter - Hash Cracker Tool             ║
║        For Educational & CTF Use Only                ║
║        Author: Raj | GitHub: @yourhandle             ║
╚══════════════════════════════════════════════════════╝

Supported Hash Types:
  MD5, SHA1, SHA224, SHA256, SHA384, SHA512

Modes:
  - Single hash cracking
  - Batch cracking from file
  - Hash identification only
  - Hash generation (for testing)

Usage:
  python3 hashhunter.py -H <hash> -w <wordlist>
  python3 hashhunter.py -f hashes.txt -w /usr/share/wordlists/rockyou.txt
  python3 hashhunter.py --identify <hash>
  python3 hashhunter.py --generate "password123" --type MD5
"""

import hashlib
import argparse
import sys
import re
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────

class Color:
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"

def banner():
    print(f"""{Color.CYAN}{Color.BOLD}
╔══════════════════════════════════════════════════════╗
║           HashHunter v1.0 - Hash Cracker             ║
║        For Educational & CTF Use Only                ║
╚══════════════════════════════════════════════════════╝
{Color.RESET}""")

# ─────────────────────────────────────────────
#  HASH DEFINITIONS
# ─────────────────────────────────────────────

HASH_TYPES = {
    "MD5":    (r"^[a-fA-F0-9]{32}$",   hashlib.md5),
    "SHA1":   (r"^[a-fA-F0-9]{40}$",   hashlib.sha1),
    "SHA224": (r"^[a-fA-F0-9]{56}$",   hashlib.sha224),
    "SHA256": (r"^[a-fA-F0-9]{64}$",   hashlib.sha256),
    "SHA384": (r"^[a-fA-F0-9]{96}$",   hashlib.sha384),
    "SHA512": (r"^[a-fA-F0-9]{128}$",  hashlib.sha512),
}

# ─────────────────────────────────────────────
#  HASH IDENTIFIER
# ─────────────────────────────────────────────

def identify_hash(h: str) -> list:
    """Identify possible hash types based on length and pattern."""
    h = h.strip()
    matches = []
    for name, (pattern, _) in HASH_TYPES.items():
        if re.match(pattern, h):
            matches.append(name)
    return matches


def print_identification(h: str):
    """Print hash identification results."""
    matches = identify_hash(h)
    print(f"\n{Color.BLUE}[*] Hash     : {Color.WHITE}{h}{Color.RESET}")
    print(f"{Color.BLUE}[*] Length   : {Color.WHITE}{len(h)} chars{Color.RESET}")
    if matches:
        print(f"{Color.GREEN}[+] Possible : {', '.join(matches)}{Color.RESET}")
    else:
        print(f"{Color.RED}[-] Unknown hash type.{Color.RESET}")
    print()


# ─────────────────────────────────────────────
#  HASH GENERATOR
# ─────────────────────────────────────────────

def generate_hash(plaintext: str, hash_type: str):
    """Generate a hash from plaintext for testing purposes."""
    hash_type = hash_type.upper()
    if hash_type not in HASH_TYPES:
        print(f"{Color.RED}[!] Unsupported hash type: {hash_type}{Color.RESET}")
        sys.exit(1)
    _, func = HASH_TYPES[hash_type]
    digest = func(plaintext.encode()).hexdigest()
    print(f"\n{Color.BLUE}[*] Plaintext : {Color.WHITE}{plaintext}{Color.RESET}")
    print(f"{Color.BLUE}[*] Type      : {Color.WHITE}{hash_type}{Color.RESET}")
    print(f"{Color.GREEN}[+] Hash      : {Color.WHITE}{digest}{Color.RESET}\n")


# ─────────────────────────────────────────────
#  CORE CRACKER
# ─────────────────────────────────────────────

def crack_single(target_hash: str, hash_func, wordlist_path: str, verbose: bool = False) -> str | None:
    """
    Try to crack a single hash using a wordlist.
    Returns the plaintext if found, else None.
    """
    target_hash = target_hash.strip().lower()
    tried = 0
    start = time.time()

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue
                digest = hash_func(word.encode()).hexdigest()
                tried += 1
                if verbose and tried % 100000 == 0:
                    elapsed = time.time() - start
                    rate = tried / elapsed if elapsed > 0 else 0
                    print(f"{Color.YELLOW}[~] Tried {tried:,} words | {rate:,.0f} w/s | Last: {word[:30]}{Color.RESET}", end="\r")
                if digest == target_hash:
                    elapsed = time.time() - start
                    print()
                    print(f"{Color.GREEN}[+] CRACKED in {elapsed:.2f}s after {tried:,} attempts{Color.RESET}")
                    return word
    except FileNotFoundError:
        print(f"{Color.RED}[!] Wordlist not found: {wordlist_path}{Color.RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[!] Interrupted by user.{Color.RESET}")
        sys.exit(0)

    elapsed = time.time() - start
    print(f"\n{Color.RED}[-] Not found after {tried:,} attempts in {elapsed:.2f}s{Color.RESET}")
    return None


# ─────────────────────────────────────────────
#  SINGLE HASH MODE
# ─────────────────────────────────────────────

def mode_single(args):
    target = args.hash.strip()
    print(f"\n{Color.BLUE}[*] Target Hash : {Color.WHITE}{target}{Color.RESET}")

    detected = identify_hash(target)
    if detected:
        print(f"{Color.BLUE}[*] Detected    : {Color.GREEN}{', '.join(detected)}{Color.RESET}")
    else:
        print(f"{Color.RED}[!] Could not identify hash type automatically.{Color.RESET}")
        if not args.type:
            print(f"{Color.RED}[!] Use -t to specify type manually.{Color.RESET}")
            sys.exit(1)

    hash_type = (args.type or detected[0]).upper()
    if hash_type not in HASH_TYPES:
        print(f"{Color.RED}[!] Unsupported type: {hash_type}{Color.RESET}")
        sys.exit(1)

    _, hash_func = HASH_TYPES[hash_type]
    print(f"{Color.BLUE}[*] Using       : {Color.WHITE}{hash_type}{Color.RESET}")
    print(f"{Color.BLUE}[*] Wordlist    : {Color.WHITE}{args.wordlist}{Color.RESET}")
    print(f"{Color.BLUE}[*] Cracking...{Color.RESET}\n")

    result = crack_single(target, hash_func, args.wordlist, verbose=args.verbose)

    if result:
        print(f"\n{Color.GREEN}{Color.BOLD}[+] Plaintext   : \"{result}\"{Color.RESET}")
        if args.output:
            save_result(args.output, target, hash_type, result)
    else:
        print(f"\n{Color.RED}[-] Hash not cracked.{Color.RESET}")


# ─────────────────────────────────────────────
#  BATCH MODE (file of hashes)
# ─────────────────────────────────────────────

def mode_batch(args):
    if not os.path.isfile(args.file):
        print(f"{Color.RED}[!] Hash file not found: {args.file}{Color.RESET}")
        sys.exit(1)

    with open(args.file, "r", errors="ignore") as f:
        hashes = [line.strip() for line in f if line.strip()]

    print(f"\n{Color.BLUE}[*] Loaded {len(hashes)} hashes from {args.file}{Color.RESET}")
    print(f"{Color.BLUE}[*] Wordlist : {args.wordlist}{Color.RESET}\n")

    cracked = 0
    results = []

    for i, h in enumerate(hashes, 1):
        detected = identify_hash(h)
        hash_type = (args.type or (detected[0] if detected else None))
        if not hash_type:
            print(f"{Color.YELLOW}[?] ({i}/{len(hashes)}) Skipping unknown hash: {h}{Color.RESET}")
            continue

        hash_type = hash_type.upper()
        if hash_type not in HASH_TYPES:
            print(f"{Color.YELLOW}[?] Unsupported type for hash: {h}{Color.RESET}")
            continue

        print(f"{Color.CYAN}[{i}/{len(hashes)}] {hash_type} | {h}{Color.RESET}")
        _, hash_func = HASH_TYPES[hash_type]
        result = crack_single(h, hash_func, args.wordlist, verbose=args.verbose)

        if result:
            cracked += 1
            results.append((h, hash_type, result))
            print(f"     {Color.GREEN}=> \"{result}\"{Color.RESET}\n")
        else:
            results.append((h, hash_type, None))
            print(f"     {Color.RED}=> Not found{Color.RESET}\n")

    print(f"\n{Color.BOLD}[*] Summary: {cracked}/{len(hashes)} cracked{Color.RESET}")

    if args.output:
        with open(args.output, "w") as out:
            out.write(f"# HashHunter Batch Results - {datetime.now()}\n\n")
            for h, t, p in results:
                status = f'"{p}"' if p else "NOT FOUND"
                out.write(f"{h}:{t}:{status}\n")
        print(f"{Color.GREEN}[+] Results saved to {args.output}{Color.RESET}")


# ─────────────────────────────────────────────
#  SAVE RESULT
# ─────────────────────────────────────────────

def save_result(output_path: str, h: str, htype: str, plaintext: str):
    with open(output_path, "a") as f:
        f.write(f"{h}:{htype}:{plaintext}\n")
    print(f"{Color.GREEN}[+] Result saved to {output_path}{Color.RESET}")


# ─────────────────────────────────────────────
#  ARGUMENT PARSER
# ─────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="HashHunter - Hash Identifier & Wordlist Cracker",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Single hash:
    python3 hashhunter.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w /usr/share/wordlists/rockyou.txt

  Force type:
    python3 hashhunter.py -H <hash> -w rockyou.txt -t SHA256

  Batch from file:
    python3 hashhunter.py -f hashes.txt -w rockyou.txt -o results.txt

  Identify only:
    python3 hashhunter.py --identify 5f4dcc3b5aa765d61d8327deb882cf99

  Generate hash:
    python3 hashhunter.py --generate "password123" --type MD5
        """
    )

    parser.add_argument("-H",  "--hash",     help="Single hash to crack")
    parser.add_argument("-f",  "--file",     help="File containing multiple hashes (one per line)")
    parser.add_argument("-w",  "--wordlist", help="Path to wordlist file")
    parser.add_argument("-t",  "--type",     help="Force hash type (MD5, SHA1, SHA256, SHA512, ...)")
    parser.add_argument("-o",  "--output",   help="Save cracked results to file")
    parser.add_argument("-v",  "--verbose",  action="store_true", help="Show progress while cracking")
    parser.add_argument("--identify",        metavar="HASH", help="Identify hash type only (no cracking)")
    parser.add_argument("--generate",        metavar="TEXT", help="Generate hash from plaintext")

    return parser, parser.parse_args()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main():
    banner()
    parser, args = parse_args()

    # Mode: Identify only
    if args.identify:
        print_identification(args.identify)
        return

    # Mode: Generate hash
    if args.generate:
        if not args.type:
            print(f"{Color.RED}[!] Specify hash type with --type (e.g. --type MD5){Color.RESET}")
            sys.exit(1)
        generate_hash(args.generate, args.type)
        return

    # Mode: Single hash
    if args.hash:
        if not args.wordlist:
            print(f"{Color.RED}[!] Wordlist required. Use -w <path>{Color.RESET}")
            sys.exit(1)
        mode_single(args)
        return

    # Mode: Batch
    if args.file:
        if not args.wordlist:
            print(f"{Color.RED}[!] Wordlist required. Use -w <path>{Color.RESET}")
            sys.exit(1)
        mode_batch(args)
        return

    # Nothing provided
    parser.print_help()


if __name__ == "__main__":
    main()
