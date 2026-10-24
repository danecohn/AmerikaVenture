import argparse,subprocess,tempfile,time,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--target',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];system=a.target.split('-')[0];work=r/'build'/a.target
exe=work/'Venture/firefox'if system=='linux'else work/'AltStack Venture.app/Contents/MacOS/firefox'if system=='macos'else work/'Venture/Venture.exe'
out=r/'release'/('smoke-'+a.target+'.png')
with tempfile.TemporaryDirectory()as profile:
 command=[str(exe),'--headless','--no-remote','--profile',profile,'--screenshot',str(out),'--window-size','1440,900','resource://venture/index.html']
 subprocess.run(command,check=True,timeout=90)
 for _ in range(20):
  if out.exists():break
  time.sleep(1)
 if not out.exists()or out.stat().st_size<10000:raise SystemExit('Browser did not produce a valid start-page screenshot.')
 data=out.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>II',data[16:24])==(1440,900)
print('Browser smoke test passed:',a.target)
