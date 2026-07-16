# File Integrity Checker

A CLI tool that verifies file integrity using SHA-256 hashes.

## How

1. **Baseline creation**: The first time a file is checked, its SHA-256 hash is stored in `hashes.json` as the trusted baseline.
2. **Verification**: On every later check, the current hash is recomputed and compared against the baseline. A match reports `[OK]`; a mismatch reports `[FAILED]` with both the old and new hash.
3. **Manual comparison**: `--hash` checks a file against a specific hash you provide, without touching the stored baseline.
4. **Baseline updates**: `--update` accepts a changed file's new hash as the baseline instead of reporting a failure.
5. **Logging**: Every check, update, and removal is timestamped in `integrity.log`.

## Why

File integrity monitoring is a core control in security work. Malware often modifies system binaries or configs to persist or hide, and breach investigations frequently start by asking what changed, and when. Tools like Tripwire and OSSEC exist because of this, and hash-based baselining is the standard technique behind them: a changed hash means changed content, full stop, regardless of timestamps or file size which can be spoofed. This project applies that same principle at a small scale, useful for personal systems, dotfiles, scripts, or any file where an unexpected change is worth knowing about immediately.

## Usage
```bash
usage: main.py [-h] [-r] [--hash SHA256] [-u] [--view-hashes] [--view-log] [--remove-hash INDEX] [--clear-hashes] [path ...]

positional arguments:
  path                 File(s) or folder(s) to verify

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
