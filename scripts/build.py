#!/usr/bin/env python3
import argparse,configparser,hashlib,io,json,os,platform,plistlib,re,shutil,struct,subprocess,sys,tarfile,tempfile,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'upstream.json').read_text())
TARGETS={'linux-x64':('linux-x86_64','firefox-{v}.tar.xz'),'linux-arm64':('linux-aarch64','firefox-{v}.tar.xz'),'windows-x64':('win64','Firefox Setup {v}.exe'),'windows-arm64':('win64-aarch64','Firefox Setup {v}.exe'),'macos-x64':('mac','Firefox {v}.dmg'),'macos-arm64':('mac','Firefox {v}.dmg')}
BRAND_FTL='''-brand-shorter-name = AltStack Venture
-brand-short-name = AltStack Venture
-brand-shortcut-name = AltStack Venture
-brand-full-name = AltStack Venture
-brand-product-name = AltStack Venture
-vendor-short-name = AltStack LLC
trademarkInfo = AltStack AltStack Venture is an AltStack LLC browser based on Mozilla Firefox. Firefox is a trademark of the Mozilla Foundation.
'''
BROWSER_CSS=(ROOT/'assets/venture-classic.css').read_text()

def jar_entries(path):
 data=Path(path).read_bytes()
 try:z=zipfile.ZipFile(io.BytesIO(data))
 except zipfile.BadZipFile:
  offset=data.rfind(b'PK\x05\x06')
  if offset<0 or data[4:8]!=b'PK\x01\x02':raise
  end=bytearray(data[offset:offset+22]);size=struct.unpack_from('<I',end,12)[0];struct.pack_into('<I',end,16,len(data));z=zipfile.ZipFile(io.BytesIO(data+data[4:4+size]+end))
 with z:return {name:z.read(name) for name in z.namelist() if not name.endswith('/')}

def write_jar(path,entries):
 temp=Path(str(path)+'.tmp')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,content in entries.items():
   info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content)
 temp.replace(path)

def brand_package(app,system):
 resource=app/'Contents/Resources' if system=='macos' else app
 jar=resource/'browser/omni.ja';entries=jar_entries(jar)
 ftl='localization/en-US/branding/brand.ftl';properties='chrome/en-US/locale/branding/brand.properties'
 if ftl not in entries:raise RuntimeError('Upstream branding layout changed; inspect before building.')
 entries[ftl]=BRAND_FTL.encode();entries[properties]=b'brandShorterName=Venture\nbrandShortName=Venture\nbrandFullName=Venture\n'
 mark=(ROOT/'assets/venture.svg').read_bytes()
 for name in list(entries):
  if '/content/branding/' not in name:continue
  base=Path(name).name
  if base.endswith('.svg') and any(x in base for x in ['logo','wordmark']):
   if 'wordmark' in base:entries[name]=b'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="60"><text x="0" y="43" fill="#f7f7fa" font-family="sans-serif" font-size="35" font-weight="600">AltStack Venture</text></svg>'
   else:entries[name]=mark
  elif base.endswith('.png'):
   m=re.search(r'icon(\d+)',base);size=int(m.group(1)) if m else 256
   entries[name]=(ROOT/f'assets/icon{min(size,512)}.png').read_bytes()
  elif base=='aboutDialog.css':entries[name]+=b'\n#aboutDialogContainer{background:#141417!important;color:#f7f7fa!important}#bottomBox{background:#0e0e10!important}\n'
 module='modules/AboutNewTab.sys.mjs'
 if b'const ABOUT_URL = "about:newtab";' not in entries.get(module,b''):raise RuntimeError('Upstream new-tab module changed.')
 entries[module]=entries[module].replace(b'const ABOUT_URL = "about:newtab";',b'const ABOUT_URL = "resource://venture/index.html";')
 entries['chrome.manifest']+=b'\nresource venture venture/ contentaccessible=yes\n'
 for path in (ROOT/'start').iterdir():
  if path.is_file():entries['venture/'+path.name]=path.read_bytes()
 css='chrome/browser/skin/classic/browser/browser.css'
 if css not in entries:raise RuntimeError('Upstream browser stylesheet moved.')
 entries[css]+=BROWSER_CSS.encode();write_jar(jar,entries)
 ini=resource/'application.ini';config=configparser.ConfigParser(interpolation=None);config.optionxform=str;config.read(ini)
 config['App'].update(Name='AltStack Venture',Vendor='AltStack LLC',RemotingName='amerika-venture',Profile='Venture')
 with ini.open('w')as f:config.write(f,space_around_delimiters=False)
 icons=resource/'browser/chrome/icons/default';icons.mkdir(parents=True,exist_ok=True)
 for size in [16,32,48,64,128]:shutil.copy2(ROOT/f'assets/icon{size}.png',icons/f'default{size}.png')
 distribution=resource/'distribution';distribution.mkdir(exist_ok=True)
 (distribution/'distribution.ini').write_text('[Global]\nid=com.amerika.venture\nversion='+META['version']+'\nabout=Venture by AltStack LLC\n[Preferences]\napp.distributor="AltStack LLC"\napp.distributor.channel="venture"\n')
 policies={'policies':{'Homepage':{'URL':'resource://venture/index.html','Locked':False,'StartPage':'homepage'},'DisableTelemetry':True,'DisableFirefoxStudies':True,'DisableAppUpdate':True,'DontCheckDefaultBrowser':True,'DisplayBookmarksToolbar':'always','Preferences':{'browser.startup.homepage_override.mstone':{'Value':'ignore','Status':'default'},'browser.aboutwelcome.enabled':{'Value':False,'Status':'default'},'extensions.activeThemeID':{'Value':'default-theme@mozilla.org','Status':'default'},'app.releaseNotesURL':{'Value':'https://github.com/danecohn/AmerikaVenture/releases','Status':'default'},'browser.startup.homepage_override.buildID':{'Value':'ignore','Status':'default'}}}}
 (distribution/'policies.json').write_text(json.dumps(policies,indent=2))
 (resource/'AMERIKA-SOURCE.json').write_text(json.dumps({**META,'product':'Venture','method':'Rebuilt chrome resources over unmodified stable Gecko binaries','modifications':'https://github.com/danecohn/AmerikaVenture','updates':'Manual: download and install a new Venture release. Mozilla automatic app updates are disabled to preserve this distribution.'},indent=2))
 shutil.copy2(ROOT/'LICENSE',resource/'AMERIKA-LICENSE.txt');shutil.copy2(ROOT/'README.md',resource/'AMERIKA-README.md')
 if system=='windows':
  from windows_resources import replace_resources
  replace_resources(resource/'firefox.exe',ROOT/'assets/venture.ico')
  for manifest in resource.glob('*.VisualElementsManifest.xml'):
   text=manifest.read_text();text=re.sub(r'DisplayName="[^"]*"','DisplayName="AltStack Venture"',text);manifest.write_text(text)
  for f in ['VisualElements_150.png','VisualElements_70.png']:
   p=resource/'browser/VisualElements'/f
   if p.exists():shutil.copy2(ROOT/'assets/icon256.png',p)
 if system=='macos':
  p=app/'Contents/Info.plist';v=plistlib.loads(p.read_bytes());v.update(CFBundleName='AltStack Venture',CFBundleDisplayName='AltStack Venture',CFBundleIdentifier='com.amerika.venture',CFBundleIconFile='venture.icns');p.write_bytes(plistlib.dumps(v));shutil.copy2(ROOT/'assets/venture.icns',resource/'venture.icns')
  signature=app/'Contents/_CodeSignature'
  if signature.exists():shutil.rmtree(signature)
  entitlements=ROOT/'assets/entitlements.plist';subprocess.run(['codesign','--force','--deep','--sign','-','--entitlements',str(entitlements),str(app)],check=True)
 return resource

