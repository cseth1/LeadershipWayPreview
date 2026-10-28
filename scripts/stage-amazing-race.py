#!/usr/bin/env python3
"""Add Amazing Race to exact copies of the published site; never rebuild leadership."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".github" / "copilot-preservation.json"
RACE = "hroe-amazing-race/index.html"


def fingerprint(data):
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def download(url):
    return subprocess.check_output([
        "curl", "--fail", "--silent", "--show-error", "--retry", "2",
        "--max-time", "60", "--header", "Cache-Control: no-cache", url,
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-live", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    files = dict(manifest["files"])
    files["copilot-lab/index.html"] = fingerprint((ROOT / "copilot-lab/index.html").read_bytes())
    source = (ROOT / RACE).read_bytes()
    if not source or b"HROE Amazing Race" not in source:
        raise ValueError("Expected the HROE Amazing Race HTML source")
    for name in files:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or name.startswith("hroe-amazing-race/"):
            raise ValueError(f"Invalid preserved path: {name}")
    expected = dict(files)
    if args.verify_live:
        expected[RACE] = fingerprint(source)

    def fetch(item):
        name, digest = item
        data = download(manifest["site_url"] + quote(name))
        if fingerprint(data) != digest:
            raise ValueError(f"Published file differs from approved fingerprint: {name}")
        return name, data

    # Do not produce any deployable output if a published file changed or is missing.
    with ThreadPoolExecutor(max_workers=8) as executor:
        captured = dict(executor.map(fetch, expected.items()))
    if args.verify_live:
        print(f"Verified Amazing Race and all {len(files)} preserved published files")
        return

    output = ROOT / "_site"
    if output.exists():
        raise ValueError("Output already exists; use a clean checkout")
    with tempfile.TemporaryDirectory(prefix="amazing-race-stage-", dir=ROOT) as temporary:
        staged = Path(temporary) / "site"
        staged.mkdir()
        for name, data in captured.items():
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        destination = staged / RACE
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source)
        actual = {p.relative_to(staged).as_posix(): fingerprint(p.read_bytes())
                  for p in staged.rglob("*") if p.is_file()}
        if actual != {**files, RACE: fingerprint(source)}:
            raise ValueError("Staged output changes files outside Amazing Race")
        shutil.move(str(staged), str(output))
    print(f"Preserved {len(files)} published files byte-for-byte; added {RACE}")


if __name__ == "__main__":
    main()
