"""Validate the shared Excel file and render both website editions from its data."""
import csv
from datetime import datetime, timedelta
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import zipfile
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "content/schema.json").read_text())
BASELINE = json.loads((ROOT / "content/baseline.json").read_text())
BINDINGS = json.loads((ROOT / "content/bindings.json").read_text())
STAGES = {"start-at-am.html": "Start at A&M", "lead-yourself.html": "Lead Yourself", "lead-people.html": "Lead People", "lead-teams.html": "Lead Teams", "lead-across-am.html": "Lead Across A&M", "develop-others.html": "Develop Others"}
TOPICS = {"Change and adaptability", "Coaching and mentoring", "Communication and feedback", "Digital skills", "New supervisors", "Performance and accountability", "Professional growth", "Trust and teamwork"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def yes(value, context):
    if value not in {"Yes", "No"}:
        raise ValueError(f"{context}: choose Yes or No")
    return value == "Yes"

def safe_url(value, context, external=False):
    if not value or any(ord(c) < 32 for c in value) or "\\" in value:
        raise ValueError(f"{context}: enter a valid URL")
    parsed = urlparse(value)
    if parsed.scheme:
        if parsed.scheme not in {"http", "https", "mailto"} or (external and parsed.scheme == "mailto"):
            raise ValueError(f"{context}: unsupported link type")
        if parsed.scheme in {"http", "https"} and (not parsed.netloc or parsed.username or parsed.password):
            raise ValueError(f"{context}: invalid web address")
    elif external or value.startswith("//") or ".." in parsed.path.split("/"):
        raise ValueError(f"{context}: use a web address or a local page link")

def read_xlsx(filename):
    """Read literal cell values, including Excel/Office web dates and shared strings."""
    with zipfile.ZipFile(filename) as z:
        if sum(i.file_size for i in z.infolist()) > 80_000_000:
            raise ValueError("Workbook is unexpectedly large")
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        prop = wb.find("m:workbookPr", NS)
        epoch = datetime(1904,1,1) if prop is not None and prop.get("date1904") in {"1","true"} else datetime(1899,12,30)
        rels = {r.get("Id"):r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            shared=["".join(s.itertext()) for s in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        result={"VALUES":BASELINE["VALUES"],"PRINCIPLES":BASELINE["PRINCIPLES"]}
        for sheet in wb.findall("m:sheets/m:sheet",NS):
            name=sheet.get("name")
            if name not in SCHEMA:
                continue
            target=rels[sheet.get('{'+NS['r']+'}id')]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            xml=ET.fromstring(z.read(target)); grid={}
            for row in xml.findall('m:sheetData/m:row',NS):
                rownum=int(row.get('r')); cells={}
                for c in row.findall('m:c',NS):
                    ref=c.get('r'); col=0
                    for char in re.match('[A-Z]+',ref).group():col=col*26+ord(char)-64
                    if c.find('m:f',NS) is not None:
                        if rownum>=6:raise ValueError(f"{name}!{ref}: use a value, not a formula")
                        continue
                    kind=c.get('t'); v=c.find('m:v',NS)
                    raw=v.text if v is not None else None
                    if kind=='s':value=shared[int(raw)] if raw is not None else ''
                    elif kind=='inlineStr':value=''.join(c.find('m:is',NS).itertext())
                    elif kind=='e':raise ValueError(f"{name}!{ref}: Excel error")
                    elif kind=='b':value='Yes' if raw=='1' else 'No'
                    else:value=raw or ''
                    cells[col]=value
                grid[rownum]=cells
            headers={str(v).strip():k for k,v in grid.get(6,{}).items() if v}
            expected=[f[0] for f in SCHEMA[name]]
            if len(headers)!=len(expected) or set(headers)!=set(expected):
                raise ValueError(f"{name}: keep the original headers in row 6")
            rows=[]
            for n,cells in sorted(grid.items()):
                if n<7 or not any(str(v).strip() for v in cells.values()):continue
                record={}
                for label,key,kind in SCHEMA[name]:
                    value=str(cells.get(headers[label], '')).strip(); context=f"{name} row {n}, {label}"
                    if kind=='list':value=[v.strip() for v in value.split(';') if v.strip()]
                    elif kind=='bool':value=yes(value or 'No',context)
                    elif kind=='yesno':
                        value=value or 'No';yes(value,context)
                    elif kind=='number':
                        try:value=float(value) if value else None
                        except ValueError:raise ValueError(f"{context}: enter a number") from None
                    elif kind=='date':
                        try:
                            if re.fullmatch(r'\d+(\.\d+)?',value):value=(epoch+timedelta(days=float(value))).date().isoformat()
                            else:value=datetime.fromisoformat(value.replace('Z','+00:00')).date().isoformat() if value else ''
                        except ValueError:raise ValueError(f"{context}: enter an Excel date") from None
                    record[key]=value
                rows.append(record)
            result[name]=rows
        if set(SCHEMA)-set(result):raise ValueError('Missing worksheet: '+', '.join(sorted(set(SCHEMA)-set(result))))
    validate(result)
    return result

def validate(data):
    all_ids=set()
    for sheet in ['Programs and Courses','Resources']:
        if not data.get(sheet):raise ValueError(f'{sheet}: the catalog cannot be empty')
        for r in data[sheet]:
            id=r['id']
            if not re.fullmatch(r'[A-Z][A-Z0-9_-]+',id) or id in all_ids:raise ValueError(f'{sheet}: missing, invalid or duplicate Record ID {id!r}')
            all_ids.add(id);yes(r['publish'],id)
            if r['publish']=='No':continue
            for field in ['title','description','owner','type','scope','audienceLabel']:
                if not r[field]:raise ValueError(f'{id}: {field} is required')
            safe_url(r['url'],id,True)
            if r['scope'] not in {'Employees','Other'}:raise ValueError(f'{id}: Audience group must be Employees or Other')
            if r['scope']=='Employees' and not r['audienceTags']:raise ValueError(f'{id}: choose at least one employee audience filter')
            allowed_audiences={'Staff','Faculty','Supervisors','Students','External','System'}
            if set(r['audienceTags'])-allowed_audiences:raise ValueError(f'{id}: unsupported audience filter')
            if set(r['journeyStages'])-set(STAGES.values()):raise ValueError(f'{id}: unsupported journey stage')
            if r['checked']:
                try:datetime.strptime(r['checked'],'%Y-%m-%d')
                except ValueError:raise ValueError(f'{id}: invalid source review date') from None
            if sheet=='Resources':
                if r['topic'] not in TOPICS:raise ValueError(f'{id}: choose an existing resource topic')
                safe_url(r['source'],id+' Source URL',True)
            else:
                yes(r['coursePage'],id)
                if r['type'] not in {'Course','Program','Community','Resource'}:raise ValueError(f'{id}: unsupported program type')
                if r['coursePage']=='Yes' and (r['type']!='Course' or r['scope']!='Employees' or not r['area']):raise ValueError(f'{id}: a course-page item needs Course type, Employees audience and Course area')
                if r['sortHours'] is not None and (not isinstance(r['sortHours'],(float,int)) or not 0<=r['sortHours']<100000):raise ValueError(f'{id}: Sort hours must be a non-negative number')
    features=set()
    for r in data['Featured Content']:
        key=r['Feature ID']; group='/'.join(r[k] for k in ['Version','Page','Section'])
        if not key or key in features:raise ValueError('Missing or duplicate Feature ID')
        features.add(key)
        if group not in BINDINGS['groups']:raise ValueError(f'{key}: unknown featured page or section')
        if r['Record ID'] not in all_ids:raise ValueError(f'{key}: Record ID does not exist')
        if r['Order'] is None or r['Order']<1 or r['Order']!=int(r['Order']):raise ValueError(f'{key}: Order must be a positive whole number')
        resource_ids={x['id'] for x in data['Resources']}
        if (r['Section']=='Resources')!=(r['Record ID'] in resource_ids):raise ValueError(f'{key}: item belongs in the other featured section')
    for sheet,key,kind in [('Page Text','Text ID','texts'),('Page Links','Link ID','links')]:
        ids=[r[key] for r in data[sheet]]
        if len(ids)!=len(set(ids)) or set(ids)!=set(BINDINGS[kind]):raise ValueError(f'{sheet}: keep every original ID once; edit values instead of deleting rows')
        if kind=='links':
            for r in data[sheet]:safe_url(r['URL'],r[key])

def cls(name):return f"contains(concat(' ',normalize-space(@class),' '),' {name} ')"
def esc(value):return escape(str(value or ''),quote=True)
def topic_file(topic):return 'tools-'+topic.lower().replace(' ','-')+'.html'
def detail(r,resource=False,related=False,course=False):
    title=esc(r['title']); desc=esc(r['description']); key=('course-' if course else '')+r['id'].lower()
    if related:return f'<details class="details" id="related-{key}"><summary><span class="superhead">{esc(r["type"])}</span><span class="ns-h3">{title}</span></summary><div class="details__content"><p>{desc}</p><a class="link--cta" href="programs.html#{key}">View provider &amp; eligibility</a></div></details>'
    pairs=[('Provider','owner'),('Access','access'),('Who it is for','audienceLabel'),('Source reviewed','checked')] if resource else [('Provider','owner'),('Who it is for','audienceLabel'),('Eligibility','eligibility'),('Format','delivery'),('Time','duration'),('Cost','cost'),('Status at source review','status'),('Source reviewed','checked')]
    dl=''.join(f'<dt>{label}</dt><dd>{esc(r[field])}</dd>' for label,field in pairs)
    # Source notes are now carried through to the static edition as well.
    notes=f'<p class="source-note">{esc(r["notes"])}</p>' if r.get('notes') else ''
    return f'<details class="details" id="{key}"><summary><span class="superhead">{esc(r["type"] if resource else r["audienceLabel"])}</span><span class="ns-h3">{title}</span></summary><div class="details__content"><p>{desc}</p><dl>{dl}</dl>{notes}<a class="btn btn--primary" href="{esc(r["url"])}">{"Open resource" if resource else "Visit the provider"}</a></div></details>'

def feature_card(r,f,style):
    title=esc(f['Title override'] or r['title']);desc=esc(f['Description override'] or r['description']);url=esc(r['url']);id=esc(r['id'])
    if style.startswith('ux-'):
        resource=style.endswith('resource');href=(topic_file(r['topic']) if resource else 'programs.html' if r['scope']=='Employees' else 'other-opportunities.html')+'#'+r['id'].lower();label='View resource' if resource else 'View details'
        icon='<div class="icon-wrapper"><svg aria-hidden="true" focusable="false"><use href="#aux_book-open"></use></svg></div>' if resource else ''
        return f'<div class="card">{icon}<div class="card__content"><div class="heading-group"><span class="superhead">{esc(r["type"])}</span><h3>{title}</h3></div><p>{desc}</p><a aria-label="{label}: {title}" class="link--cta-leading" href="{esc(href)}">{label}</a></div></div>'
    if style=='original-program':
        return f'<article class="learning-card"><span class="resource-type">{esc(r["type"])}</span><p class="provider">{esc(r["owner"])}</p><h3>{title}</h3><p>{desc}</p><p class="small"><strong>Who it serves:</strong> {esc(r["eligibility"])}</p><button class="detail-button" data-opportunity="{id}">View offering details<span class="sr-only">: {title}</span></button><p class="source-date">Source reviewed {esc(r["checked"])} · <a href="{url}" target="_blank" rel="noopener">Provider website</a></p></article>'
    source=f'<p class="source-date"><a href="{esc(r["source"])}" target="_blank" rel="noopener">Source collection</a></p>' if r['source']!=r['url'] else ''
    return f'<article><div class="resource-meta"><span class="resource-type">{esc(r["type"])}</span><span>{esc(r["origin"])}</span></div><h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3><p>{desc}</p><p class="resource-credit">{esc(r["owner"])} · {esc(r["audienceLabel"])}</p><a class="text-link" href="{url}" target="_blank" rel="noopener">Explore this resource<span class="sr-only">: {title}</span> →</a>{source}</article>'

def replace_children(node,markup,keep_button=False):
    for child in list(node):
        if not (keep_button and child.tag=='button'):node.remove(child)
    node.text=None
    if not markup:markup='<p>No published items are currently listed.</p>'
    for el in html.fragments_fromstring(markup):node.append(el)

def render_content(output,data):
    import hashlib
    validate(data)
    for file,expected in BINDINGS['files'].items():
        if hashlib.sha256((ROOT/file).read_text().encode()).hexdigest()!=expected:raise ValueError(f'{file}: source layout changed; refresh workbook bindings before publishing')
    programs=[r for r in data['Programs and Courses'] if r['publish']=='Yes']
    resources=[r for r in data['Resources'] if r['publish']=='Yes']
    records={r['id']:r for r in programs+resources}
    files={path:html.fromstring((output/('aggie-ux/'+Path(path).name if path.startswith('aggie-ux/') else Path(path).name)).read_text()) for path in BINDINGS['files']}
    # Resolve every binding before replacing containers. All edited values are plain text.
    for sheet,id_field,kind,value_field in [('Page Text','Text ID','texts','Text'),('Page Links','Link ID','links','URL')]:
        for row in data[sheet]:
            b=BINDINGS[kind][row[id_field]];nodes=files[b['path']].xpath(b['xpath'])
            if len(nodes)!=1:raise ValueError(f'{row[id_field]}: source binding no longer matches')
            node=nodes[0];value=row[value_field]
            if kind=='links':node.set('href',value)
            elif b['part']=='content':node.set('content',value)
            else:
                raw=b['original'];prefix=raw[:len(raw)-len(raw.lstrip())];suffix=raw[len(raw.rstrip()):]
                setattr(node,b['part'],prefix+value+suffix)
    for group,b in BINDINGS['groups'].items():
        rows=sorted([r for r in data['Featured Content'] if '/'.join(r[k] for k in ['Version','Page','Section'])==group],key=lambda r:(r['Order'],r['Feature ID']))
        rows=[r for r in rows if r['Record ID'] in records]
        node=files[b['path']].xpath(b['xpath'])[0]
        replace_children(node,''.join(feature_card(records[f['Record ID']],f,b['style']) for f in rows))
    for path,doc in files.items():
        file=Path(path).name
        if not path.startswith('aggie-ux/'):
            # New providers, areas, types and origins must be selectable immediately.
            for select_id,rows,field in [('course-provider',[r for r in programs if r['coursePage']=='Yes'],'owner'),('course-area',[r for r in programs if r['coursePage']=='Yes'],'area'),('resource-type',resources,'type'),('resource-origin',resources,'origin')]:
                found=doc.xpath('//*[@id=$id]',id=select_id)
                if found:
                    select=found[0]
                    for option in list(select)[1:]:select.remove(option)
                    for value in sorted({r[field] for r in rows if r[field]}):
                        option=html.Element('option');option.text=value;select.append(option)
        if path.startswith('aggie-ux/'):
            targets={}
            if file=='programs.html':
                for section,kind in [('courses','Course'),('programs','Program'),('communities','Community'),('resources','Resource')]:targets[section]=[r for r in programs if r['scope']=='Employees' and r['type']==kind]
            elif file=='other-opportunities.html':targets['other-listings']=[r for r in programs if r['scope']=='Other']
            elif file=='professional-development.html':targets['courses']=[r for r in programs if r['coursePage']=='Yes']
            elif file.startswith('tools-'):targets['resources']=[r for r in resources if topic_file(r['topic'])==file]
            elif file in STAGES:
                selected={r['Record ID'] for r in data['Featured Content'] if r['Version']=='Aggie UX' and r['Page']==file and r['Section']=='Learning'}
                targets['more-learning']=[r for r in programs if r['scope']=='Employees' and STAGES[file] in r['journeyStages'] and r['id'] not in selected]
            for section,rows in targets.items():
                nodes=doc.xpath(f"//*[@id='{section}']//*[{cls('details-collection__container')}]")
                if len(nodes)!=1:raise ValueError(f'{file}: missing content section {section}')
                replace_children(nodes[0],''.join(detail(r,file.startswith('tools-'),section=='more-learning',file=='professional-development.html') for r in rows),True)
        dest=output/('aggie-ux/'+file if path.startswith('aggie-ux/') else file)
        dest.write_text('<!DOCTYPE html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
    # Each edition receives identical catalog data and public downloads.
    for folder in [output,output/'aggie-ux']:
        def clean(r):return {k:v for k,v in r.items() if k not in {'publish','coursePage'} and (k not in {'area','sortHours'} or r.get('coursePage')=='Yes')}
        catalog=[clean(r) for r in programs]; toolkit=[clean(r) for r in resources]
        entries={'CATALOG':catalog,'VALUES':data['VALUES'],'PRINCIPLES':data['PRINCIPLES'],'RESEARCH_DOWNLOAD':'leadership-opportunities.csv','COURSES':[clean(r) for r in programs if r['coursePage']=='Yes']}
        (folder/'data.js').write_text(''.join(f'window.{name}={json.dumps(value,ensure_ascii=False)};\n' for name,value in entries.items()))
        (folder/'toolkit-data.js').write_text('window.TOOLKIT='+json.dumps(toolkit,ensure_ascii=False)+';\n')
        (folder/'journey-map.js').write_text("'use strict';\nwindow.JourneyMapping=Object.freeze({canonical:value=>({'Grow your skills':'Lead Yourself','Lead people':'Lead People','Lead across A&M':'Lead Across A&M','Develop others':'Develop Others'}[value]||value)});\n")
        for filename,rows in [('leadership-opportunities.csv',catalog),('leadership-resources.csv',toolkit)]:
            keys=list(dict.fromkeys(k for r in rows for k in r))
            with (folder/filename).open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
                for r in rows:writer.writerow({k:'; '.join(v) if isinstance(v,list) else v for k,v in r.items()})
    courses_js=output/'courses.js'
    courses_js.write_text(courses_js.read_text().replace("r.id==='E005'?'Confirm with provider':",''))
    return {'programs':len(programs),'courses':sum(r['coursePage']=='Yes' for r in programs),'resources':len(resources),'featured':len(data['Featured Content'])}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('workbook');args=parser.parse_args()
    data=read_xlsx(args.workbook)
    print('Workbook validated: '+', '.join(f'{len(data[k])} {k}' for k in SCHEMA))