def download(url,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  print('Downloading',url,flush=True);urllib.request.urlretrieve(url,str(path)+'.partial');Path(str(path)+'.partial').replace(path)
 return path

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--target',choices=TARGETS,required=True);parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'release');args=parser.parse_args();system,arch=args.target.split('-');version=META['version'];folder,filename=TARGETS[args.target];filename=filename.format(v=version);base=f'https://archive.mozilla.org/pub/firefox/releases/{version}/';relative=f'{folder}/en-US/{filename}';archive=args.input or download(base+urllib.parse.quote(relative),ROOT/'cache'/args.target/filename.replace(' ','-'))
 sums=urllib.request.urlopen(base+'SHA512SUMS').read().decode();expected=next((line.split()[0] for line in sums.splitlines() if line.split(maxsplit=1)[-1].strip().lstrip('*')==relative),None)
 if not expected or hashlib.sha512(archive.read_bytes()).hexdigest()!=expected:raise RuntimeError('Official Firefox SHA512 verification failed.')
 work=ROOT/'build'/args.target
 if work.exists():shutil.rmtree(work)
 work.mkdir(parents=True)
 if system=='linux':
  with tarfile.open(archive)as f:f.extractall(work,filter='data')
  app=work/'firefox'
 elif system=='windows':
  seven=shutil.which('7z')or r'C:\Program Files\7-Zip\7z.exe';subprocess.run([seven,'x',str(archive),'-o'+str(work),'-y'],check=True,stdout=subprocess.DEVNULL);app=work/'core'
 else:
  result=subprocess.run(['hdiutil','attach','-readonly','-nobrowse','-plist',str(archive)],capture_output=True,check=True);info=plistlib.loads(result.stdout);mount=next(x['mount-point']for x in info['system-entities']if 'mount-point'in x)
  try:source=next(Path(mount).glob('*.app'));app=work/'Venture.app';shutil.copytree(source,app,symlinks=True)
  finally:subprocess.run(['hdiutil','detach',mount],check=True,stdout=subprocess.DEVNULL)
 resource=brand_package(app,system);args.output.mkdir(parents=True,exist_ok=True);name=f'Venture-{system}-{arch}'
 if system=='linux':
  dest=work/'Venture';app.rename(dest)
  (dest/'Venture').write_text('#!/bin/sh\nROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec "$ROOT/firefox" --name Venture --class Venture "$@"\n');(dest/'Venture').chmod(0o755)
  shutil.copy2(ROOT/'scripts/install-linux.sh',dest/'install-linux.sh');(dest/'install-linux.sh').chmod(0o755)
  with tarfile.open(args.output/(name+'.tar.gz'),'w:gz')as f:f.add(dest,arcname='Venture')
 elif system=='windows':
  shutil.copy2(app/'firefox.exe',app/'Venture.exe');app.rename(work/'Venture');shutil.make_archive(str(args.output/name),'zip',work,'Venture')
 else:subprocess.run(['hdiutil','create','-volname','Venture','-srcfolder',str(app),'-ov',str(args.output/(name+'.dmg'))],check=True)
 for p in args.output.glob(name+'.*'):
  if p.suffix!='.sha256':p.with_name(p.name+'.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
 print('Built',name,flush=True)
if __name__=='__main__':main()
