"""Verifica progresso sem abrir GUI ou executar o instalador empacotado."""
import io,queue,time
from progresso import ProgressLog
from instalador_gui import App
f=io.StringIO();messages=[];stream=ProgressLog(f,messages.append)
stream.write('Conferindo ');stream.write('backup...\n');stream.write('{"state":"restored"}\nMontando pacote...\n')
assert messages==['Conferindo backup...','Montando pacote...']
assert '{"state":"restored"}' in f.getvalue()
class Value:
 def set(self,s):self.value=s
class Control:
 def __init__(self):self.calls=[]
 def state(self,s):self.calls.append(s)
 def stop(self):self.calls.append('stop')
class Root:
 def after(self,*args):pass
app=object.__new__(App);app.busy=True;app.started=time.monotonic()-65;app.events=queue.Queue();app.status=Value();app.elapsed=Value();app.root=Root();app.bar=Control();app.install=Control();app.restore=Control();app.browse=Control()
app.events.put(('progress','Copiando backup...'));app.poll()
assert app.busy and app.status.value=='Copiando backup...' and not app.install.calls
assert '01:05' in app.elapsed.value
app.events.put(('progress','Verificando integridade...'));app.events.put(('done',True,'Concluído.'));app.poll()
assert not app.busy and app.status.value=='Concluído.' and app.install.calls==[['!disabled']]
print('PASS: log imediato, linhas parciais, JSON preservado apenas no log, progresso sem destravar controles, conclusão e tempo decorrido.')
