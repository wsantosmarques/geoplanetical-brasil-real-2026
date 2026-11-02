"""Eventos de progresso e I/O verificável, sem acessar Tk na thread de trabalho."""
import contextlib,threading,time,hashlib,shutil
from pathlib import Path
_state=threading.local()

@contextlib.contextmanager
def progress_task(callback):
    old=getattr(_state,'callback',None)
    _state.callback=callback
    try:yield
    finally:_state.callback=old

def report(operation,file,done,total,started):
    callback=getattr(_state,'callback',None)
    if callback:callback({'operation':operation,'file':Path(file).name,'done':done,'total':total,'seconds':time.monotonic()-started})

def copy_stream(source,target,total,file,operation='Copiando'):
    done=0;started=last=time.monotonic()
    report(operation,file,0,total,started)
    while True:
        chunk=source.read(16*1024*1024)
        if not chunk:break
        target.write(chunk);done+=len(chunk)
        now=time.monotonic()
        if now-last>=.2:
            report(operation,file,done,total,started);last=now
    report(operation,file,done,total,started)

def copy_file(source,target):
    source,target=Path(source),Path(target)
    if target.exists() and source.samefile(target):raise shutil.SameFileError(str(source))
    with source.open('rb') as src,target.open('wb') as dst:
        copy_stream(src,dst,source.stat().st_size,source.name)
    shutil.copystat(source,target)
    return target

def file_sha(file):
    file=Path(file);total=file.stat().st_size;done=0;started=last=time.monotonic();digest=hashlib.sha256()
    report('Verificando',file,0,total,started)
    with file.open('rb') as source:
        while True:
            chunk=source.read(16*1024*1024)
            if not chunk:break
            digest.update(chunk);done+=len(chunk);now=time.monotonic()
            if now-last>=.2:
                report('Verificando',file,done,total,started);last=now
    report('Verificando',file,done,total,started)
    return digest.hexdigest()

class ProgressLog:
    def __init__(self, file, notify):
        self.file, self.notify, self.pending = file, notify, ''
    def write(self, text):
        count = self.file.write(text)
        self.file.flush()
        self.pending += text
        while '\n' in self.pending:
            line, self.pending = self.pending.split('\n', 1)
            if line.strip() and not line.lstrip().startswith('{'): self.notify(line.strip())
        return count
    def flush(self):
        self.file.flush()
