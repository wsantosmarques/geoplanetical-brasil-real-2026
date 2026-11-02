"""Identidades históricas e retratos locais, somente para campanhas novas."""
import pathlib,json,base64,hashlib,re,html

def replace_once(s,old,new):
    if s.count(old)!=1:raise ValueError('Contrato de identidades mudou: '+old[:90])
    return s.replace(old,new)

def patch_people(app,worker,root,version):
    if version!='1.0.7':raise ValueError('Os retratos e as identidades 0.7 exigem Geoplanetical 1.0.7 estudado')
    data=json.loads((root/'identidades/pessoas-2026.json').read_text(encoding='utf8'));keys={p['key'] for p in data['people']}
    if len(keys)!=47 or len(data['parties'])!=20:raise ValueError('Cadastro de pessoas incompleto')
    photos={};public=json.loads(json.dumps(data))
    for p in public['people']:
        photo=p.get('photo')
        if not photo:continue
        path=(root/'identidades'/photo['file']).resolve();base=(root/'identidades/fotos').resolve()
        if path.parent!=base:raise ValueError('Caminho de foto fora do pacote')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=photo['sha256']:raise ValueError('Retrato corrompido: '+p['name'])
        mime='image/png' if raw.startswith(b'\x89PNG') else 'image/jpeg' if raw.startswith(b'\xff\xd8') else None
        if not mime:raise ValueError('Formato de retrato inesperado')
        photos[p['key']]='data:'+mime+';base64,'+base64.b64encode(raw).decode('ascii')
        photo['authorText']=html.unescape(re.sub('<[^>]+>','',photo['author']))
    compact=lambda d:json.dumps(d,ensure_ascii=False,separators=(',',':'))
    # Só a simulação carrega o cadastro factual. URLs/bytes de imagem ficam no renderer.
    worker='const BR2026_PEOPLE='+compact(data)+';\n'+(root/'pessoas-bootstrap.js').read_text(encoding='utf-8-sig')+'\n'+worker
    worker=replace_once(worker,'let v=()=>{u("player","start"),P.start(Q,','let v=()=>{u("player","start"),!C&&BR2026ApplyPeople(P,k3),P.start(Q,')
    worker=replace_once(worker,'function No(A){return A?{id:A.id||null,','function No(A){return A?{brRealPersonId:typeof A._brRealPersonId==="string"?A._brRealPersonId:null,id:A.id||null,')
    start=worker.index('function twA(');end=worker.index('function ',start+10);part=worker[start:end]
    part=replace_once(part,'if(t.length>=DwA)break;','if(t.length>=DwA&&!A.people.get(I)?._brRealPersonId)continue;')
    worker=worker[:start]+part+worker[end:]
    app='const BR2026_CATALOG='+compact(public)+';const BR2026_PHOTOS='+compact(photos)+';\n'+(root/'pessoas-ui.js').read_text(encoding='utf-8-sig')+'\n'+app
    app=replace_once(app,'function t2(A,e,t){if(!A||','function t2(A,e,t){const brKey=BR2026Key(A);if(brKey)return BR2026_PHOTOS[brKey]||null;if(!A||')
    app=replace_once(app,'function Ne(A){return IW(A)?.name||A?.name||""}','function Ne(A){return BR2026Record(A)?.name||IW(A)?.name||A?.name||""}')
    # Acrescenta quadro histórico sem substituir as funções nativas dos personagens.
    app=replace_once(app,'this._persApplyFilter(A);for(let E of A.querySelectorAll("[data-fiche]"))','this._persApplyFilter(A);BR2026HistoricalPanel(A,e);for(let E of A.querySelectorAll("[data-fiche]"))')
    return app,worker
