#!/usr/bin/env python3
"""Build both previews without changing either version's source files."""

from html import escape
from pathlib import Path
import posixpath
import re
import shutil
import argparse
import hashlib
import json
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
ORIGINAL = ROOT / "Aggie_Leadership_Website 2" / "dist"
AGGIE_UX = ROOT / "aggie-ux"
VERSIONS = (("original", ORIGINAL, ""), ("aggie-ux", AGGIE_UX, "aggie-ux"))


def relative_link(target, current_directory):
    return posixpath.relpath(target, current_directory or ".")


def switcher(current_version, page_name, current_directory):
    links = []
    for version, source, destination in VERSIONS:
        target_page = page_name if (source / page_name).is_file() else "index.html"
        target = posixpath.join(destination, target_page)
        href = escape(relative_link(target, current_directory), quote=True)
        label = "Version 1: Original" if version == "original" else "Version 2: Aggie UX"
        current = ' aria-current="true"' if version == current_version else ""
        links.append(f'<a class="preview-versions__link" href="{href}"{current}>{label}</a>')
    return (
        '\n<nav class="preview-versions" aria-label="Website versions">'
        '<div class="preview-versions__inner">'
        '<span class="preview-versions__label">Website versions</span>'
        '<div class="preview-versions__choices">'
        + "".join(links)
        + "</div></div></nav>\n"
    )


def build(workbook=None):
    # Validate before replacing output. Bad shared edits never reach deployment.
    if workbook:
        from content_workbook import read_xlsx
        content = read_xlsx(workbook)
    # Only this generated directory is replaced. The two source versions stay intact.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(ORIGINAL, OUTPUT)
    shutil.copytree(AGGIE_UX, OUTPUT / "aggie-ux")
    (OUTPUT / "versions").mkdir()
    shutil.copyfile(ROOT / "versions" / "version-switcher.css", OUTPUT / "versions" / "version-switcher.css")
    (OUTPUT / ".nojekyll").touch()

    count = 0
    for version, source, destination in VERSIONS:
        for source_file in sorted(source.glob("*.html")):
            html = source_file.read_text(encoding="utf-8")
            # Historical redirect pages keep their existing destination and behavior.
            header = re.search(r"<header\b", html, re.IGNORECASE)
            if header is None:
                continue
            if "preview-versions" in html:
                raise ValueError(f"Source already contains a version switcher: {source_file}")
            html = html[:header.start()] + switcher(version, source_file.name, destination) + html[header.start():]
            css_href = relative_link("versions/version-switcher.css", destination)
            stylesheet = f'\n<link rel="stylesheet" href="{css_href}">\n'
            if html.lower().count("</head>") != 1:
                raise ValueError(f"Expected one head element in {source_file}")
            html = re.sub(r"</head>", stylesheet + "</head>", html, count=1, flags=re.IGNORECASE)
            (OUTPUT / destination / source_file.name).write_text(html, encoding="utf-8")
            count += 1
    print(f"Built {count} pages with version navigation in {OUTPUT}")
    if workbook:
        from content_workbook import render_content
        counts = render_content(OUTPUT, content)
        print(f"Applied workbook content: {counts}")
        (OUTPUT / 'content-sync.json').write_text(json.dumps({
            'source': 'Excel workbook',
            'workbookSha256': hashlib.sha256(workbook.read_bytes()).hexdigest(),
            'builtAt': datetime.now(timezone.utc).isoformat(),
            **counts,
        }, indent=2) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--workbook', type=Path, help='Shared master workbook or a local validation copy')
    args = parser.parse_args()
    build(args.workbook)
