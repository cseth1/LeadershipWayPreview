#!/usr/bin/env python3
"""Extract the existing website into an editable workbook seed and stable bindings."""
import hashlib
import json
import re
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {"Original": "Aggie_Leadership_Website 2/dist", "Aggie UX": "aggie-ux"}
STAGES = {"start-at-am.html": "Start at A&M", "lead-yourself.html": "Lead Yourself", "lead-people.html": "Lead People", "lead-teams.html": "Lead Teams", "lead-across-am.html": "Lead Across A&M", "develop-others.html": "Develop Others"}
NAMES = {"Grow your skills": "Lead Yourself", "Lead people": "Lead People", "Lead across A&M": "Lead Across A&M", "Develop others": "Develop Others"}
EXTRA = {"E002": ["Lead Teams"], "E003": ["Lead People", "Lead Teams"], "E004": ["Lead Teams"], "E005": ["Lead Teams"], "E006": ["Lead People"], "E007": ["Lead Teams"], **{k: ["Lead Teams"] for k in ["E011", "E012", "E013", "E015", "E016", "E017", "E027", "E033"]}}
TOPICS = {"New supervisors": ["Start at A&M", "Lead People"], "Communication and feedback": ["Lead Yourself", "Lead People", "Lead Teams"], "Trust and teamwork": ["Lead People", "Lead Teams", "Lead Across A&M"], "Performance and accountability": ["Lead People", "Lead Teams"], "Coaching and mentoring": ["Lead Yourself", "Lead People", "Lead Teams", "Develop Others"], "Change and adaptability": ["Lead Yourself", "Lead Teams", "Lead Across A&M"], "Professional growth": ["Lead Yourself", "Develop Others"], "Digital skills": ["Lead Yourself"]}

def cls(name):
    return f"contains(concat(' ',normalize-space(@class),' '),' {name} ')"

def strings(path):
    return {name: json.loads(value) for name, value in re.findall(r"window\.(\w+)=(.*?);(?:\n|$)", path.read_text())}

def text(el):
    return " ".join(el.text_content().split())

