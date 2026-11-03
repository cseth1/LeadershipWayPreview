#!/usr/bin/env python3
"""Update the two toolkit pages while preserving the published site exactly."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import quote

from resource_sheet import render_resource_sheets

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {'toolkit.html', 'aggie-ux/toolkit.html', 'versions/resource-sheet.css'}


def fingerprint(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output already exists; use a clean output directory')
    manifest = json.loads((ROOT / '.github/copilot-preservation.json').read_text())
    expected = dict(manifest['files'])
    for folder in ['copilot-lab', 'hroe-amazing-race']:
        for path in (ROOT / folder).rglob('*'):
            if path.is_file():
                expected[path.relative_to(ROOT).as_posix()] = fingerprint(path.read_bytes())

    def fetch(item):
        name, digest = item
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError(f'Invalid preserved path: {name}')
        data = subprocess.check_output([
            'curl', '--fail', '--silent', '--show-error', '--retry', '2',
            '--max-time', '60', '--header', 'Cache-Control: no-cache',
            manifest['site_url'] + quote(name),
        ])
        if fingerprint(data) != digest:
            raise ValueError(f'Published file changed; review before deploying: {name}')
        return name, data

    with ThreadPoolExecutor(max_workers=8) as executor:
        captured = dict(executor.map(fetch, expected.items()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='toolkit-stage-', dir=args.output.parent) as temp:
        staged = Path(temp) / 'site'
        for name, data in captured.items():
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        render_resource_sheets(staged)
        shutil.copyfile(ROOT / 'versions/resource-sheet.css', staged / 'versions/resource-sheet.css')
        actual = {p.relative_to(staged).as_posix(): fingerprint(p.read_bytes())
                  for p in staged.rglob('*') if p.is_file()}
        if set(actual) != set(expected) | TARGETS:
            raise ValueError('Unexpected files in staged release')
        for name in set(expected) - TARGETS:
            if actual[name] != expected[name]:
                raise ValueError(f'Unrelated published file changed: {name}')
        shutil.move(str(staged), str(args.output))
    print(f'Staged the two toolkit pages and stylesheet; preserved {len(set(expected) - TARGETS)} other published files')


if __name__ == '__main__':
    main()
