"""Instalador local reversivel; nao le ou escreve conteudo de partidas."""
import pathlib,json,os,shutil,datetime,hashlib,argparse,subprocess,tempfile,contextlib,msvcrt,uuid,re
from asar_local import Asar
from progresso import file_sha,copy_file
from construir import build,EXPECTED_HEADER,EXPECTED_EXE,identify
HERE=pathlib.Path(__file__).resolve().parent
NAMES=('resources/app.asar','Geoplanetical.exe')
INTEGRATION_VERSION='0.3.1'
ORIGINAL_HASHES={
    'resources/app.asar':'eb19415e652989dbea87d0578b0deea120a3734a51d803de268b9dd500fe3f74',
    'Geoplanetical.exe':'d445eb1d3d6c19251c4f533eebb64e7a9655c2ab9535f0338f3c50f4d17042de',
}
CURRENT_HASHES={
    'resources/app.asar':'7540712bc75f84b66303d67841e06797503939758ada792d595656a9bba7cdbe',
    'Geoplanetical.exe':'732b2bb242fb4c9cfdd8f7efa7c4e54f42094d81ee9e8d4e470622012a2eb396',
}

def load_receipt(game,restoring=False):
    """Recusar registro incompleto antes de preparar mod ou alterar o jogo."""
    try:
        receipt=json.loads((game/'brasil-real-editor-installed.json').read_text(encoding='utf8'))
        if not isinstance(receipt,dict):raise ValueError('objeto ausente')
        if not re.fullmatch(r'[a-f0-9]{32}',receipt.get('operationId','')):raise ValueError('operação inválida')
        if receipt.get('gameVersion')!='1.0.7':raise ValueError('versão do jogo inválida')
        if not re.fullmatch(r'\d+\.\d+\.\d+',receipt.get('extensionVersion','')):raise ValueError('versão da integração inválida')
        states={'installed','installing','restoring','recovery-required'} if restoring else {'installed'}
        if receipt.get('state') not in states:raise ValueError('operação anterior incompleta')
        recorded=pathlib.Path(receipt['game']);backup=pathlib.Path(receipt['backup'])
        if not recorded.is_absolute() or recorded.resolve()!=game.resolve():raise ValueError('outra instalação')
        if not backup.is_absolute() or backup.resolve()==game.resolve():raise ValueError('backup inválido')
        files=receipt.get('files')
        if not isinstance(files,dict) or set(files)!=set(NAMES):raise ValueError('lista de arquivos incompleta')
        for name in NAMES:
            info=files[name]
            if not isinstance(info,dict):raise ValueError('arquivo inválido')
            for key in ('originalSha256','installedSha256'):
                if not isinstance(info.get(key),str) or not re.fullmatch(r'[a-f0-9]{64}',info[key]):raise ValueError('hash inválido')
            if info['originalSha256']!=ORIGINAL_HASHES[name]:raise ValueError('original não reconhecido')
            if receipt['extensionVersion']==INTEGRATION_VERSION and info['installedSha256']!=CURRENT_HASHES[name]:raise ValueError('integração não reconhecida')
        return receipt
    except (OSError,ValueError,TypeError,KeyError) as error:
        raise RuntimeError('Registro de instalação inválido ou incompleto. A operação foi recusada antes de alterar o jogo ou o mod. Preserve os backups para recuperação.') from error
def sha(p):
    return file_sha(p)
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
    receipt={'operationId':uuid.uuid4().hex,'extensionVersion':INTEGRATION_VERSION,'gameVersion':version,'game':str(game),'backup':str(backup),'staging':str(stage),'state':'preparing','files':{}}
    changed=[];journal=False;safe_cleanup=True
    try:
        print('Construindo pacote visual e recalculando integridade...',flush=True);receipt['construction']=build(game,stage,catalog)
        for name in NAMES:
            print('Verificando original: '+name,flush=True)
            p=game/name;h=sha(p);dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True)
            print('Criando backup: '+name+' (a cópia e a conferência podem levar alguns minutos)',flush=True);copy_file(p,dest)
            if sha(dest)!=h or sha(p)!=h:raise RuntimeError('Origem mudou durante backup: '+name)
            receipt['files'][name]={'originalSha256':h,'installedSha256':sha(stage/name)}
            if h!=ORIGINAL_HASHES[name] or receipt['files'][name]['installedSha256']!=CURRENT_HASHES[name]:
                raise RuntimeError('Os arquivos construídos não correspondem à integração estudada. A aplicação foi recusada.')
        write_json(backup/'receipt.json',receipt);check_closed(game)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Instalacao mudou antes da substituicao: '+name)
        print('Aplicando a nova integração e verificando os arquivos finais...',flush=True)
        receipt['state']='installing';write_json(state,receipt);journal=True
        for name in NAMES:os.replace(stage/name,game/name);changed.append(name)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['installedSha256']:raise RuntimeError('Verificacao apos instalacao falhou: '+name)
        receipt['state']='installed';write_json(state,receipt);write_json(backup/'receipt.json',receipt)
        print(json.dumps({'state':'installed','backup':str(backup),'savesTouched':False,'fusesUnchanged':True}),flush=True);return receipt
    except Exception:
        try:
            for name in reversed(changed):copy_file(backup/name,game/name)
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
    check_closed(game);state=game/'brasil-real-editor-installed.json';receipt=load_receipt(game,restoring=True);backup=pathlib.Path(receipt['backup'])
    start={}
    for name,info in receipt['files'].items():
        print('Conferindo arquivo instalado e backup: '+name,flush=True)
        start[name]=sha(game/name)
        if start[name] not in {info['originalSha256'],info['installedSha256']}:raise RuntimeError('Arquivo alterado por outra origem/Steam. Restauracao automatica recusada: '+name)
        if sha(backup/name)!=info['originalSha256']:raise RuntimeError('Backup nao confere: '+name)
    stage=pathlib.Path(tempfile.mkdtemp(prefix='brasil-real-editor-restore-',dir=game));changed=[];safe_cleanup=True;previous_state=receipt['state']
    try:
        for name in NAMES:
            print('Preparando restauração segura: '+name+' (cópia do original e da versão atual)',flush=True)
            dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);copy_file(backup/name,dest)
            rollback=stage/'rollback'/name;rollback.parent.mkdir(parents=True,exist_ok=True);copy_file(game/name,rollback)
            if sha(rollback)!=start[name] or sha(dest)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Copias de restauracao divergentes')
        check_closed(game)
        for name in NAMES:
            if sha(game/name)!=start[name]:raise RuntimeError('Arquivo mudou antes de restaurar: '+name)
        print('Aplicando os arquivos originais e conferindo a restauração...',flush=True)
        receipt['state']='restoring';receipt['restoreStaging']=str(stage);write_json(state,receipt)
        for name in NAMES:os.replace(stage/name,game/name);changed.append(name)
        for name in NAMES:
            if sha(game/name)!=receipt['files'][name]['originalSha256']:raise RuntimeError('Restauracao divergente')
        state.unlink();receipt['state']='restored';write_json(backup/'receipt.json',receipt)
        print(json.dumps({'state':'restored','savesTouched':False}),flush=True)
    except Exception:
        try:
            for name in reversed(changed):copy_file(stage/'rollback'/name,game/name)
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