def extract():
    data = {**strings(ROOT / "aggie-ux/data.js"), **strings(ROOT / "aggie-ux/toolkit-data.js")}
    courses = {r["id"]: r for r in data["COURSES"]}
    programs = []
    for r in data["CATALOG"]:
        item = dict(r, publish="Yes", coursePage="Yes" if r["id"] in courses else "No")
        item["journeyStages"] = list(dict.fromkeys([NAMES.get(s,s) for s in r["stages"]] + EXTRA.get(r["id"],[])))
        item["area"] = courses.get(r["id"],{}).get("area", "")
        item["sortHours"] = courses.get(r["id"],{}).get("sortHours")
        programs.append(item)
    mapping = (ROOT / "aggie-ux/journey-map.js").read_text()
    selected = json.loads(re.search(r"const selectedResources=(\{.*?\});", mapping).group(1))
    resources = [dict(r, publish="Yes", journeyStages=list(dict.fromkeys(TOPICS.get(r["topic"],[]) + selected.get(r["id"],[])))) for r in data["TOOLKIT"]]
    records = {r["id"]: r for r in programs + resources}
    url_map = {r["url"]: r["id"] for r in resources}
    bindings = {"schemaVersion": 1, "files": {}, "groups": {}, "texts": {}, "links": {}}
    featured, page_text, links = [], [], []
    for edition, directory in VERSIONS.items():
        for file in sorted((ROOT / directory).glob("*.html")):
            src = file.read_text()
            doc = html.fromstring(src)
            tree = doc.getroottree()
            if not doc.xpath("//header"):
                continue
            path = file.relative_to(ROOT).as_posix()
            bindings["files"][path] = hashlib.sha256(src.encode()).hexdigest()
            managed = []
            if edition == "Aggie UX":
                # Complete catalog lists are rebuilt, so additions/removals are reflected too.
                for container in doc.xpath(f"//*[{cls('details-collection__container')}]"):
                    if any(el.get("id", "").removeprefix("related-").removeprefix("course-").upper() in records for el in container.findall("details")):
                        managed.append(container)
            if file.name in STAGES:
                groups = [("Learning", f"//*[@id='learn']//*[{cls('learning-cards')}]/article", "original-program"), ("Resources", f"//*[@id='tools']//*[{cls('stage-tool-grid')}]/article", "original-resource")] if edition == "Original" else [("Learning", f"//*[@id='learn']//*[{cls('standard-flow')}]/*[{cls('card')}]", "ux-program"), ("Resources", f"//*[@id='tools']//*[{cls('standard-flow')}]/*[{cls('card')}]", "ux-resource")]
                for section, xpath, style in groups:
                    cards = doc.xpath(xpath)
                    if not cards:
                        raise ValueError(f"Missing feature group {path}/{section}")
                    parent = cards[0].getparent()
                    group_id = f"{edition}/{file.name}/{section}"
                    bindings["groups"][group_id] = {"path": path, "xpath": tree.getpath(parent), "style": style}
                    managed.append(parent)
                    for order, card in enumerate(cards,1):
                        if style == "original-program":
                            item_id = card.xpath(".//*[@data-opportunity]/@data-opportunity")[0]
                        elif style == "original-resource":
                            item_id = url_map[card.xpath(".//h3/a/@href")[0]]
                        else:
                            item_id = card.xpath(".//a/@href")[0].split("#")[-1].upper()
                        title = text(card.xpath(".//h3")[0])
                        desc = text(card.xpath(f".//*[{cls('card__content')}]/p")[0]) if edition == "Aggie UX" else text(card.xpath("./p[not(@class)]")[0])
                        featured.append({"Feature ID": f"F{len(featured)+1:03}", "Version": edition, "Page": file.name, "Section": section, "Record ID": item_id, "Order": order, "Title override": "" if title == records[item_id]["title"] else title, "Description override": "" if desc == records[item_id]["description"] else desc})
            def excluded(node):
                return any(node == m or m in node.iterancestors() for m in managed) or any(a.tag in {"script", "style", "svg", "select", "option", "nav"} for a in [node,*node.iterancestors()])
            # Main body text and document metadata. Navigation/visual styling stay in HTML.
            nodes = doc.xpath("//main//* | //title | //meta[@name='description']")
            for node in nodes:
                if not isinstance(node.tag,str) or excluded(node):
                    continue
                section = next((a.get("id") for a in [node,*node.iterancestors()] if a.tag == "section" and a.get("id")), "Page introduction")
                for part in (["content"] if node.tag == "meta" else ["text", "tail"]):
                    raw = node.get("content") if part == "content" else getattr(node,part)
                    if not raw or not raw.strip() or (part == "tail" and (node.getparent() is None or excluded(node.getparent()))):
                        continue
                    key = f"P{len(page_text)+1:04}"
                    bindings["texts"][key] = {"path": path, "xpath": tree.getpath(node), "part": part, "original": raw}
                    page_text.append({"Text ID": key, "Version": edition, "Page": file.name, "Section": section, "Element": node.tag + (" following text" if part == "tail" else ""), "Text": raw.strip()})
                if node.tag == "a" and node.get("href"):
                    key = f"L{len(links)+1:04}"
                    bindings["links"][key] = {"path": path, "xpath": tree.getpath(node), "original": node.get("href")}
                    links.append({"Link ID": key, "Version": edition, "Page": file.name, "Section": section, "Link label (reference)": text(node), "URL": node.get("href")})
    seed = {"schemaVersion": 1, "sourceCommit": "67daca15014815655b831f934c0cde566b063e6e", "Programs and Courses": programs, "Resources": resources, "Featured Content": featured, "Page Text": page_text, "Page Links": links, "VALUES": data["VALUES"], "PRINCIPLES": data["PRINCIPLES"]}
    (ROOT / "content").mkdir(exist_ok=True)
    for name,obj in [("baseline.json",seed),("bindings.json",bindings)]:
        (ROOT / "content" / name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:len(v) for k,v in seed.items() if isinstance(v,list)},indent=2))

if __name__ == "__main__":
    extract()
