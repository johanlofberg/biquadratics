"""Create a deterministic standalone archive and refresh SHA256SUMS.txt."""
import argparse
import hashlib
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("destination", type=Path)
args = parser.parse_args()
top = ["reproduce.py", "README.md", "METHODS.md", "CLAIMS.md",
       "SOURCE_PROVENANCE.json", "pyproject.toml", "CITATION.cff",
       "LICENSE", ".gitignore", ".gitattributes", "RELEASE_VALIDATION.json"]
files = [root / name for name in top if (root / name).is_file()]
patterns = {
    "sodn": ("*.py",), "scripts": ("*.py", "*.cpp"),
    "tests": ("*.py",), "paper": ("*.tex", "*.pdf", "*.md"),
    "results": ("*.json",), "witnesses": ("*.json",),
    "certificates": ("*.json",), ".github/workflows": ("*.yml",),
}
for folder, suffixes in patterns.items():
    for pattern in suffixes:
        files.extend((root / folder).glob(pattern))
files = sorted(set(files), key=lambda p: p.relative_to(root).as_posix())
manifest = root / "SHA256SUMS.txt"
manifest.write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " +
                    p.relative_to(root).as_posix() + "\n" for p in files),
                    encoding="utf-8", newline="\n")
files.append(manifest)
args.destination.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(args.destination, "w", compression=zipfile.ZIP_DEFLATED,
                     compresslevel=9) as archive:
    for path in sorted(files, key=lambda p: p.relative_to(root).as_posix()):
        info = zipfile.ZipInfo("second_order_zarankiewicz_numbers/" +
                              path.relative_to(root).as_posix(),
                              date_time=(2026, 9, 5, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        archive.writestr(info, path.read_bytes(), compresslevel=9)
print("Archived", len(files), "files in", args.destination.resolve())
print("ZIP SHA256:", hashlib.sha256(args.destination.read_bytes()).hexdigest())
