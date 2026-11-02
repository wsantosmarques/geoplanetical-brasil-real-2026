"""Instalador local reversivel; nao le ou escreve conteudo de partidas."""
import pathlib,json,os,shutil,datetime,hashlib,argparse,subprocess,tempfile,contextlib,msvcrt,uuid
from asar_local import Asar
from construir import build,EXPECTED_HEADER,EXPECTED_EXE,identify
HERE=pathlib.Path(__file__).resolve().parent
NAMES=('resources/app.asar','Geoplanetical.exe')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write_json(p,data):
    temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temp.open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(temp,p)
    finally:
        if temp.exists():temp.unlink()
@contextlib.contextmanager
def operation_lock(game):
    f=(game/'brasil-real-editor.lock').open('a+b');locked=False
    try:
        if f.seek(0,2)==0:f.write(b'0');f.flush()
        f.seek(0)
        try:msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);locked=True
        except OSError:raise RuntimeError('Outra instalacao/restauracao esta em andamento')
        yield
    finally:
        if locked:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
        f.close()
def check_closed(game):
    r=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',"@(Get-Process -Name Geoplanetical -ErrorAction SilentlyContinue | Where-Object { -not $_.Path -or $_.Path -ieq $env:BRASIL_REAL_TARGET_EXE }).Count"],capture_output=True,text=True,check=True,env={**os.environ,'BRASIL_REAL_TARGET_EXE':str(game/'Geoplanetical.exe')},creationflags=subprocess.CREATE_NO_WINDOW)
    if r.stdout.strip()!='0':raise RuntimeError('Feche o Geoplanetical antes de instalar ou restaurar. O instalador nao encerra processos.')
def cleanup(stage,game):
    if stage.resolve().parent!=game or not stage.name.startswith('brasil-real-editor-'):raise RuntimeError('Diretorio temporario inesperado; limpeza recusada')
    shutil.rmtree(stage)
def install(game,catalog):
    game=game.resolve(strict=True)
    with operation_lock(game):return _install(game,catalog)
def _install(game,catalog):
    check_closed(game);asar=game/'resources/app.asar';exe=game/'Geoplanetical.exe';state=game/'brasil-real-editor-installed.json'
    if state.exists():raise RuntimeError('Existe recibo anterior. Use restaurar antes de reinstalar; backups nao sao substituidos automaticamente.')
    if not catalog.is_file():raise RuntimeError('Catalogo nao encontrado junto do instalador: '+str(catalog))
    version=identify(game)
    stage=pathlib.Path(tempfile.mkdtemp(prefix='brasil-real-editor-stage-',dir=game))
    backup=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor'/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True);backup=backup.resolve(strict=True)
    receipt={'operationId':uuid.uuid4().hex,'extensionVersion':'0.3.1','gameVersion':version,'game':str(game),'backup':str(backup),'staging':str(stage),'state':'preparing','files':{}}
    changed=[];journal=False;safe_cleanup=True
    try:
        print('Construindo pacote visual e recalculando integridade...',flush=True);receipt['construction']=build(game,stage,catalog)
        for name in NAMES:
            p=game/name;h=sha(p);dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
            if sha(dest)!=h or sha(p)!=h:raise RuntimeError('Origem mudou durante backup: '+name)
            receipt['files'][name]={'originalSha256':h,'installedSha256':sha(stage/name)}
        write_json(backup/'receipt.json',receipt);check_closed(game)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Instalacao mudou antes da substituicao: '+name)
        receipt['state']='installing';write_json(state,receipt);journal=True
        for name in NAMES:os.replace(stage/name,game/name);changed.append(name)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['installedSha256']:raise RuntimeError('Verificacao apos instalacao falhou: '+name)
        receipt['state']='installed';write_json(state,receipt);write_json(backup/'receipt.json',receipt)
        print(json.dumps({'state':'installed','backup':str(backup),'savesTouched':False,'fusesUnchanged':True}),flush=True);return receipt
    except Exception:
        try:
            for name in reversed(changed):shutil.copy2(backup/name,game/name)
            for name in changed:
                if sha(game/name)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Rollback divergente: '+name)
            receipt['state']='rolled-back' if changed else 'not-installed';write_json(backup/'receipt.json',receipt)
            if journal and state.exists() and json.loads(state.read_text(encoding='utf8')).get('operationId')==receipt['operationId']:state.unlink()
        except Exception as rollback:
            safe_cleanup=False;receipt['state']='recovery-required';receipt['recoveryError']=str(rollback)
            write_json(state,receipt);write_json(backup/'receipt.json',receipt)
        raise
    finally:
        if safe_cleanup:cleanup(stage,game)
def restore(game):
    game=game.resolve(strict=True)
    with operation_lock(game):return _restore(game)
def _restore(game):
    check_closed(game);state=game/'brasil-real-editor-installed.json';receipt=json.loads(state.read_text(encoding='utf8'));backup=pathlib.Path(receipt['backup'])
    if pathlib.Path(receipt['game']).resolve()!=game or set(receipt['files'])!=set(NAMES):raise RuntimeError('Recibo invalido ou pertence a outra instalacao')
    start={}
    for name,info in receipt['files'].items():
        start[name]=sha(game/name)
        if start[name] not in {info['originalSha256'],info['installedSha256']}:raise RuntimeError('Arquivo alterado por outra origem/Steam. Restauracao automatica recusada: '+name)
        if sha(backup/name)!=info['originalSha256']:raise RuntimeError('Backup nao confere: '+name)
    stage=pathlib.Path(tempfile.mkdtemp(prefix='brasil-real-editor-restore-',dir=game));changed=[];safe_cleanup=True;previous_state=receipt['state']
    try:
        for name in NAMES:
            dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(backup/name,dest)
            rollback=stage/'rollback'/name;rollback.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(game/name,rollback)
            if sha(rollback)!=start[name] or sha(dest)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Copias de restauracao divergentes')
        check_closed(game)
        for name in NAMES:
            if sha(game/name)!=start[name]:raise RuntimeError('Arquivo mudou antes de restaurar: '+name)
        receipt['state']='restoring';receipt['restoreStaging']=str(stage);write_json(state,receipt)
        for name in NAMES:os.replace(stage/name,game/name);changed.append(name)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Restauracao divergente')
        state.unlink();receipt['state']='restored';write_json(backup/'receipt.json',receipt)
        print(json.dumps({'state':'restored','savesTouched':False}),flush=True)
    except Exception:
        try:
            for name in reversed(changed):shutil.copy2(stage/'rollback'/name,game/name)
            for name in changed:
                if sha(game/name)!=start[name]:raise RuntimeError('Rollback da restauracao divergente: '+name)
            receipt['state']=previous_state;write_json(state,receipt)
        except Exception as rollback:
            safe_cleanup=False;receipt['state']='recovery-required';receipt['recoveryError']=str(rollback);write_json(state,receipt)
        raise
    finally:
        if safe_cleanup:cleanup(stage,game)
def main():
    p=argparse.ArgumentParser();p.add_argument('acao',choices=['instalar','restaurar']);p.add_argument('--jogo',type=pathlib.Path,default=pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\Geoplanetical'));p.add_argument('--catalogo',type=pathlib.Path,default=HERE/'catalogo-brasil-2026.json');a=p.parse_args()
    if a.acao=='instalar':install(a.jogo,a.catalogo)
    else:restore(a.jogo)
if __name__=='__main__':main()
