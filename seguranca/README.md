# Verificações dos pacotes

Os arquivos distribuídos têm SHA-256 publicado em cada release. A análise local com Microsoft Defender é registrada por versão, incluindo nomes, hashes, mecanismo, assinaturas e resultado.

- [Verificação no GitHub Actions da 0.8.0](github-actions-0.8.0.json): passou, nenhuma ameaça detectada; [execução auditável](https://github.com/wsantosmarques/geoplanetical-brasil-real-2026/actions/runs/41373376571).
- [Análise local da 0.8.0](defender-0.8.0.json): nenhuma ameaça detectada nessa verificação.
- [Análise local da 0.7.0](defender-0.7.0.json): nenhuma ameaça detectada nessa verificação.
- [Execução manual no GitHub Actions](../.github/workflows/antivirus.yml): baixa os arquivos da release, confere hashes e analisa sem executar o instalador. Só roda quando acionada; não há agendamento ou envio automático a serviços externos de amostras.

Os relatórios do GitHub ficam no artefato do job, por 90 dias. Um scanner indisponível ou um erro não é apresentado como resultado limpo. Uma detecção precisa ser investigada; não orientamos desativar o antivírus.

O instalador ainda não tem assinatura digital. Ausência de detecção nessa análise não prova ausência de vulnerabilidades ou de ameaças futuras. Os relatórios não são certificados de aprovação da Microsoft, GitHub ou Steam.

O executável completo fica no GitHub. A Oficina aceita apenas os arquivos de apresentação suportados pelo jogo; a página da Steam deve apontar para a release e esta evidência, sem prometer que a Oficina instala ou certifica o EXE.
