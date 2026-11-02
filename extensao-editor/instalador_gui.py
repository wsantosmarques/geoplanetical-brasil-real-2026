"""Entrada do executavel unico do Brasil Real. Sem Python externo."""
import pathlib,os,sys,json,threading,queue,traceback,datetime,contextlib,shutil,argparse,winreg
import time
from progresso import ProgressLog
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from instalar_extensao import operation_lock,_install,_restore,check_closed,sha,write_json
from construir import identify
HERE=pathlib.Path(getattr(sys,'_MEIPASS',pathlib.Path(__file__).resolve().parent))
VERSION='0.8.0'
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
        print('Preparando nomes, imagens e configuração do mod...',flush=True)
        plan=prepare_names();game_changed=False
        if state.exists():
            receipt=json.loads(state.read_text(encoding='utf8'))
            print('Conferindo a integridade da integração instalada...',flush=True)
            matches=all(sha(game/name)==info['installedSha256'] for name,info in receipt['files'].items())
            if not matches:
                # Steam substituiu o patch: so aceitar uma versao ORIGINAL explicitamente conferida.
                identify(game)
                archive=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor/stale-receipts';archive.mkdir(parents=True,exist_ok=True)
                shutil.copy2(state,archive/(receipt.get('operationId','anterior')+'.json'));state.unlink()
                _install(game,HERE/'catalogo-brasil-2026.json');game_changed=True
            elif receipt.get('extensionVersion')!='0.3.1':
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
class App:
    def __init__(self,root):
        self.root=root;root.title('Brasil Real 2026 | Instalador '+VERSION);root.geometry('730x510');root.minsize(650,430);self.busy=False;self.events=queue.Queue()
        style=ttk.Style();style.theme_use('vista');style.configure('Title.TLabel',font=('Segoe UI',20,'bold'));style.configure('TLabel',font=('Segoe UI',10));style.configure('TButton',font=('Segoe UI',10),padding=8)
        body=ttk.Frame(root,padding=24);body.pack(fill='both',expand=True)
        ttk.Label(body,text='Brasil Real 2026',style='Title.TLabel').pack(anchor='w')
        ttk.Label(body,text='20 partidos, 47 identidades históricas e 45 fotos reais em campanhas novas.',wraplength=650).pack(anchor='w',pady=(4,14))
        ttk.Label(body,text='Pasta do Geoplanetical').pack(anchor='w');row=ttk.Frame(body);row.pack(fill='x',pady=5)
        found=steam_games();self.path=tk.StringVar(value=str(found[0]) if found else '')
        ttk.Entry(row,textvariable=self.path).pack(side='left',fill='x',expand=True);self.browse=ttk.Button(row,text='Procurar',command=self.choose);self.browse.pack(side='left',padx=(8,0))
        ttk.Label(body,text='Feche o jogo antes de instalar. Seus saves não serão convertidos.\nO instalador cria backup dos arquivos do jogo e permite restaurá-los.',wraplength=650).pack(anchor='w',pady=10)
        buttons=ttk.Frame(body);buttons.pack(fill='x',pady=8)
        self.install=ttk.Button(buttons,text='Instalar / atualizar',command=lambda:self.start('install'));self.install.pack(side='left')
        self.restore=ttk.Button(buttons,text='Restaurar jogo',command=lambda:self.start('restore'));self.restore.pack(side='left',padx=8)
        self.bar=ttk.Progressbar(body,mode='indeterminate');self.bar.pack(fill='x',pady=10)
        self.status=tk.StringVar(value='Pronto para instalar. Compatível com a versão 1.0.7 estudada.')
        ttk.Label(body,textvariable=self.status,wraplength=650).pack(anchor='w')
        self.elapsed=tk.StringVar(value='')
        ttk.Label(body,textvariable=self.elapsed).pack(anchor='w',pady=(6,0))
        root.protocol('WM_DELETE_WINDOW',self.close);root.after(150,self.poll)
    def choose(self):
        value=filedialog.askdirectory(title='Selecione a pasta que contém Geoplanetical.exe')
        if value:self.path.set(value)
    def close(self):
        if self.busy:messagebox.showinfo('Operação em andamento','Aguarde a conclusão para fechar o instalador.');return
        self.root.destroy()
    def start(self,action):
        if self.busy:return
        game=pathlib.Path(self.path.get())
        if not (game/'Geoplanetical.exe').is_file():messagebox.showerror('Pasta não encontrada','Selecione a pasta que contém Geoplanetical.exe.');return
        self.started=time.monotonic();self.busy=True;self.install.state(['disabled']);self.restore.state(['disabled']);self.browse.state(['disabled']);self.bar.start(15);self.status.set('Conferindo arquivos, criando backups e aplicando alterações. Aguarde...')
        threading.Thread(target=self.run,args=(action,game),daemon=True).start()
    def run(self,action,game):
        logs=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor/logs';logs.mkdir(parents=True,exist_ok=True);log=logs/('instalador-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.log')
        try:
            with log.open('w',encoding='utf8',buffering=1) as file:
                stream=ProgressLog(file,lambda line:self.events.put(('progress',line)))
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                    try:msg=perform(action,game)
                    except Exception:traceback.print_exc();raise
            self.events.put(('done',True,msg))
        except Exception as e:self.events.put(('done',False,str(e)+'\nRegistro: '+str(log)))
    def poll(self):
        try:
            while True:
                event=self.events.get_nowait()
                if event[0]=='progress':
                    self.status.set(event[1])
                    continue
                _,ok,msg=event
                self.busy=False;self.bar.stop();self.install.state(['!disabled']);self.restore.state(['!disabled']);self.browse.state(['!disabled']);self.status.set(msg)
                if not ok:messagebox.showerror('Não foi possível concluir',msg)
        except queue.Empty:pass
        if hasattr(self,'started'):
            seconds=int(time.monotonic()-self.started)
            self.elapsed.set(('Em andamento' if self.busy else 'Tempo decorrido')+f': {seconds//60:02d}:{seconds%60:02d}. '+('A etapa atual aparece acima; arquivos grandes podem levar alguns minutos.' if self.busy else ''))
        self.root.after(150,self.poll)

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--result',type=pathlib.Path);args=p.parse_args()
    root=tk.Tk()
    if args.self_test:
        root.withdraw();app=App(root);data={'frozen':bool(getattr(sys,'frozen',False)),'tk':root.tk.call('info','patchlevel'),'catalogParties':len(json.loads((HERE/'catalogo-brasil-2026.json').read_text(encoding='utf8'))),'presetParties':len(json.loads((HERE/'novo-jogo-brasil-2026.json').read_text(encoding='utf8'))['preset']['parties']),'historicalPeople':len(json.loads((HERE/'identidades/pessoas-2026.json').read_text(encoding='utf8'))['people']),'photoFiles':len(list((HERE/'identidades/fotos').glob('*'))),'modVersion':json.loads((HERE/'mod/mod.json').read_text(encoding='utf8'))['version'],'mutations':False};root.update();root.destroy()
        if args.result:args.result.write_text(json.dumps(data,indent=2),encoding='utf8')
        return
    App(root);root.mainloop()
if __name__=='__main__':main()
