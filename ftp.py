#!/usr/bin/env python3
import sys,os,re,traceback
from ftplib import FTP
import lib.help

class _ftp:
 root_dir='/htdocs'
 def __init__(self,**argv):
  '''
argv
 rootdir(s) defaults to /htdocs,i.e. get(ftpfile='apps/handler.py',mchfile='.') would get from /htdocs/render...'''
  print(f'>< _ftp.__init__{self=}')
  if len(argv)==0:
   self.ftp=FTP("ftpupload.net")
   self.ftp.login(os.getenv("FTP_USER"),os.getenv("FTP_PASSWORD"))
   #self.ftp.set_pasv(False)
   print(f'<=> _ftp.__init__ logged in successfully')
   if 'rootdir' in argv:_ftp.root_dir=argv['rootdir']

 def isfile(self,**kwarg_):
  '''
kwarg_
 file(s) filename'''
  print(f'>< isfile {kwarg_=}')
  try:
   self.ftp.size(kwarg_['file'])
   return True
  except Exception as e:
   print(f'<=> isfile exception, not a file, {e=}')
  return False

 def _get(self,**kwarg_):
  '''
kwarg_
 mchfile(s) machine filename
 ftpfile(s) ftp server filename
 dir_(b) if ftpfile argument is a directory. to avoid overloading ftp server'''
  if not 'dir_' in kwarg_:kwarg_['mchfile'],kwarg_['ftpfile']=[self.getfullpath(scope=('mchn' if x=='mchfile' else 'ftp'),file=kwarg_[x]) for x in ('mchfile','ftpfile')]
  print(f'<=> get {kwarg_=}')
  if 'dir_' in kwarg_ or not self.isfile(file=kwarg_['ftpfile']):
   kwarg_['mchfile']+='/'+os.path.basename(kwarg_['ftpfile'])
   os.makedirs(kwarg_['mchfile'],exist_ok=True)
   try:
    for file, facts in self.ftp.mlsd(kwarg_['ftpfile']):
     if facts['type']=='file':
      self.ftpfile(mode='ret',mchfile=kwarg_['mchfile']+'/'+file,ftpfile=kwarg_['ftpfile']+'/'+file)
     elif facts['type']=='dir':
      self._get(mchfile=kwarg_['mchfile'], ftpfile=kwarg_['ftpfile']+'/'+file,dir_=True)
   except Exception as e:
    print(f'Exception recieved, {e=}')
  else:
   self.ftpfile(mode='ret',mchfile=kwarg_['mchfile']+('/'+os.path.basename(kwarg_['ftpfile']) if not os.path.isfile(kwarg_['mchfile']) else ''),ftpfile=kwarg_['ftpfile'])

 def _put(self,**kwarg_):
  '''
kwarg_
 mchfile(s) machine filename
 ftpfile(s) ftp server filename
 dir_(b) if ftpfile argument is a directory. to avoid overloading ftp server'''
  if not 'dir_' in kwarg_:kwarg_['mchfile'],kwarg_['ftpfile']=[self.getfullpath(scope=('mchn' if x=='mchfile' else 'ftp'),file=kwarg_[x]) for x in ('mchfile','ftpfile')]
  print(f'<=> put {kwarg_=}')
  if 'dir_' in kwarg_ or not os.path.isfile(kwarg_['mchfile']):
   kwarg_['ftpfile']+='/'+os.path.basename(kwarg_['mchfile'])
   try:
    self.ftp.mkd(kwarg_['ftpfile'])
   except:
    pass
   with os.scandir(kwarg_['mchfile']) as entries:
    for entry in entries:
     if entry.is_file():
      self.ftpfile(mode='up',ftpfile=kwarg_['ftpfile']+'/'+entry.name,mchfile=kwarg_['mchfile']+'/'+entry.name)
     elif entry.is_dir():
      self._put(ftpfile=kwarg_['ftpfile'], mchfile=kwarg_['mchfile']+'/'+entry.name,dir_=True)
  else:
   self.ftpfile(mode='up',ftpfile=kwarg_['ftpfile']+('/'+os.path.basename(kwarg_['mchfile']) if not self.isfile(file=kwarg_['ftpfile']) else ''),mchfile=kwarg_['mchfile'])

 def _ls(self,**kwarg_):
  '''
kwarg_
 ftpfile(s) ftp server file
 recursive (True/False)
 dir_(b) if ftpfile argument is a directory. to avoid overloading ftp server'''
  if not 'dir_' in kwarg_:kwarg_['ftpfile']=self.getfullpath(file=kwarg_['ftpfile'])
  print(f'<=> _ls {kwarg_=}')
  if 'dir_' in kwarg_ or not self.isfile(file=kwarg_['ftpfile']):
   try:
    for file, facts in self.ftp.mlsd(kwarg_['ftpfile']):
     if not 'recursive' in kwarg_ or re.search(r'False',kwarg_['recursive'],flags=re.I) or re.search(r'True',kwarg_['recursive'],flags=re.I) and facts['type']=='file':
      print(kwarg_['ftpfile']+'/'+file)
     elif facts['type']=='dir':
      self._ls(recursive="True",ftpfile=kwarg_['ftpfile']+'/'+file,dir_=True)
   except Exception as e:
    print(f'Exception recieved {e=}')
  else:
     print(kwarg_['ftpfile'])

 def _delete(self,**kwarg_):
  '''
kwarg_
 ftpfile(s) ftp server file
 recursive (True/False)
 dir_(b) if ftpfile argument is a directory. to avoid overloading ftp server'''
  if not 'dir_' in kwarg_:kwarg_['ftpfile']=self.getfullpath(file=kwarg_['ftpfile'])
  print(f'<=> _delete {kwarg_=}')
  if 'dir_' in kwarg_ or not self.isfile(file=kwarg_['ftpfile']):
   try:
    for file, facts in self.ftp.mlsd(kwarg_['ftpfile']):
     if facts['type']=='file':
      self.ftp.delete(kwarg_['ftpfile']+'/'+file)
      print(f'deleted {kwarg_["ftpfile"]+"/"+file}')
     elif facts['type']=='dir' and 'recursive' in kwarg_ and re.search(r'True',kwarg_['recursive'],flags=re.I):
      self._delete(recursive="True",ftpfile=kwarg_['ftpfile']+'/'+file,dir_=True)
    self.ftp.rmd(kwarg_['ftpfile'])
   except Exception as e:
    print(f'Exception recieved {e=}')
  else:
   self.ftp.delete(kwarg_['ftpfile'])

 def getfullpath(self,**kwarg_):
  '''
kwarg_
 scope(s) 'mchn'/'ftp'
 file(s) name of the file'''
  print(f'>< getfullpath {kwarg_}')
  if not re.search(r'^/',kwarg_['file']):
   return re.sub(r'(/*[.]/*|/*)$','',_ftp.root_dir+'/'+kwarg_['file']  if not 'scope' in kwarg_ or kwarg_['scope']=='ftp' else os.getcwd()+'/'+kwarg_['file'])
  return kwarg_['file']

 def ftpfile(self,**kwarg_):
  '''
kwarg_
 mchfile(s) machine filename
 ftpfile(s) ftp server filename
 mode(s) 'up'/'ret'/'del' '''
  print(f'>< ftpfile {kwarg_=} {self=}')
  if kwarg_['mode']=='del':
   ftp.delete(kwarg_['ftpfile'])
  else:
   with open(kwarg_['mchfile'],'wb' if kwarg_['mode']=='ret' else 'rb') as f:
    self.ftp.retrbinary(f'RETR {kwarg_["ftpfile"]}',f.write) if kwarg_['mode']=='ret' else self.ftp.storbinary(f'STOR {kwarg_["ftpfile"]}', f)

if __name__=='__main__':
 lib.help._help(module='lib.ftp')
