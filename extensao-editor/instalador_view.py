"""Interface nativa do instalador. As operações permanecem na thread de trabalho."""
import contextlib,datetime,json,math,os,pathlib,queue,threading,time,traceback,webbrowser
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from progresso import ProgressLog,progress_task

BG='#171b20';PANEL='#22272d';LINE='#41464c';FG='#edeae2';MUTED='#bdc0c1';GOLD='#d6ad63';GREEN='#9ac58c'
REPO='https://github.com/wsantosmarques/geoplanetical-brasil-real-2026'

def amount(value):
    return (f'{value/1024**3:.2f} GB' if value>=1024**3 else f'{value/1024**2:.1f} MB').replace('.',',')

class AppView:
    def __init__(self,root,perform,here,version,find_games):
        self.root=root;self.perform=perform;self.here=here;self.version=version
        self.busy=False;self.events=queue.Queue();self.log_path=None;self.operation_started=None
        root.title('Brasil Real 2026 | MeB Mods | '+version);root.geometry('1040x760');root.minsize(980,720);root.configure(bg=BG)
        style=ttk.Style();style.theme_use('clam')
        style.configure('BR.TFrame',background=BG);style.configure('Panel.TFrame',background=PANEL)
        style.configure('BR.TLabel',background=BG,foreground=FG,font=('Segoe UI',10))
        style.configure('Muted.TLabel',background=BG,foreground=MUTED,font=('Segoe UI',10))
        style.configure('Title.TLabel',background=BG,foreground=FG,font=('Segoe UI',23,'bold'))
        style.configure('Section.TLabel',background=BG,foreground=FG,font=('Segoe UI',12,'bold'))
        style.configure('BR.TEntry',fieldbackground='#11151a',foreground=FG,insertcolor=FG,bordercolor=LINE,padding=9)
        style.map('BR.TEntry',bordercolor=[('focus',GOLD)])
        style.configure('BR.TButton',background='#31373e',foreground=FG,bordercolor=LINE,padding=(13,10),font=('Segoe UI',10),focuscolor=GOLD)
        style.map('BR.TButton',background=[('disabled','#252a30'),('pressed','#424a53'),('active','#3d454e')],foreground=[('disabled','#92979a')],bordercolor=[('focus',GOLD)])
        style.configure('Gold.TButton',background=GOLD,foreground='#171b20',bordercolor=GOLD,padding=(18,11),font=('Segoe UI',10,'bold'),focuscolor='#171b20')
        style.map('Gold.TButton',background=[('disabled','#66583e'),('pressed','#bb934b'),('active','#e6c383')],foreground=[('disabled','#ddd0b3')])
        style.configure('BR.Horizontal.TProgressbar',background=GOLD,troughcolor='#101419',bordercolor=LINE,lightcolor=GOLD,darkcolor=GOLD,thickness=9)
        root.columnconfigure(1,weight=1);root.rowconfigure(0,weight=1)
        left=tk.Frame(root,bg=PANEL,width=290);left.grid(row=0,column=0,sticky='nsew');left.grid_propagate(False)
        self.images=[]
        cover=here/'mod/images/capa-brasil-real-meb.png'
        if cover.exists():
            im=tk.PhotoImage(file=str(cover));im=im.subsample(max(1,math.ceil(im.width()/250)))
            self.images.append(im);tk.Label(left,image=im,bg=PANEL).pack(padx=20,pady=(30,22))
        tk.Label(left,text='O Brasil de 2026,\nmais perto da realidade.',bg=PANEL,fg=FG,font=('Segoe UI',17,'bold'),justify='left',anchor='w').pack(fill='x',padx=25)
        tk.Label(left,text='20 partidos\n47 identidades históricas\n45 fotografias reais',bg=PANEL,fg=MUTED,font=('Segoe UI',11),justify='left',anchor='w',pady=16).pack(fill='x',padx=25)
        tk.Label(left,text='Campanhas novas\nWindows · jogo 1.0.7 estudado',bg=PANEL,fg=MUTED,font=('Segoe UI',10),justify='left',anchor='w').pack(fill='x',padx=25)
        tk.Label(left,text='MeB Mods',bg=PANEL,fg=GOLD,font=('Segoe UI',17,'bold'),anchor='w').pack(side='bottom',fill='x',padx=25,pady=(8,3))
        tk.Label(left,text='Grupo Mente em Beta',bg=PANEL,fg=MUTED,font=('Segoe UI',9),anchor='w').pack(side='bottom',fill='x',padx=25,pady=(0,20))
        body=ttk.Frame(root,style='BR.TFrame',padding=(30,27));body.grid(row=0,column=1,sticky='nsew');body.columnconfigure(0,weight=1)
        ttk.Label(body,text='Brasil Real 2026',style='Title.TLabel').grid(row=0,column=0,sticky='w')
        ttk.Label(body,text='Versão Full  '+version+' experimental',style='Muted.TLabel').grid(row=1,column=0,sticky='w',pady=(3,17))
        ttk.Label(body,text='Baixou. Abriu. Instalou.',style='Section.TLabel').grid(row=2,column=0,sticky='w')
        ttk.Label(body,text='Feche o jogo, confira a pasta e escolha Instalar / atualizar.\nDepois, abra Novo jogo > Brasil.',style='BR.TLabel',wraplength=610,justify='left').grid(row=3,column=0,sticky='w',pady=(5,15))
        ttk.Label(body,text='Pasta do Geoplanetical',style='BR.TLabel').grid(row=4,column=0,sticky='w')
        row=ttk.Frame(body,style='BR.TFrame');row.grid(row=5,column=0,sticky='ew',pady=(5,12));row.columnconfigure(0,weight=1)
        found=find_games();self.path=tk.StringVar(value=str(found[0]) if found else '')
        self.entry=ttk.Entry(row,textvariable=self.path,style='BR.TEntry');self.entry.grid(row=0,column=0,sticky='ew')
        self.browse=ttk.Button(row,text='Procurar',style='BR.TButton',command=self.choose);self.browse.grid(row=0,column=1,padx=(8,0))
        buttons=ttk.Frame(body,style='BR.TFrame');buttons.grid(row=6,column=0,sticky='w',pady=(0,16))
        self.install=ttk.Button(buttons,text='Instalar / atualizar',style='Gold.TButton',command=lambda:self.start('install'));self.install.pack(side='left')
        self.restore=ttk.Button(buttons,text='Restaurar jogo',style='BR.TButton',command=lambda:self.start('restore'));self.restore.pack(side='left',padx=8)
        self.status=tk.StringVar(value='Pronto para instalar')
        ttk.Label(body,textvariable=self.status,style='Section.TLabel',wraplength=610).grid(row=7,column=0,sticky='w',pady=(0,7))
        self.bar=ttk.Progressbar(body,style='BR.Horizontal.TProgressbar',mode='determinate',maximum=100);self.bar.grid(row=8,column=0,sticky='ew')
        self.transfer=tk.StringVar(value='O progresso do arquivo atual aparecerá aqui.')
        ttk.Label(body,textvariable=self.transfer,style='Muted.TLabel',wraplength=610).grid(row=9,column=0,sticky='w',pady=(6,3))
        self.elapsed=tk.StringVar(value='')
        ttk.Label(body,textvariable=self.elapsed,style='Muted.TLabel').grid(row=10,column=0,sticky='w',pady=(0,10))
        self.history=tk.Text(body,height=5,bg='#11151a',fg=MUTED,font=('Segoe UI',9),relief='flat',borderwidth=0,padx=12,pady=9,wrap='word',state='disabled',takefocus=True,highlightthickness=1,highlightbackground=LINE,highlightcolor=GOLD)
        self.history.grid(row=11,column=0,sticky='nsew');body.rowconfigure(11,weight=1)
        self.add_history('Seus saves são preservados. Há backup e opção de restauração.\nA cópia e a conferência de arquivos de quase 4 GB podem levar alguns minutos.')
        ttk.Label(body,text='O arquivo atual tem progresso real. O tempo restante varia com o disco.\nNão feche o instalador durante a aplicação.',style='Muted.TLabel',wraplength=610).grid(row=12,column=0,sticky='w',pady=(10,10))
        links=ttk.Frame(body,style='BR.TFrame');links.grid(row=13,column=0,sticky='ew')
        self.log_button=ttk.Button(links,text='Ver registro',style='BR.TButton',command=self.open_log,state='disabled');self.log_button.pack(side='left')
        ttk.Button(links,text='Antivírus e SHA-256',style='BR.TButton',command=lambda:webbrowser.open(REPO+'/blob/codex/primeira-publicacao/seguranca/README.md')).pack(side='left',padx=8)
        ttk.Label(body,text='Código aberto · sem assinatura digital · sem serviço em segundo plano',style='Muted.TLabel',wraplength=610).grid(row=14,column=0,sticky='w',pady=(10,0))
        root.protocol('WM_DELETE_WINDOW',self.close);root.after(150,self.poll)

    def add_history(self,line):
        self.history.configure(state='normal');self.history.insert('end',line+'\n');self.history.see('end');self.history.configure(state='disabled')
    def choose(self):
        value=filedialog.askdirectory(title='Selecione a pasta que contém Geoplanetical.exe')
        if value:self.path.set(value)
    def close(self):
        if self.busy:messagebox.showinfo('Operação em andamento','Aguarde a conclusão para fechar o instalador.');return
        self.root.destroy()
    def open_log(self):
        if self.log_path and self.log_path.exists():os.startfile(self.log_path)
    def set_controls(self,enabled):
        for control in (self.install,self.restore,self.browse,self.entry):control.state(['!disabled'] if enabled else ['disabled'])
    def start(self,action):
        if self.busy:return
        game=pathlib.Path(self.path.get())
        if not (game/'Geoplanetical.exe').is_file():messagebox.showerror('Pasta não encontrada','Selecione a pasta que contém Geoplanetical.exe.');return
        self.started=time.monotonic();self.busy=True;self.set_controls(False);self.bar.configure(mode='indeterminate');self.bar.start(18);self.status.set('Conferindo a instalação');self.transfer.set('Preparando a operação...')
        threading.Thread(target=self.run,args=(action,game),daemon=True).start()
    def run(self,action,game):
        log=None
        try:
            logs=pathlib.Path(os.environ['LOCALAPPDATA'])/'BrasilRealEditor/logs';logs.mkdir(parents=True,exist_ok=True);log=logs/('instalador-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.log')
            self.events.put(('log',log))
            with log.open('w',encoding='utf8',buffering=1) as file:
                stream=ProgressLog(file,lambda line:self.events.put(('progress',line)))
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream),progress_task(lambda event:self.events.put(('transfer',event))):
                    try:msg=self.perform(action,game)
                    except Exception:traceback.print_exc();raise
            self.events.put(('done',True,msg))
        except Exception as e:self.events.put(('done',False,str(e)+(('\nRegistro: '+str(log)) if log else '\nNão foi possível criar o registro. Confira a permissão da pasta local.')))
    def poll(self):
        try:
            while True:
                event=self.events.get_nowait()
                if event[0]=='log':
                    self.log_path=event[1];self.log_button.state(['!disabled']);continue
                if event[0]=='progress':
                    self.status.set(event[1]);self.add_history(event[1]);self.bar.stop();self.bar.configure(mode='indeterminate');self.bar.start(18);self.transfer.set('Preparando a próxima operação...');continue
                if event[0]=='transfer':
                    e=event[1];self.bar.stop();self.bar.configure(mode='determinate');self.bar['value']=100*e['done']/e['total'] if e['total'] else 0
                    speed=e['done']/max(e['seconds'],.001)
                    self.transfer.set(f"{e['operation']} {e['file']} · {amount(e['done'])} de {amount(e['total'])}"+(f" · {amount(speed)}/s" if e['seconds']>.5 else ''));continue
                _,ok,msg=event;self.busy=False;self.bar.stop();self.bar.configure(mode='determinate');self.bar['value']=100 if ok else 0;self.set_controls(True)
                self.status.set('Concluído' if ok else 'Não foi possível concluir');self.transfer.set('Operação finalizada.' if ok else 'Consulte o erro e o registro abaixo.');self.add_history(msg)
                if not ok:messagebox.showerror('Não foi possível concluir',msg)
        except queue.Empty:pass
        if hasattr(self,'started'):
            seconds=int(time.monotonic()-self.started);self.elapsed.set(('Tempo decorrido: ' if self.busy else 'Concluído em ')+f'{seconds//60:02d}:{seconds%60:02d}')
            if not self.busy:del self.started
        self.root.after(150,self.poll)
