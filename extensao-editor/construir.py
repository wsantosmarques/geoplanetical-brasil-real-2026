"""Brasil Real 0.3: presets de novas campanhas, preview e editor."""
import pathlib,json,re
from pessoas_patch import patch_people
from asar_local import Asar,digest,update_exe_integrity
EXPECTED_HEADER='dd101fe1a0f2d79773301a8c54094832f24fde2b88fbf5004f71090801417df0'
EXPECTED_EXE='a5bf1c2614bc0c9f563d0413943f04a9ffe9c2e7a8b831f8f495845647512335'
EXPECTED='7dd2a1b9100a0e1ac430bdb67a6ed036a02783765f1e7c0ebe4184849caafe00'
HERE=pathlib.Path(__file__).resolve().parent
SUPPORTED={
 '1.0.6':{'header':EXPECTED_HEADER,'exe':EXPECTED_EXE,'renderer':EXPECTED,'coalRender':'Ige','coalWorker':'b3Q','width':'L'},
 '1.0.7':{'header':'0bdcf9c5e230260f8a35a9df79721532df57f314ba8e5133736815bbf06e8273','exe':'d445eb1d3d6c19251c4f533eebb64e7a9655c2ab9535f0338f3c50f4d17042de','renderer':'b3f99bd638f89e7ae7b7e6936d91a78e9faa54e06632e5c8305bd54851a3db19','coalRender':'cce','coalWorker':'L9Q','width':'x'}
}
def identify(game):
    ar=Asar(game/'resources/app.asar');version=json.loads(ar.read('package.json'))['version'];allowed=SUPPORTED.get(version)
    if version!='1.0.7' or not allowed or ar.header_hash!=allowed['header'] or digest((game/'Geoplanetical.exe').read_bytes())!=allowed['exe']:raise ValueError('Arquivos diferentes da versao 1.0.7 estudada')
    return version
def object_span(s,start):
    if s[start]!='{':raise ValueError('Inicio de objeto incorreto')
    depth=0;quote=None;escape=False
    for n in range(start,len(s)):
        ch=s[n]
        if quote:
            if escape:escape=False
            elif ch=='\\':escape=True
            elif ch==quote:quote=None
        elif ch in ('"',"'",'`'):quote=ch
        elif ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return start,n+1
    raise ValueError('Objeto incompleto')
def replace_object(s,needle,value):
    if s.count(needle)!=1:raise ValueError('Ancora ausente/ambigua: '+needle)
    a=s.index(needle)+needle.index('{');a,b=object_span(s,a)
    return s[:a]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+s[b:]
def patch_seed(s,seed):
    s=replace_object(s,'"076":{archetype:"presidential-republic",rulingPartyId:"PT"',seed['preset'])
    s=replace_object(s,'"076":{seats:81,sel:"equal-per-state"',seed['bicameral'])
    return s
