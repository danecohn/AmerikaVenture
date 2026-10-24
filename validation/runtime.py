"""Verify the actual published browser's policies using a fresh temporary profile."""
from pathlib import Path
import socket,json,subprocess,time,tempfile,sys,os
root=Path(sys.argv[1]);candidates=[p for p in root.rglob('*') if p.is_file() and (p.name=='Venture.exe' or p.name=='zen' and (os.name!='nt'))]
exe=next((p for p in candidates if 'Contents/MacOS' in p.as_posix()),candidates[0] if candidates else None)
if not exe:raise SystemExit('Published browser executable not found')
def receive(sock):
 size=b''
 while not size.endswith(b':'):
  block=sock.recv(1)
  if not block:raise RuntimeError('Marionette closed the connection')
  size+=block
 remaining=int(size[:-1]);data=b''
 while len(data)<remaining:data+=sock.recv(remaining-len(data))
 return json.loads(data)
with tempfile.TemporaryDirectory(prefix='venture-runtime-',ignore_cleanup_errors=True) as profile:
 process=subprocess.Popen([str(exe),'--headless','--no-remote','--remote-allow-system-access','--marionette','--profile',profile,'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  sock=None
  for _ in range(120):
   try:sock=socket.create_connection(('127.0.0.1',2828),timeout=1);break
   except OSError:
    if process.poll() is not None:raise RuntimeError('Venture exited during startup')
    time.sleep(.5)
  if not sock:raise RuntimeError('Marionette did not start')
  sock.settimeout(45);receive(sock);counter=0
  def command(name,body=None):
   global counter
   counter+=1;message=json.dumps([0,counter,name,body or {}]).encode();sock.sendall(str(len(message)).encode()+b':'+message)
   reply=receive(sock)
   if reply[2]:raise RuntimeError(str(reply[2]))
   return reply[3]
  command('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{'pageLoadStrategy':'none'}}})
  command('Marionette:SetContext',{'value':'chrome'})
  result=command('WebDriver:ExecuteAsyncScript',{'script':'''const done=arguments[arguments.length-1];(async()=>{const {SearchService}=ChromeUtils.importESModule("moz-src:///toolkit/components/search/SearchService.sys.mjs");await SearchService.init();for(let i=0;i<40&&SearchService.defaultEngine.name!=='AltStack Search';i++)await new Promise(r=>setTimeout(r,250));const engine=SearchService.defaultEngine;done({engine:engine.name,privateEngine:SearchService.defaultPrivateEngine.name,url:engine.getSubmission('runtime-check').uri.spec,homepage:Services.prefs.getStringPref('browser.startup.homepage'),policies:Services.policies.getActivePolicies()});})().catch(e=>done({error:String(e)}));''','args':[],'newSandbox':True,'sandbox':'default','scriptTimeout':30000})
  value=result.get('value',result);assert value.get('engine')=='AltStack Search',value;assert value.get('privateEngine')=='AltStack Search',value;assert value.get('url')=='https://www.amerika.social/search?q=runtime-check',value;assert value.get('homepage')=='https://www.amerika.social/',value
  print(json.dumps({'defaultSearch':value['engine'],'searchURL':value['url'],'homepage':value['homepage']}))
  command('WebDriver:ExecuteScript',{'script':"Services.wm.getMostRecentWindow('navigator:browser').BrowserCommands.openTab();return true;",'args':[],'newSandbox':True,'sandbox':'default'})
  current=''
  for _ in range(60):
   result=command('WebDriver:ExecuteScript',{'script':"return Services.wm.getMostRecentWindow('navigator:browser').gBrowser.selectedBrowser.currentURI.spec;",'args':[],'newSandbox':True,'sandbox':'default'})
   current=result.get('value',result) if isinstance(result,dict) else result
   if current.startswith('https://www.amerika.social/'):break
   time.sleep(.5)
  diagnostics=command('WebDriver:ExecuteScript',{'script':"const w=Services.wm.getMostRecentWindow('navigator:browser');return {configured:w.BROWSER_NEW_TAB_URL,replace:Services.prefs.getBoolPref('zen.urlbar.replace-newtab'),tabs:Array.from(w.gBrowser.tabs,t=>({url:t.linkedBrowser.currentURI.spec,selected:t.selected,empty:t.hasAttribute('zen-empty-tab')}))};",'args':[],'newSandbox':True,'sandbox':'default'});print(json.dumps(diagnostics))
  assert current.startswith('https://www.amerika.social/'),('New tab did not open AltStack',current)
  print('New tab opens the AltStack desktop:',current)
  try:command('Marionette:Quit',{'flags':['eAttemptQuit']})
  except Exception:pass
  sock.close()
 finally:
  try:process.wait(timeout=15)
  except subprocess.TimeoutExpired:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait()

