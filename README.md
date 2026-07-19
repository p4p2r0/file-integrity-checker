# File Integrity Checker

An integrity checker that detects changes to data in files.

## How

1. **Baseline creation**: The first time a file is checked, its SHA-256 hash is stored in `hashes.json` as the trusted baseline.
2. **Verification**: On every later check, the current hash is recomputed and compared against the baseline. A match reports `[OK]`; a mismatch reports `[FAILED]` with both the old and new hash.
3. **Manual comparison**: `--hash` checks a file against a specific hash you provide, without touching the stored baseline.
4. **Baseline updates**: `--update` accepts a changed file's new hash as the baseline instead of reporting a failure.
5. **Logging**: Every check, update, and removal is timestamped in `integrity.log`.

## Why

Files change for many reasons: malware, misconfiguration, accidental edits, unauthorized access. A changed hash means changed content, unlike timestamps or file size, which can be altered without touching the actual data. This project checks that at a small scale, for personal systems, dotfiles, scripts, or any file where a change needs to be caught immediately.

## Usage
```
usage: main.py [-h] [-r] [--hash SHA256] [-u] [--view-hashes] [--view-log] [--remove-hash INDEX] [--clear-hashes] [path ...]

positional arguments:
  path                 file(s) or folder(s) to verify

options:
  -h, --help           show this help message and exit
  -r, --recursive      recursively scan directories
  --hash SHA256        compare a single file against the supplied SHA-256 hash
  -u, --update         accept current file hash as the new baseline
  --view-hashes        display stored hashes
  --view-log           display the log file
  --remove-hash INDEX  remove a stored hash by index
  --clear-hashes       delete all stored hashes
```

## Installation

Prerequisites: Python 3.9+.

```bash
git clone https://github.com/p4p2r0/file-integrity-checker.git
cd file-integrity-checker
python main.py
```

## License

This project is licensed under the MIT License.
