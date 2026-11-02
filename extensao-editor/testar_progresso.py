"""Testa I/O, isolamento por thread e transações em arquivos pequenos temporários."""
import io,queue,time,pathlib,tempfile,threading,hashlib,json,os
from unittest.mock import patch
from progresso import ProgressLog,progress_task,file_sha,copy_file
from instalador_view import AppView
import instalar_extensao as install
f=io.StringIO();lines=[];stream=ProgressLog(f,lines.append);stream.write('Conferindo ');stream.write('backup...\n');stream.write('{"state":"restored"}\nMontando...\n')
assert lines==['Conferindo backup...','Montando...'] and '{"state":"restored"}' in f.getvalue()
class Value:
 def set(self,s):self.value=s
class Control:
 def __init__(self):self.calls=[];self.value=None
 def state(self,s):self.calls.append(s)
 def stop(self):self.calls.append('stop')
 def start(self,*args):pass
 def configure(self,**kwargs):pass
 def __setitem__(self,k,v):self.value=v
class Root:
 def after(self,*args):pass
app=object.__new__(AppView);app.busy=True;app.started=time.monotonic()-65;app.events=queue.Queue();app.status=Value();app.transfer=Value();app.elapsed=Value();app.root=Root();app.bar=Control();app.install=Control();app.restore=Control();app.browse=Control();app.entry=Control();history=[];app.add_history=history.append
app.events.put(('progress','Criando backup...'));app.events.put(('transfer',{'operation':'Copiando','file':'app.asar','done':50,'total':100,'seconds':1}));app.poll()
assert app.busy and app.bar.value==50 and not app.install.calls and '01:05' in app.elapsed.value
app.events.put(('done',True,'Concluído.'));app.poll();assert not app.busy and app.bar.value==100 and app.install.calls==[['!disabled']]
with tempfile.TemporaryDirectory(prefix='meb-io-test-') as temp:
 root=pathlib.Path(temp);source=root/'source';source.write_bytes(os.urandom(20*1024*1024));events=[]
 with progress_task(events.append):
  copy_file(source,root/'copy');assert file_sha(root/'copy')==hashlib.sha256(source.read_bytes()).hexdigest()
 assert all(e['done']<=e['total'] for e in events) and events[-1]['done']==source.stat().st_size
 try:copy_file(source,source);raise AssertionError('samefile accepted')
 except install.shutil.SameFileError:pass
 unrelated=[]
 with progress_task(unrelated.append):
  thread=threading.Thread(target=lambda:file_sha(source));thread.start();thread.join()
 assert not unrelated,'callback leaked between threads'
 game=root/'game';(game/'resources').mkdir(parents=True);originals={'resources/app.asar':b'ORIGINAL ASAR','Geoplanetical.exe':b'ORIGINAL EXE'}
 for name,data in originals.items():(game/name).write_bytes(data)
 catalog=root/'catalog.json';catalog.write_text('{}');(root/'saves').mkdir();save=root/'saves/campaign';save.write_bytes(b'USER SAVE')
 def build(game,stage,catalog):
  (stage/'resources').mkdir(exist_ok=True)
  for name,data in originals.items():(stage/name).write_bytes(data+b' PATCH')
  return {'fakeBuildForTransactionTest':True}
 with patch.dict(os.environ,{'LOCALAPPDATA':str(root/'local')}),patch.object(install,'ORIGINAL_HASHES',{n:hashlib.sha256(b).hexdigest() for n,b in originals.items()}),patch.object(install,'CURRENT_HASHES',{n:hashlib.sha256(b+b' PATCH').hexdigest() for n,b in originals.items()}),patch.object(install,'check_closed'),patch.object(install,'identify',return_value='1.0.7'),patch.object(install,'build',side_effect=build):
  receipt=install._install(game,catalog);assert receipt['state']=='installed'
  install._restore(game)
  assert all((game/name).read_bytes()==data for name,data in originals.items())
  real_replace=install.os.replace
  def fail_second(source,target):
   if pathlib.Path(target)==game/'Geoplanetical.exe' and pathlib.Path(source).parent.name.startswith('brasil-real-editor-stage-'):raise OSError('injected apply failure')
   return real_replace(source,target)
  with patch.object(install.os,'replace',side_effect=fail_second):
   try:install._install(game,catalog);raise AssertionError('failure not raised')
   except OSError:pass
  assert all((game/name).read_bytes()==data for name,data in originals.items())
  assert not (game/'brasil-real-editor-installed.json').exists()
 assert save.read_bytes()==b'USER SAVE'
print('PASS: progresso/cronômetro, bytes reais, hashes, cópia, mesma origem, isolamento por thread, instalar/restaurar e rollback após falha. Sem tocar no jogo real.')

app.events=queue.Queue()
with patch('instalador_view.pathlib.Path.mkdir',side_effect=PermissionError('injected log directory failure')):app.run('install',pathlib.Path('.'))
assert app.events.get_nowait()[0]=='done'
print('PASS: falha na pasta do registro termina com evento de erro, sem deixar a interface ocupada indefinidamente.')
