import importlib.util,unittest,tempfile,zipfile,sys,configparser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import build
class Packaging(unittest.TestCase):
 def test_standard_jar_roundtrip(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'omni.ja';build.write_jar(p,{'hello.txt':b'hello','nested/a.txt':b'a'});self.assertEqual(build.jar_entries(p)['hello.txt'],b'hello')
 def test_branding_patches_are_bounded_and_preserve_security(self):
  with tempfile.TemporaryDirectory()as d:
   app=Path(d);(app/'browser').mkdir();(app/'application.ini').write_text('[App]\nName=Firefox\nVendor=Mozilla\nVersion=158.0.1\n')
   entries={'localization/en-US/branding/brand.ftl':b'original','modules/AboutNewTab.sys.mjs':b'const ABOUT_URL = "about:newtab";','chrome.manifest':b'manifest chrome/chrome.manifest\n','chrome/browser/skin/classic/browser/browser.css':b'/* upstream */'}
   build.write_jar(app/'browser/omni.ja',entries);build.brand_package(app,'linux');actual=build.jar_entries(app/'browser/omni.ja');self.assertIn(b'Amerika Venture',actual['localization/en-US/branding/brand.ftl']);self.assertIn(b'resource://venture/index.html',actual['modules/AboutNewTab.sys.mjs']);self.assertIn(b'/* upstream */',actual['chrome/browser/skin/classic/browser/browser.css']);self.assertIn('venture/index.html',actual)
   import json
   p=json.loads((app/'distribution/policies.json').read_text())['policies'];self.assertNotIn('DisableSafeBrowsing',p);self.assertNotIn('DisableSecurity',p)
   c=configparser.ConfigParser();c.read(app/'application.ini');self.assertEqual(c['App']['Name'],'AmerikaVenture')
 def test_changed_upstream_layout_stops_build(self):
  with tempfile.TemporaryDirectory()as d:
   app=Path(d);(app/'browser').mkdir();build.write_jar(app/'browser/omni.ja',{'unrelated':b''})
   with self.assertRaises(RuntimeError):build.brand_package(app,'linux')
if __name__=='__main__':unittest.main()
