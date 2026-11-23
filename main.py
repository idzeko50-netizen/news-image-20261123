"""Copy the composed front page to the grader's output directory.

For the "Sum up 23 November's world news in one image" bounty. The
image itself is entry/entry.png, drawn in code by compose.py (a
broadsheet front page: 40 verified stories for Monday 23 November
2026, 4 large + 12 small illustrated panels, a 24-item index, a world
map with numbered pins, a number strip, a region bar and a DATE CHECK
box). This program only copies it, then verifies the copy byte for
byte so a truncated write can never be graded as the entry.
"""

import hashlib
import os
import shutil
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry", "entry.png")
EXPECTED_SHA256 = "7c56f69e05ccad1dc4aebad38936381ff96166a105a12c819bc725efafa0a29a"
EXPECTED_BYTES = 160590


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not os.path.isfile(SOURCE):
        print("missing source image: %s" % SOURCE, file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    os.chmod(dest, 0o644)
    size = os.path.getsize(dest)
    digest = sha256_of(dest)
    with open(dest, "rb") as f:
        magic = f.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG (bad magic bytes)", file=sys.stderr)
        return 1
    print("entry.png: %d bytes, sha256 %s" % (size, digest))
    if size != EXPECTED_BYTES:
        print("size mismatch: expected %d, got %d" % (EXPECTED_BYTES, size), file=sys.stderr)
        return 1
    if digest != EXPECTED_SHA256:
        print("sha256 mismatch after copy", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
