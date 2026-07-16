#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging
import hashlib
import json
import sys
import re

HASH_FILE = "hashes.json"
LOG_FILE = "integrity.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def parse():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="File Integrity Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "paths", nargs="*", metavar="path", help="File(s) or folder(s) to verify"
    )

    parser.add_argument(
        "-r", "--recursive", action="store_true", help="recursively scan directories"
    )

    parser.add_argument(
        "--hash",
        metavar="SHA256",
        help="compare a single file against the supplied SHA-256 hash",
    )

    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="accept current file hash as the new baseline"
    )

    parser.add_argument(
        "--view-hashes", action="store_true", help="display stored hashes"
    )

    parser.add_argument("--view-log", action="store_true", help="display the log file")

    parser.add_argument(
        "--remove-hash", type=int, metavar="INDEX", help="remove a stored hash by index"
    )

    parser.add_argument(
        "--clear-hashes", action="store_true", help="delete all stored hashes"
    )

    args = parser.parse_args()

    if args.hash and len(args.paths) != 1:
        parser.error("--hash requires exactly one file.")

    if args.hash and not re.fullmatch(r"[0-9a-fA-F]{64}", args.hash):
        parser.error("--hash must be a 64-character hex SHA-256 value.")

    return parser, args


def view_hashes():
    hashes = load_hashes()

    if not hashes:
        print("No stored hashes.")
        return

    for i, (path, h) in enumerate(hashes.items(), start=1):
        print(f"{i}.")
        print(f"Path: {path}")
        print(f"Hash: {h}\n")


def view_log():
    file = Path(LOG_FILE)

    if not file.exists():
        print("Log file does not exist.")
        return

    with open(file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            print(f"{i}: {line.rstrip()}")


def remove_hash(index):
    hashes = load_hashes()
    items = list(hashes.items())

    if index < 1 or index > len(items):
        print("Invalid index.")
        return

    path, _ = items[index - 1]
    del hashes[path]
    save_hashes(hashes)
    report("REMOVED", path)


def clear_hashes():
    save_hashes({})
    report("CLEARED", "all stored hashes")


def load_hashes():
    file = Path(HASH_FILE)
    if not file.exists():
        return {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=4)


def sha256(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)

    return h.hexdigest()


def verify_file(file, hashes, expected_hash=None, update=False):
    file = file.resolve()

    try:
        current_hash = sha256(file)
    except OSError as e:
        report("ERROR", file, logging.ERROR, f"\n  {e}")
        return

    if expected_hash:
        match = current_hash.lower() == expected_hash.lower()
        extra = f"\n  expected: {expected_hash}\n  current:  {current_hash}"
        report("OK" if match else "FAILED", file,
               logging.INFO if match else logging.WARNING,
               "" if match else extra)
        return

    key = str(file)

    if key not in hashes:
        hashes[key] = current_hash
        report("NEW", file, extra=f"\n  hash: {current_hash}")
        return

    match = hashes[key] == current_hash

    if match:
        report("OK", file)
        return

    if update:
        hashes[key] = current_hash
        report("UPDATED", file, extra=f"\n  new hash: {current_hash}")
        return

    extra = f"\n  old: {hashes[key]}\n  new: {current_hash}"
    report("FAILED", file, logging.WARNING, extra)


def verify_path(path, hashes, recursive=False, expected_hash=None, update=False):
    path = Path(path)

    if not path.exists():
        report("NOT FOUND", path, logging.WARNING)
        return

    if path.is_file():
        verify_file(path, hashes, expected_hash, update)
        return

    if expected_hash:
        print("--hash can only be used with a file.")
        return

    iterator = path.rglob("*") if recursive else path.iterdir()

    while True:
        try:
            file = next(iterator)
        except StopIteration:
            break
        except OSError as e:
            report("ERROR", path, logging.ERROR, f"\n  {e}")
            break

        if file.is_file():
            verify_file(file, hashes, update=update)


def report(tag, path, level=logging.INFO, extra=""):
    print(f"[{tag}] {path}{extra}")
    logging.log(level, f"{tag}: {path}{extra}")


def main():
    parser, args = parse()

    if (
        not args.paths
        and not args.view_hashes
        and not args.view_log
        and args.remove_hash is None
        and not args.clear_hashes
    ):
        parser.print_help()
        return

    if args.view_hashes:
        view_hashes()
        return

    if args.view_log:
        view_log()
        return

    if args.remove_hash is not None:
        remove_hash(args.remove_hash)
        return

    if args.clear_hashes:
        clear_hashes()
        return

    hashes = load_hashes()

    for path in args.paths:
        verify_path(
            path,
            hashes,
            recursive=args.recursive,
            expected_hash=args.hash,
            update=args.update
        )

    if not args.hash:
        save_hashes(hashes)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        logging.exception(e)
        print(f"Error: {e}")
        sys.exit(1)
