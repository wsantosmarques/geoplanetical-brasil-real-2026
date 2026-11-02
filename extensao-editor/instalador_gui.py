"""Entrada do executavel unico do Brasil Real. Sem Python externo."""
import pathlib,os,sys,json,threading,queue,traceback,datetime,contextlib,shutil,argparse,winreg
import time
from progresso import ProgressLog
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from instalar_extensao import operation_lock,_install,_restore,check_closed,sha,write_json,load_receipt,INTEGRATION_VERSION
from construir import identify
HERE=pathlib.Path(getattr(sys,'_MEIPASS',pathlib.Path(__file__).resolve().parent))
VERSION='0.8.2'
def steam_games():
    roots=[]
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam') as key:roots.append(pathlib.Path(winreg.QueryValueEx(key,'SteamPath')[0]))
    except OSError:pass
    roots.append(pathlib.Path(os.environ.get('ProgramFiles(x86)',r'C:\Program Files (x86)'))/'Steam')
    import re
    for root in list(roots):
        file=root/'steamapps/libraryfolders.vdf'
        if file.exists():
            for name in re.findall(r'"path"\s+"([^"]+)"',file.read_text(encoding='utf8')):roots.append(pathlib.Path(name.replace('\\\\','\\')))
    games=[p/'steamapps/common/Geoplanetical' for p in roots]
    return list(dict.fromkeys(p for p in games if (p/'Geoplanetical.exe').is_file()))
def prepare_names():
    data=pathlib.Path(os.environ['APPDATA'])/'Geoplanetical';folder=data/'mods/brasil-real-2026';folder.mkdir(parents=True,exist_ok=True)
    source=HERE/'mod';manifest=json.loads((source/'mod.json').read_text(encoding='utf8'))
    backup=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor/mod-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
    config=data/'mods.json'
    if config.exists():
        settings=json.loads(config.read_text(encoding='utf8'));shutil.copy2(config,backup/'mods.json')
    else:settings={'version':1,'order':[],'disabled':[]}
    if not isinstance(settings.get('order',[]),list) or not isinstance(settings.get('disabled',[]),list):raise ValueError('Configuracao de mods invalida')
    order=settings.setdefault('order',[])
    if 'brasil-real-2026' not in order:order.append('brasil-real-2026')
    settings['disabled']=[x for x in settings.get('disabled',[]) if x!='brasil-real-2026']
    targets={}
    for file in source.rglob('*'):
        if not file.is_file():continue
        relative=file.relative_to(source);target=folder/relative
        targets[target]=file.read_bytes()
        if target.exists():
            dest=backup/'mod'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
    targets[config]=json.dumps(settings,ensure_ascii=False,indent=2).encode('utf8')
    return {'backup':str(backup),'targets':targets,'originals':{p:p.read_bytes() if p.exists() else None for p in targets}}
def commit_names(plan):
    changed=[]
    try:
        for p,old in plan['originals'].items():
            if (p.read_bytes() if p.exists() else None)!=old:raise RuntimeError('Um arquivo do mod mudou enquanto era preparado: '+str(p))
        for p,new in plan['targets'].items():
            p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.brasil-real.tmp');temp.write_bytes(new);os.replace(temp,p);changed.append(p)
    except Exception:
        for p in reversed(changed):
            old=plan['originals'][p]
            if old is None:p.unlink()
            else:
                temp=p.with_name(p.name+'.brasil-real-rollback.tmp');temp.write_bytes(old);os.replace(temp,p)
        raise
def perform(action,game):
    game=game.resolve(strict=True);check_closed(game)
    with operation_lock(game):
        state=game/'brasil-real-editor-installed.json'
        if action=='restore':_restore(game);return 'Arquivos do jogo restaurados. Seus mods e suas partidas foram preservados.'
        if action!='install':raise ValueError('Operação desconhecida')
        receipt=None;matches=False
        if state.exists():
            receipt=load_receipt(game)
            print('Conferindo a integridade da integração instalada...',flush=True)
            matches=all(sha(game/name)==info['installedSha256'] for name,info in receipt['files'].items())
            if not matches:identify(game)
            elif receipt['extensionVersion']!=INTEGRATION_VERSION:identify(pathlib.Path(receipt['backup']))
        else:identify(game)
        print('Preparando nomes, imagens e configuração do mod...',flush=True)
        plan=prepare_names();game_changed=False
        if receipt is not None:
            if not matches:
                # Steam substituiu o patch: so aceitar uma versao ORIGINAL explicitamente conferida.
                identify(game)
                archive=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor/stale-receipts';archive.mkdir(parents=True,exist_ok=True)
                shutil.copy2(state,archive/(receipt.get('operationId','anterior')+'.json'));state.unlink()
                _install(game,HERE/'catalogo-brasil-2026.json');game_changed=True
            elif receipt['extensionVersion']!=INTEGRATION_VERSION:
                # Atualizacao usa o backup original; se falhar a nova instalacao, permanece o jogo original.
                print('Conferindo o backup original para atualizar a integração...',flush=True)
                identify(pathlib.Path(receipt['backup']))
                print('Restaurando a extensao anterior...',flush=True);_restore(game);_install(game,HERE/'catalogo-brasil-2026.json');game_changed=True
        else:_install(game,HERE/'catalogo-brasil-2026.json');game_changed=True
        try:
            print('Instalando nomes e capa do mod...',flush=True);commit_names(plan)
        except Exception:
            if game_changed:_restore(game)
            raise
        return 'Concluído. Abra Novo jogo e escolha Brasil para os 20 partidos, 47 identidades e 45 fotos. Consulte Política > Personalidades para ver fontes e lideranças. As campanhas existentes foram preservadas e não recebem as novas identidades.'
from instalador_view import AppView
class App(AppView):
    def __init__(self,root):
        super().__init__(root,perform,HERE,VERSION,steam_games)

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--result',type=pathlib.Path);args=p.parse_args()
    root=tk.Tk()
    if args.self_test:
        root.withdraw();app=App(root);data={'frozen':bool(getattr(sys,'frozen',False)),'tk':root.tk.call('info','patchlevel'),'catalogParties':len(json.loads((HERE/'catalogo-brasil-2026.json').read_text(encoding='utf8'))),'presetParties':len(json.loads((HERE/'novo-jogo-brasil-2026.json').read_text(encoding='utf8'))['preset']['parties']),'historicalPeople':len(json.loads((HERE/'identidades/pessoas-2026.json').read_text(encoding='utf8'))['people']),'photoFiles':len(list((HERE/'identidades/fotos').glob('*'))),'modVersion':json.loads((HERE/'mod/mod.json').read_text(encoding='utf8'))['version'],'mutations':False};root.update();root.destroy()
        if args.result:args.result.write_text(json.dumps(data,indent=2),encoding='utf8')
        return
    App(root);root.mainloop()
if __name__=='__main__':main()
