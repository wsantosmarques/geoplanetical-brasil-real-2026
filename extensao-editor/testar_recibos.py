"""Regressão do falso sucesso de recibo incompleto; nunca acessa instalação real."""
import pathlib,tempfile,json,copy,uuid
from unittest.mock import patch
import instalador_gui as gui
import instalar_extensao as core
with tempfile.TemporaryDirectory(prefix='meb-receipt-') as temp:
 root=pathlib.Path(temp);game=root/'game';(game/'resources').mkdir(parents=True)
 for name in core.NAMES:(game/name).write_bytes(b'ORIGINAL FIXTURE '+name.encode())
 baseline={n:(game/n).read_bytes() for n in core.NAMES};state=game/'brasil-real-editor-installed.json'
 valid={'operationId':uuid.uuid4().hex,'extensionVersion':'0.3.1','gameVersion':'1.0.7','game':str(game),'backup':str(root/'backup'),'state':'installed','files':{n:{'originalSha256':core.ORIGINAL_HASHES[n],'installedSha256':core.CURRENT_HASHES[n]} for n in core.NAMES}}
 bad=[]
 def case(label,change):
  r=copy.deepcopy(valid);change(r);bad.append((label,r))
 case('empty_files',lambda r:r.update(files={}))
 case('missing_file',lambda r:r['files'].pop('Geoplanetical.exe'))
 case('extra_path',lambda r:r['files'].update({'../another':r['files']['Geoplanetical.exe']}))
 case('invalid_hash',lambda r:r['files']['Geoplanetical.exe'].update(installedSha256='not-a-hash'))
 case('original_claimed_as_current',lambda r:r['files']['Geoplanetical.exe'].update(installedSha256=core.ORIGINAL_HASHES['Geoplanetical.exe']))
 case('wrong_original',lambda r:r['files']['Geoplanetical.exe'].update(originalSha256='0'*64))
 case('other_installation',lambda r:r.update(game=str(root/'other')))
 case('relative_game',lambda r:r.update(game='game'))
 case('relative_backup',lambda r:r.update(backup='backup'))
 case('same_game_backup',lambda r:r.update(backup=str(game)))
 case('unfinished_operation',lambda r:r.update(state='recovery-required'))
 case('wrong_game_version',lambda r:r.update(gameVersion='1.0.6'))
 case('operation_path_injection',lambda r:r.update(operationId='../outside'))
 bad.extend([('null',None),('array',[])])
 for label,receipt in bad:
  state.write_text(json.dumps(receipt),encoding='utf8');before=state.read_bytes()
  with patch.object(gui,'check_closed'),patch.object(gui,'prepare_names') as names,patch.object(gui,'_install') as install,patch.object(gui,'_restore') as restore:
   try:gui.perform('install',game);raise AssertionError('accepted '+label)
   except RuntimeError as e:assert 'Registro de instalação inválido' in str(e),(label,str(e))
   names.assert_not_called();install.assert_not_called();restore.assert_not_called()
  assert state.read_bytes()==before and all((game/n).read_bytes()==data for n,data in baseline.items())
 state.write_text('{invalid json',encoding='utf8')
 with patch.object(gui,'check_closed'),patch.object(gui,'prepare_names') as names:
  try:gui.perform('install',game);raise AssertionError('bad json accepted')
  except RuntimeError:pass
  names.assert_not_called()
 state.write_text(json.dumps(valid),encoding='utf8')
 assert core.load_receipt(game)['files']==valid['files']
 with patch.object(gui,'check_closed'),patch.object(gui,'sha',side_effect=lambda p:core.CURRENT_HASHES[p.relative_to(game).as_posix()]) as sha,patch.object(gui,'prepare_names',return_value={'test':True}),patch.object(gui,'commit_names') as commit,patch.object(gui,'_install') as install,patch.object(gui,'_restore') as restore:
  result=gui.perform('install',game)
  assert result.startswith('Concluído') and sha.call_count==2
  commit.assert_called_once_with({'test':True});install.assert_not_called();restore.assert_not_called()
print('PASS: 16 recibos inválidos recusados antes do preparo do mod; recibo válido e atualização idempotente aceitos. Somente temporários.')
