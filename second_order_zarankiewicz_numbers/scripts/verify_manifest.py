"""Verify every released file against SHA256SUMS.txt (standard library)."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
count = 0
for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
    digest, name = line.split("  ", 1)
    path = (root / name).resolve()
    if root not in path.parents:
        raise ValueError("Manifest path escapes the package: " + name)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise AssertionError("Checksum mismatch: " + name)
    count += 1
print("Verified", count, "released file checksums.")
