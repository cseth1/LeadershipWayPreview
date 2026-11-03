"""Render both toolkit pages as plain, complete resource tables at build time.

Run after optional workbook publishing so the table always reflects its catalog.
The source editions and workbook text bindings remain intact.
"""

from html import escape
import json
import re


def resource_main(records, main_id):
    rows = []
    for index, record in enumerate(records, 1):
        e = lambda key: escape(str(record.get(key, '')), quote=True)
        audience = record.get('audienceLabel') or '; '.join(record.get('audienceTags', []))
        rows.append(
            f'<tr id="{e("id").lower()}"><td class="sheet-number">{index}</td>'
            f'<th scope="row" class="sheet-resource"><a href="{e("url")}" target="_blank" rel="noopener">{e("title")}</a></th>'
            f'<td>{e("description")}</td><td>{e("topic")}</td><td>{e("type")}</td>'
            f'<td>{escape(audience)}</td><td>{e("owner")}</td><td>{e("access")}</td></tr>'
        )
    return f'''<main id="{main_id}" class="resource-sheet-page" tabindex="-1">
<div class="sheet-heading"><h1>Tools &amp; Resources</h1>
<p>Browse the complete resource list. Select a resource name to open it.</p></div>
<section id="library" aria-label="Resource library">
<div class="sheet-toolbar"><p><strong>{len(records)} resources</strong> <span>All resources shown</span></p>
<a class="sheet-download" href="leadership-resources.csv" download>Download spreadsheet (CSV)</a></div>
<p id="sheet-help" class="sheet-help">Scroll across for more columns. Resource links open in a new tab.</p>
<div class="sheet-scroll" role="region" aria-label="Tools and resources spreadsheet" aria-describedby="sheet-help" tabindex="0">
<table class="resource-sheet"><caption class="sheet-sr-only">Complete tools and resources library: {len(records)} resources</caption>
<colgroup><col class="col-number"><col class="col-resource"><col class="col-description"><col class="col-topic"><col class="col-format"><col class="col-audience"><col class="col-provider"><col class="col-access"></colgroup>
<thead><tr><th scope="col" class="sheet-number"><span aria-hidden="true">#</span><span class="sheet-sr-only">Row</span></th><th scope="col" class="sheet-resource">Resource</th><th scope="col">Description</th><th scope="col">Topic</th><th scope="col">Format</th><th scope="col">Audience</th><th scope="col">Provider</th><th scope="col">Access</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="sheet-note">Some resources require sign-in. External guidance supports learning and does not replace Texas A&amp;M policy. Check each provider for current access.</p>
</section></main>'''


def render_resource_sheets(output):
    for prefix, main_id, stylesheet in [('', 'main', 'versions/resource-sheet.css'), ('aggie-ux', 'main-content', '../versions/resource-sheet.css')]:
        folder = output / prefix
        data = (folder / 'toolkit-data.js').read_text(encoding='utf-8')
        records = json.loads(data.split('=', 1)[1].strip().rstrip(';'))
        path = folder / 'toolkit.html'
        page = path.read_text(encoding='utf-8')
        page, count = re.subn(r'<main\b[^>]*>.*?</main>', lambda _: resource_main(records, main_id), page, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'{path}: expected one main element')
        # The resource table is fully usable without JavaScript. Keep site navigation.
        page = re.sub(r'<script\b[^>]*src="(?:toolkit(?:-data)?\.js|journey-map\.js)[^"]*"[^>]*></script>', '', page)
        page = re.sub(r'<link\b[^>]*href="resource-hub\.css[^"]*"[^>]*>', '', page)
        page = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Browse all leadership tools and resources in one spreadsheet-style table.">', page)
        # Remove the original lower-page promotional section to keep the page compact.
        page = re.sub(r'<section class="about-concept">.*?</section>', '', page, flags=re.S)
        if 'resource-sheet.css' not in page:
            page = page.replace('</head>', f'<link rel="stylesheet" href="{stylesheet}"></head>')
        path.write_text(page, encoding='utf-8')
