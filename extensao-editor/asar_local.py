"""Leitura e atualizacao local de ASAR. Nao desativa fuses do Electron."""
import pathlib,json,struct,hashlib,copy,shutil
from progresso import copy_stream

def digest(data):return hashlib.sha256(data).hexdigest()
class Asar:
    def __init__(self,file):
        self.file=pathlib.Path(file)
        self.identity=self.file.stat()
        with self.file.open('rb') as f:
            h=struct.unpack('<4I',f.read(16));self.raw=f.read(h[3]);self.tree=json.loads(self.raw);self.base=8+h[1]
        self.header_hash=digest(self.raw)
    def entry(self,name):
        obj=self.tree
        for part in name.split('/'):obj=obj['files'][part]
        return obj
    def read(self,name):
        entry=self.entry(name)
        with self.file.open('rb') as f:f.seek(self.base+int(entry['offset']));return f.read(entry['size'])
    def append_replacements(self,target,replacements):
        def identity(p):
            s=p.stat();return (s.st_ino,s.st_size,s.st_mtime_ns)
        expected=(self.identity.st_ino,self.identity.st_size,self.identity.st_mtime_ns)
        if identity(self.file)!=expected or Asar(self.file).header_hash!=self.header_hash:raise ValueError('ASAR de origem mudou antes da construcao')
        tree=copy.deepcopy(self.tree);offset=self.file.stat().st_size-self.base
        for name,data in replacements.items():
            obj=tree
            for part in name.split('/')[:-1]:obj=obj['files'][part]
            item=obj['files'][name.split('/')[-1]]
            block=item.get('integrity',{}).get('blockSize',4194304)
            item.update(size=len(data),offset=str(offset),integrity={'algorithm':'SHA256','hash':digest(data),'blockSize':block,'blocks':[digest(data[n:n+block]) for n in range(0,len(data),block)]})
            offset+=len(data)
        raw=json.dumps(tree,ensure_ascii=False,separators=(',',':')).encode('utf8');pad=(-len(raw))%4;payload=4+len(raw)+pad
        with pathlib.Path(target).open('xb') as out,self.file.open('rb') as source:
            out.write(struct.pack('<4I',4,4+payload,payload,len(raw)));out.write(raw);out.write(b'\0'*pad)
            source.seek(self.base);copy_stream(source,out,self.identity.st_size-self.base,self.file.name,'Construindo')
            for data in replacements.values():out.write(data)
        if identity(self.file)!=expected or Asar(self.file).header_hash!=self.header_hash:raise ValueError('ASAR de origem mudou durante a construcao')
        result=Asar(target)
        for name,data in replacements.items():
            if result.read(name)!=data:raise ValueError('Arquivo reconstruido diferente do esperado: '+name)
        return result
def update_exe_integrity(original,target,old_hash,new_hash):
    data=pathlib.Path(original).read_bytes();old=old_hash.encode('ascii');new=new_hash.encode('ascii')
    if data.count(old)!=1:raise ValueError('Hash ASAR esperado ausente ou ambiguo no executavel')
    patched=data.replace(old,new)
    # O bloco de fuses precisa permanecer byte a byte identico.
    sentinel=b'dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX';at=data.index(sentinel)
    if patched[at:at+64]!=data[at:at+64]:raise ValueError('Fuses modificados inesperadamente')
    pathlib.Path(target).write_bytes(patched)
    return {'originalExeSha256':digest(data),'patchedExeSha256':digest(patched),'fusesUnchanged':True,'newHeaderSha256':new_hash}
