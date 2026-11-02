# Atualizações pelo próprio aplicativo: proposta

Não implementado na 0.8.1. O instalador é um EXE portátil: não depende de serviço residente, início automático ou instalação adicional de um gerenciador no Windows.

| Opção | Esforço relativo | Benefício | Limite |
|---|---|---|---|
| Botão Verificar atualizações, abre a release | Baixo | O usuário descobre versões sem procurar | Download e execução continuam manuais |
| Baixar a versão compatível pelo aplicativo, conferir SHA-256 e entregar ao usuário | Médio | Menos etapas, preserva a decisão de atualizar | Requer tratamento de rede, cache, canal experimental, disco e integridade |
| Autoatualizar o instalador e aplicar sozinho | Alto | Fluxo mais automático | Exige recuperação após falhas, substituição de arquivo em uso e verificação confiável da origem |

Recomendação: começar pela primeira opção; depois implementar download verificado com confirmação. Nenhum serviço precisa permanecer rodando. A alteração do jogo continua exigindo que ele esteja fechado, com backup e recuperação.

O repositório publica pré-releases: uma futura consulta deve considerar o canal experimental explicitamente. O endpoint latest do GitHub exclui pré-releases. Validar também versão do jogo suportada, versão da integração, notas, limites, origem HTTPS e hashes dos arquivos; não confiar só no número maior.

Fonte: [API oficial de releases do GitHub](https://docs.github.com/en/rest/releases/releases). Esta é uma proposta de desenho, não uma atualização automática já instalada.
