"""Regression tests for workbook publishing. Run with Python and lxml."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from lxml import html
import content_workbook as content

spec=importlib.util.spec_from_file_location('build_pages',Path(__file__).with_name('build-pages.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class ContentTests(unittest.TestCase):
    def setUp(self):self.data=copy.deepcopy(content.BASELINE)

    def test_baseline_valid(self):content.validate(self.data)

    def test_rejects_duplicate_and_invalid_inputs(self):
        for field,value in [('id','E002'),('url','javascript:alert(1)'),('publish','Maybe'),('checked','not-a-date'),('journeyStages',['Not a stage'])]:
            with self.subTest(field=field):
                d=copy.deepcopy(self.data);d['Programs and Courses'][0][field]=value
                with self.assertRaises(ValueError):content.validate(d)

    def test_incomplete_unpublished_draft_allowed(self):
        r=copy.deepcopy(self.data['Programs and Courses'][0]);r.update(id='E999',publish='No',title='',url='',description='',audienceTags=[])
        self.data['Programs and Courses'].append(r);content.validate(self.data)

    def test_page_binding_missing_rejected(self):
        self.data['Page Text'].pop()
        with self.assertRaises(ValueError):content.validate(self.data)

    def test_added_changed_hidden_and_reclassified_records(self):
        with tempfile.TemporaryDirectory() as temp:
            builder.OUTPUT=Path(temp)/'site';builder.build()
            first=self.data['Programs and Courses'][0]
            first.update(title='Updated <course> & title',description='New description from workbook',duration='12 hours',url='https://example.edu/updated')
            new=copy.deepcopy(first);new.update(id='E999',title='New workbook course',owner='New provider',area='New area',journeyStages=['Start at A&M'])
            self.data['Programs and Courses'].append(new)
            self.data['Programs and Courses'][1]['publish']='No'
            self.data['Resources'][0].update(title='Updated toolkit title',topic='Digital skills')
            self.data['Resources'][1]['publish']='No'
            newtool=copy.deepcopy(self.data['Resources'][0]);newtool.update(id='T999',title='New workbook toolkit')
            self.data['Resources'].append(newtool)
            label=next(r for r in self.data['Page Text'] if r['Version']=='Aggie UX' and r['Page']=='index.html' and r['Element']=='h1')
            label['Text']='Updated main heading <test>'
            content.render_content(builder.OUTPUT,self.data)
            for prefix in ['', 'aggie-ux/']:
                js=(builder.OUTPUT/prefix/'data.js').read_text();tool=(builder.OUTPUT/prefix/'toolkit-data.js').read_text()
                self.assertIn('E999',js);self.assertNotIn('"id": "E002"',js);self.assertIn('T999',tool);self.assertNotIn('"id": "T002"',tool)
                self.assertIn('12 hours',js)
                self.assertIn('E999',(builder.OUTPUT/prefix/'leadership-opportunities.csv').read_text())
            programs=html.fromstring((builder.OUTPUT/'aggie-ux/programs.html').read_text())
            self.assertEqual(len(programs.xpath('//*[@id="e999"]')),1)
            self.assertEqual(programs.xpath('//*[@id="e001"]//span[@class="ns-h3"]')[0].text,'Updated <course> & title')
            self.assertFalse(programs.xpath('//course'))
            self.assertFalse(programs.xpath('//*[@id="e002"]'))
            courses=html.fromstring((builder.OUTPUT/'aggie-ux/professional-development.html').read_text())
            self.assertEqual(len(courses.xpath('//*[@id="course-e999"]')),1)
            original_courses=html.fromstring((builder.OUTPUT/'professional-development.html').read_text())
            self.assertIn('New provider',original_courses.xpath('//*[@id="course-provider"]/option/text()'))
            self.assertIn('New area',original_courses.xpath('//*[@id="course-area"]/option/text()'))
            newtopic=html.fromstring((builder.OUTPUT/'aggie-ux/tools-digital-skills.html').read_text())
            oldtopic=html.fromstring((builder.OUTPUT/'aggie-ux/tools-new-supervisors.html').read_text())
            self.assertTrue(newtopic.xpath('//*[@id="t001"]'));self.assertFalse(oldtopic.xpath('//*[@id="t001"]'))
            self.assertTrue(newtopic.xpath('//*[@id="t999"]'))
            stage=html.fromstring((builder.OUTPUT/'aggie-ux/start-at-am.html').read_text())
            self.assertTrue(stage.xpath('//*[@id="related-e999"]'))
            self.assertIn('tools-digital-skills.html#t001',html.tostring(stage).decode())
            home=html.fromstring((builder.OUTPUT/'aggie-ux/index.html').read_text())
            self.assertEqual(home.xpath('//h1')[0].text_content(),'Updated main heading <test>')
            self.assertFalse(home.xpath('//test'))

    def test_baseline_catalog_and_internal_anchors(self):
        with tempfile.TemporaryDirectory() as temp:
            builder.OUTPUT=Path(temp)/'site';builder.build();content.render_content(builder.OUTPUT,self.data)
            for filename in ['programs.html','other-opportunities.html','professional-development.html']:
                source=html.fromstring((content.ROOT/'aggie-ux'/filename).read_text())
                actual=html.fromstring((builder.OUTPUT/'aggie-ux'/filename).read_text())
                before={e.get('id') for e in source.xpath('//details')};after={e.get('id') for e in actual.xpath('//details')}
                self.assertEqual(before,after,filename)
            docs={str(p.relative_to(builder.OUTPUT)):html.fromstring(p.read_text()) for p in builder.OUTPUT.rglob('*.html')}
            from urllib.parse import urlsplit,unquote
            import posixpath
            for file,doc in docs.items():
                for href in doc.xpath('//a/@href'):
                    u=urlsplit(href)
                    if u.scheme or u.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(file),unquote(u.path))) if u.path else file
                    if target in docs and u.fragment:
                        fragment=unquote(u.fragment)
                        # V1 library/search hashes are handled by existing JavaScript.
                        self.assertTrue(docs[target].xpath('//*[@id=$id]',id=fragment),f'{file}: {href}')

    def test_delivered_workbook_matches_every_seed_value(self):
        workbook=content.ROOT/'content/Leadership_Website_Content.xlsx'
        if not workbook.exists():self.skipTest('Starter workbook not copied yet')
        parsed=content.read_xlsx(workbook)
        for name,fields in content.SCHEMA.items():
            self.assertEqual(len(parsed[name]),len(self.data[name]))
            for actual,expected in zip(parsed[name],self.data[name]):
                for _,key,_ in fields:self.assertEqual(actual[key],expected.get(key),f'{name}: {key}')

if __name__=='__main__':unittest.main()
