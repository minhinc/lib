import importlib
import inspect,re,sys

def _i(modules_,**kwarg_):
 '''return instance of a class present in module modules_. class name has to be provided through kwarg_['classs']. Default class name will be taken from module name if kwarg_['class'] not available.
kwarg_
 classs class name in modules_ file to be instantiated (if not already instantiated) and returned
 classobj (True/False) class object to be returned rather than instance.'''
 classs=kwarg_['classs'] if 'classs' in kwarg_ else '_'+re.split(r'[.]',modules_)[-1]
 print(f'<=> _i {modules_=} {kwarg_=}  {classs=}')
 try:
  return getattr(getattr(sys.modules[modules_],classs),classs) if not 'classobj' in kwarg_ else getattr(sys.modules[modules_],classs)
 except Exception as e:
  print(f'Exception in _i {e=}')
  if not modules_ in sys.modules:
   importlib.import_module(modules_)
  if not 'classobj' in kwarg_ and not hasattr(getattr(sys.modules[modules_],classs),classs):
   setattr(getattr(sys.modules[modules_],classs),classs,eval(f'sys.modules[modules_].{classs}()'))
  return _i(modules_,**kwarg_)

def _help(**kwarg_):
 '''kwarg_
 module modulename on which help has to be applied
 classs classs name in the module(optonal)'''
 print(f'>< _help {kwarg_=}')
 obj=_i(kwarg_['module'],**(dict(classes=kwarg_['classes']) if 'classes' in kwarg_ else dict()),**(dict(classobj=True) if len(sys.argv)<=1 else dict()))
 print(f'{obj=} {hasattr(obj,"__class__")=}')
 methodd=dict([method for method in inspect.getmembers(obj,predicate=(inspect.ismethod if len(sys.argv)>1 else inspect.isfunction)) if re.search(r'^_(?!'+(obj.__class__.__name__ if len(sys.argv)>1 else obj.__name__)+r'__)',method[0])])
 if len(sys.argv)<2:
  for method in [method for method in methodd if type(methodd[method].__doc__)==str]:
   print(f'{methodd[method].__doc__=}')
   #print(f"--{re.sub(r'(^_+|_+$)','',method)}\n  "+'\n  '.join(re.findall(r"^\s*(?!.*_(?:\([^)]*\))?(?:\s|$))(\S+.*)$",methodd[method].__doc__,flags=re.M)))
   print(f"--{re.sub(r'(^_+|_+$)','',method)}\n  "+'\n  '.join(re.findall(r"^[ ]+(?!.*_(?:\([^)]*\))?(?:\s|$))(\S+.*)$",methodd[method].__doc__,flags=re.M)))
 else:
  count=1
  dictl=[]
  key=None
  while True:
   if count==len(sys.argv) or re.search(r'^--',sys.argv[count]):
    if key:methodd[key](**dict(dictl))
    if count<len(sys.argv):
     key=re.sub(r'^--','',sys.argv[count])
     key=('_'+key if key!='init' else '__'+key+'__')
    dictl=[]
    if count==len(sys.argv):
     break
   elif count<len(sys.argv) and not re.search(r'^--',sys.argv[count]):
    dictl.append(re.split('=',sys.argv[count]))
   count+=1


def _help2(**kwarg_):
 count=1
 dictl=[]
 method=None
 while True:
  #print(f'{count=} {sys.argv=}')
  if count==len(sys.argv) or re.search(r'^--',sys.argv[count]):
   #print(f'II{count=} {dictl=}')
   if dictl:method(**dict(dictl))
   if count<len(sys.argv):
    #print(re.sub(r'^--(.*)[.].+$',r'\1',sys.argv[count]),re.sub(r'^.*[.]','',sys.argv[count]))
    method=getattr(_i(re.sub(r'^--(.*)[.].+$',r'\1',sys.argv[count])),re.sub(r'^.*[.]_?','_',sys.argv[count]))
   dictl=[]
   if count==len(sys.argv):
    break
  elif count<len(sys.argv) and not re.search(r'^--',sys.argv[count]):
   dictl.append(re.split('=',sys.argv[count]))
  count+=1

#help(cins=_i('lib.ftp'))
#showhelp(cobj=_ftp,mode='print')

if __name__ == "__main__":
 _help2()
