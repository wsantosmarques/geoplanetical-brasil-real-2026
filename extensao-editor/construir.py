import pathlib,json,re,shutil,os
from asar_local import Asar,digest,update_exe_integrity
ROOT=pathlib.Path(__file__).resolve().parents[1]
GAME=pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\Geoplanetical')
PUB=ROOT/'Publicacao_Brasil_2026_v050'
OUT=ROOT/'extensao'/'preparado'
EXPECTED='7dd2a1b9100a0e1ac430bdb67a6ed036a02783765f1e7c0ebe4184849caafe00'
EXPECTED_HEADER='dd101fe1a0f2d79773301a8c54094832f24fde2b88fbf5004f71090801417df0'
EXPECTED_EXE='a5bf1c2614bc0c9f563d0413943f04a9ffe9c2e7a8b831f8f495845647512335'
def build(game,out,catalog_file):
    out.mkdir(exist_ok=True);(out/'resources').mkdir(exist_ok=True)
    ar=Asar(game/'resources/app.asar');version=json.loads(ar.read('package.json'))['version']
    if ar.header_hash!=EXPECTED_HEADER or digest((game/'Geoplanetical.exe').read_bytes())!=EXPECTED_EXE:raise ValueError('Instalacao diferente do original estudado; recusar patch')
    bundle=ar.read('renderer/app.bundle.js')
    if version!='1.0.6' or digest(bundle)!=EXPECTED:raise ValueError('Versao/hash nao estudados')
    catalog=json.loads(catalog_file.read_text(encoding='utf8'))
    if len(catalog)!=20 or len({p['selector'] for p in catalog})!=20:raise ValueError('Catalogo invalido')
    app=bundle.decode();matches=list(re.finditer(r'function\s+([\w$]+)\(A=null\)\{let e=[\w$]+\("parties",\(\)=>\{let t=\[\];',app))
    if len(matches)!=1:raise ValueError('Funcao de catalogo ausente/ambigua')
    start=matches[0].start();end=app.index('function ',start+10);old=app[start:end]
    if old.count('return t.sort(')!=1:raise ValueError('Ancora ausente/ambigua')
    addition='if(Array.isArray(window.__BRASIL_EDITOR_CATALOG__)){t=t.filter(q=>q.countryKey!=="076");t.push(...window.__BRASIL_EDITOR_CATALOG__);}return t.sort('
    new=old.replace('return t.sort(',addition);app=app[:start]+new+app[end:]
    status={'version':'0.1.0','gameVersion':'1.0.6','visualOnly':True,'requiresCompanionSave':True}
    prefix='/* Brasil Real: extensao visual local 0.1.0. Nao modifica simulacao ou saves. */\nwindow.__BRASIL_REAL_EDITOR__='+json.dumps(status)+';window.__BRASIL_EDITOR_CATALOG__='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n'
    app=prefix+app
    locale=json.loads(ar.read('renderer/locales/pt-BR.json'))
    for key,value in list(locale.items()):
        if value=='Jogo base':locale[key]='Referência (base/cenário)'
        if value=='Estúdio de mods':locale[key]='Estúdio de mods · Brasil Real 0.1'
    replacements={'renderer/app.bundle.js':app.encode(),'renderer/locales/pt-BR.json':json.dumps(locale,ensure_ascii=False,separators=(',',':')).encode()}
    built=ar.append_replacements(out/'resources/app.asar',replacements)
    exe=update_exe_integrity(game/'Geoplanetical.exe',out/'Geoplanetical.exe',ar.header_hash,built.header_hash)
    result={'version':'0.1.0','gameVersion':version,'originalHeaderSha256':ar.header_hash,'patchedHeaderSha256':built.header_hash,'originalBundleSha256':EXPECTED,'patchedBundleSha256':digest(replacements['renderer/app.bundle.js']),'replacedFiles':list(replacements),'simulationWorkerUnchanged':ar.entry('renderer/simulation-worker.bundle.js')==built.entry('renderer/simulation-worker.bundle.js'),**exe}
    if not result['simulationWorkerUnchanged']:raise ValueError('Motor da simulacao alterado')
    (out/'construcao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');return result
def main():print(json.dumps(build(GAME,OUT,PUB/'extensao-editor/catalogo-brasil-2026.json')))
if __name__=='__main__':main()