def build(game,out,catalog_file):
    out.mkdir(exist_ok=True);(out/'resources').mkdir(exist_ok=True)
    version=identify(game);ar=Asar(game/'resources/app.asar');allowed=SUPPORTED[version]
    if ar.header_hash!=allowed['header']:raise ValueError('ASAR mudou durante a identificacao')
    bundle=ar.read('renderer/app.bundle.js');worker=ar.read('renderer/simulation-worker.bundle.js')
    if digest(bundle)!=allowed['renderer']:raise ValueError('Renderer inesperado')
    if digest(worker)!=ar.entry('renderer/simulation-worker.bundle.js')['integrity']['hash']:raise ValueError('Worker diferente do conteudo estudado')
    locale_bytes=ar.read('renderer/locales/pt-BR.json')
    if digest(locale_bytes)!=ar.entry('renderer/locales/pt-BR.json')['integrity']['hash']:raise ValueError('Locale corrompido')
    catalog=json.loads(catalog_file.read_text(encoding='utf8'));seed=json.loads(catalog_file.with_name('novo-jogo-brasil-2026.json').read_text(encoding='utf8'))
    if len(catalog)!=20 or {p['id'] for p in seed['preset']['parties']}!={p['partyId'] for p in catalog}:raise ValueError('Catalogo/preset incoerentes')
    app=patch_seed(bundle.decode(),seed);new_worker=patch_seed(worker.decode(),seed)
    # O bootstrap presidencial nativo reduz a coalizao ao partido lider.
    # Preserva a coalizao explicita do novo preset brasileiro, sem alterar saves de quatro partidos.
    for marker,old,new in [
        ('function '+allowed['coalWorker']+'(', 'B.coalition=B.rulingPartyId?[B.rulingPartyId]:[]', 'B.coalition=A.key==="076"&&B.parties.some(p=>p.id==="PCdoB")&&B.coalition?.includes(B.rulingPartyId)?B.coalition:(B.rulingPartyId?[B.rulingPartyId]:[])'),
    ]:
        start=new_worker.index(marker);end=new_worker.index('function ',start+10);piece=new_worker[start:end]
        if piece.count(old)!=1:raise ValueError('Bootstrap de coalizao mudou')
        new_worker=new_worker[:start]+piece.replace(old,new)+new_worker[end:]
    fn=allowed['coalRender'];start=app.index('function '+fn+'(');end=app.index('function ',start+10);piece=app[start:end];old='e.coalition=e.rulingPartyId?[e.rulingPartyId]:[]'
    if piece.count(old)!=1 or app.count(fn+'({pol:e})')!=1:raise ValueError('Preview de coalizao mudou')
    piece=piece.replace(old,'e.coalition=A.key==="076"&&e.parties.some(p=>p.id==="PCdoB")&&e.coalition?.includes(e.rulingPartyId)?e.coalition:(e.rulingPartyId?[e.rulingPartyId]:[])')
    app=(app[:start]+piece+app[end:]).replace(fn+'({pol:e})',fn+'({key:A.key,pol:e})')
    width=allowed['width'];old='style="width:${'+width+'}%;background:${i(k.id)}"'
    if app.count(old)!=1:raise ValueError('Barra de eleitorado mudou')
    app=app.replace(old,'style="width:${t.key==="076"?k.v*100:'+width+'}%;background:${i(k.id)}"')
    for old,new in [
        ('top:I.slice(0,3).map(([P,v])=>({id:P,v}))','top:I.slice(0,B.key==="076"?20:3).map(([P,v])=>({id:P,v}))'),
        ('top:t.slice(0,3).map(([n,s])=>({id:n,v:s}))','top:t.slice(0,B.key==="076"?20:3).map(([n,s])=>({id:n,v:s}))')]:
        if new_worker.count(old)!=1:raise ValueError('Resumo de eleitorado mudou')
        new_worker=new_worker.replace(old,new)
    # Brasil permite escolher tambem PT; outras nacoes mantem a lista nativa.
    needle='g=l.filter(c=>!c.isGovernmentLead)'
    if app.count(needle)!=1:raise ValueError('Filtro de partidos jogaveis mudou')
    app=app.replace(needle,'g=l.filter(c=>String(A.key)==="076"||!c.isGovernmentLead)')
    matches=list(re.finditer(r'function\s+([\w$]+)\(A=null\)\{let e=[\w$]+\("parties",\(\)=>\{let t=\[\];',app))
    if len(matches)!=1:raise ValueError('Catalogo do editor mudou')
    start=matches[0].start();end=app.index('function ',start+10);old=app[start:end]
    if old.count('return t.sort(')!=1:raise ValueError('Ordenacao de catalogo mudou')
    app=app[:start]+old.replace('return t.sort(','if(Array.isArray(window.__BRASIL_EDITOR_CATALOG__)){t=t.filter(q=>q.countryKey!=="076");t.push(...window.__BRASIL_EDITOR_CATALOG__);}return t.sort(')+app[end:]
    prefix='/* Brasil Real 0.3.1: novos jogos e editor. Nao migra saves existentes. */\nwindow.__BRASIL_REAL_EDITOR__={version:"0.3.1",gameVersion:'+json.dumps(version)+',newGames:true};window.__BRASIL_EDITOR_CATALOG__='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n'
    app,new_worker=patch_people(app,new_worker,catalog_file.parent,version)
    app=prefix+app
    locale=json.loads(locale_bytes)
    for key,value in list(locale.items()):
        if value=='Jogo base':locale[key]='Referência Brasil Real (novos jogos)'
        if value=='Estúdio de mods':locale[key]='Estúdio de mods · Brasil Real 0.3'
    changed={'renderer/app.bundle.js':app.encode(),'renderer/simulation-worker.bundle.js':new_worker.encode(),'renderer/locales/pt-BR.json':json.dumps(locale,ensure_ascii=False,separators=(',',':')).encode()}
    print('Montando o pacote do jogo (cerca de 4 GB). Aguarde a cópia...',flush=True)
    built=ar.append_replacements(out/'resources/app.asar',changed);exe=update_exe_integrity(game/'Geoplanetical.exe',out/'Geoplanetical.exe',ar.header_hash,built.header_hash)
    print('Pacote construído; integridade do executável conferida.',flush=True)
    if exe['originalExeSha256']!=allowed['exe']:raise ValueError('Executavel mudou durante a construcao')
    result={'version':'0.3.1','gameVersion':version,'originalHeaderSha256':ar.header_hash,'patchedHeaderSha256':built.header_hash,'newGamePresetPartyIds':[p['id'] for p in seed['preset']['parties']],'replacedFiles':list(changed),'fileHashes':{k:digest(v) for k,v in changed.items()},'existingSavesMigrated':False,**exe}
    (out/'construcao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');return result
