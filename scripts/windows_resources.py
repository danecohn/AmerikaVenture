import ctypes,struct
from pathlib import Path

def align(data):return data+b'\0'*((-len(data))%4)
def block(key,value=b'',children=b'',text=False):
 data=align(struct.pack('<HHH',0,len(value)//2 if text else len(value),int(text))+key.encode('utf-16le')+b'\0\0')+value
 data=align(data)+children
 return struct.pack('<H',len(data))+data[2:]
def version_resource():
 values={'CompanyName':'AltStack LLC','FileDescription':'AltStack Venture','FileVersion':'158.0.1','InternalName':'AmerikaVenture','LegalCopyright':'AltStack LLC; includes Mozilla software under MPL 2.0','OriginalFilename':'firefox.exe','ProductName':'AltStack Venture','ProductVersion':'158.0.1'}
 strings=b''.join(align(block(k,(v+'\0').encode('utf-16le'),text=True))for k,v in values.items())
 table=block('StringFileInfo',children=block('040904B0',children=strings,text=True),text=True)
 translation=block('VarFileInfo',children=block('Translation',struct.pack('<HH',0x409,1200)))
 fixed=struct.pack('<13I',0xFEEF04BD,0x10000,158<<16,1<<16,158<<16,1<<16,0x3f,0,0x40004,1,0,0,0)
 return block('VS_VERSION_INFO',fixed,align(table)+translation)
def replace_resources(executable,icon):
 from ctypes import wintypes
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.LoadLibraryExW.argtypes=[wintypes.LPCWSTR,wintypes.HANDLE,wintypes.DWORD];kernel.LoadLibraryExW.restype=wintypes.HMODULE
 module=kernel.LoadLibraryExW(str(executable),None,2);groups=[]
 kernel.FreeLibrary.argtypes=[wintypes.HMODULE]
 if not module:raise ctypes.WinError(ctypes.get_last_error())
 callback=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HMODULE,ctypes.c_void_p,ctypes.c_void_p,wintypes.LPARAM)
 def collect(_module,_kind,name,_param):
  groups.append(name if name<=65535 else ctypes.wstring_at(name));return True
 enum=callback(collect)
 kernel.EnumResourceNamesW.argtypes=[wintypes.HMODULE,ctypes.c_void_p,callback,wintypes.LPARAM];kernel.EnumResourceNamesW(module,ctypes.c_void_p(14),enum,0);kernel.FreeLibrary(module)
 kernel.BeginUpdateResourceW.argtypes=[wintypes.LPCWSTR,wintypes.BOOL];kernel.BeginUpdateResourceW.restype=wintypes.HANDLE
 handle=kernel.BeginUpdateResourceW(str(executable),False)
 if not handle:raise ctypes.WinError(ctypes.get_last_error())
 kernel.UpdateResourceW.argtypes=[wintypes.HANDLE,ctypes.c_void_p,ctypes.c_void_p,wintypes.WORD,ctypes.c_void_p,wintypes.DWORD]
 kernel.EndUpdateResourceW.argtypes=[wintypes.HANDLE,wintypes.BOOL]
 def update(kind,name,data):
  identifier=ctypes.c_void_p(name) if isinstance(name,int) else ctypes.cast(ctypes.c_wchar_p(name),ctypes.c_void_p);buffer=ctypes.create_string_buffer(data)
  if not kernel.UpdateResourceW(handle,ctypes.c_void_p(kind),identifier,1033,buffer,len(data)):raise ctypes.WinError(ctypes.get_last_error())
 try:
  raw=Path(icon).read_bytes();reserved,kind,count=struct.unpack_from('<HHH',raw);group=struct.pack('<HHH',reserved,kind,count)
  for i in range(count):
   w,h,c,r,planes,bits,size,offset=struct.unpack_from('<BBBBHHII',raw,6+16*i);resource=5000+i;update(3,resource,raw[offset:offset+size]);group+=struct.pack('<BBBBHHIH',w,h,c,r,planes,bits,size,resource)
  for name in groups or [32512]:update(14,name,group)
  update(16,1,version_resource())
 except BaseException:
  kernel.EndUpdateResourceW(handle,True);raise
 if not kernel.EndUpdateResourceW(handle,False):raise ctypes.WinError(ctypes.get_last_error())
