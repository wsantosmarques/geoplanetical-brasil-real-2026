# Ministérios brasileiros: investigação e próximo protótipo

**Corte: 1º de janeiro de 2026.** A pesquisa reúne 38 postos: 32 pastas/órgãos, incluindo a CGU, mais seis postos com status de ministro. Este inventário não foi instalado como gabinete funcional. O complemento atual continua com cinco pastas abstratas, quatro titulares reais e Interior fictício.

[Conferência com o guia oficial de mods e console](wiki-oficial.md).

## O limite é do motor

| Camada | Comportamento encontrado na 1.0.7 | Mudança necessária |
|---|---|---|
| Formação | `J8` contém economy, defense, interior, foreign, justice; `p1Q`, `py` preenchem até cinco. | Catálogo por país/cenário e contagem derivada dele. |
| Reforma de gabinete | `b1Q`, `oR`, `L1Q` reconstroem ou substituem titulares conforme coalizão. | Preservar cargo adicional em troca de governo e permitir sua nomeação. |
| Conselho e candidatos | `ABB` valida cargo contra `J8`; `_AB`, `ICC`, `dCC`, `aCC`, `cCC` têm cinco rotas. | Incluir candidatos, ações e rotas do cargo novo em todas as camadas. |
| Interface | Algumas listas iteram `cabinetIds`, mas rótulos e ações reconhecem apenas cinco chaves. | Exibir titular, pasta, ações e efeito; não só uma foto adicional. |
| Efeitos | Economia/Defesa e outros caminhos usam cargos fixos. `M4Q` agrega atributos de todo o gabinete. | Definir efeito setorial explícito e medir efeitos colaterais de aumentar o número de ministros. |
| Save e reload | `CDQ` salva `cab`; `wBB` não limita a cinco referências, `rDQ` restaura. | Persistir também o catálogo/variante do gabinete; impedir que reforma posterior volte a cinco. |

Também é preciso representar acúmulo de funções sem clonar pessoas: Alckmin é vice e titular do MDIC; Luciana Santos já existe como dirigente licenciada e titular de CT&I. O campo único `role`/`office` da pessoa exige um mapa de vínculos por pasta para preservar esses papéis.

Apenas anexar nomes a `cabinetIds` pode produzir titulares decorativos ou alterar agregados de corrupção sem função própria. Não recomendamos distribuir isso como ministérios implementados.

## Opções

| Caminho | Ganho | Custo/risco |
|---|---|---|
| Quadro histórico separado | Mostra todos os titulares com fontes, sem prometer mecânicas inexistentes. | Baixo; permanece informação histórica. |
| Um cargo adicional completo | Valida o caminho de nomeação, conselho, efeito, reforma e persistência. | Médio/alto; precisa de testes no motor e na interface. |
| Todas as pastas de uma vez | Maior semelhança visual imediata. | Alto risco de ministros decorativos, duplicar efeitos e quebrar reformas. |

**Recomendação: Educação primeiro, em cópia isolada e campanha nova.** Camilo Santana é o titular histórico; isso não significa que já haja uma pasta funcional dele nesta versão.

## Critérios do protótipo de Educação

1. Identificar uma métrica nativa do setor educacional e estabelecer um efeito mensurável antes de codificar o cargo.
2. Registrar um catálogo brasileiro de seis cargos; outros países e saves antigos mantêm seus cinco.
3. Gerar titular/candidatos, permitir nomeação e substituição e encaminhar o cargo pelo DTO.
4. Implementar conselho/ação com custo e efeito identificáveis, evitando multiplicar um efeito existente duas vezes.
5. Validar reforma da coalizão, troca de governo, demissão, sucessão e preenchimento de vaga.
6. Salvar/recarregar o catálogo e os vínculos. Verificar que um sucessor não herda identidade ou foto histórica por ocupar a mesma pasta.
7. Comparar campanha com/sem o cargo, incluindo finanças e agregados pessoais; depois ampliar por grupos de setores.

Nenhum desses novos cargos foi ativado nas partidas do usuário. A investigação é sobre a 1.0.7 exata estudada; uma atualização exige revisar as âncoras do patch.

## Inventário histórico

Base: [Mensagem ao Congresso Nacional 2025, Casa Civil](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf), atualizada pelas nomeações de 2025 indicadas em cada fonte. O [JSON](governo-2026-inventario.json) contém as 38 linhas e referências. Férias e substituições temporárias de expediente não substituem o titular no inventário.

| Pasta/posto | Titular em 01/01/2026 | Fonte |
|---|---|---|
| Agricultura e Pecuária | Carlos Fávaro | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Cidades | Jader Filho | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Ciência, Tecnologia e Inovação | Luciana Santos | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Comunicações | Frederico de Siqueira Filho | [Referência](https://www.gov.br/mcom/pt-br/acesso-a-informacao/perguntas-frequentes/o-ministerio-das-comunicacoes/quem-e-o-ministro-das) |
| Cultura | Margareth Menezes | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Defesa | José Múcio Monteiro | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Desenvolvimento Agrário e Agricultura Familiar | Paulo Teixeira | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Desenvolvimento e Assistência Social, Família e Combate à Fome | Wellington Dias | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Desenvolvimento, Indústria, Comércio e Serviços | Geraldo Alckmin | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Direitos Humanos e da Cidadania | Macaé Evaristo | [Referência](https://www.gov.br/mdh/pt-br/assuntos/noticias/2024/setembro/macae-evaristo-e-nomeada-ministra-dos-direitos-humanos-e-da-cidadania) |
| Educação | Camilo Santana | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Empreendedorismo, da Microempresa e da Empresa de Pequeno Porte | Márcio França | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Esporte | André Fufuca | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Fazenda | Fernando Haddad | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Gestão e Inovação em Serviços Públicos | Esther Dweck | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Igualdade Racial | Anielle Franco | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Integração e Desenvolvimento Regional | Waldez Góes | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Justiça e Segurança Pública | Ricardo Lewandowski | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Meio Ambiente e Mudança do Clima | Marina Silva | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Minas e Energia | Alexandre Silveira | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Mulheres | Márcia Lopes | [Referência](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=05%2F05%2F2025&jornal=605&pagina=1) |
| Pesca e Aquicultura | André de Paula | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Planejamento e Orçamento | Simone Tebet | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Portos e Aeroportos | Silvio Costa Filho | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Povos Indígenas | Sonia Guajajara | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Previdência Social | Wolney Queiroz | [Referência](https://www.gov.br/previc/pt-br/acesso-a-informacao-1/acordos-de-cooperacao-tecnica/44011-003070-2025-22.pdf) |
| Relações Exteriores | Mauro Vieira | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Saúde | Alexandre Padilha | [Referência](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=10%2F03%2F2025&jornal=604&pagina=1) |
| Trabalho e Emprego | Luiz Marinho | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Transportes | Renan Filho | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Turismo | Gustavo Feliciano | [Referência](https://www.gov.br/turismo/pt-br/composicao/gabinete-do-ministro/gustavo-costa-feliciano) |
| Controladoria-Geral da União | Vinícius Marques de Carvalho | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Casa Civil | Rui Costa | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Secretaria-Geral da Presidência | Guilherme Boulos | [Referência](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=21%2F10%2F2025&jornal=529&pagina=1) |
| Secretaria de Relações Institucionais | Gleisi Hoffmann | [Referência](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=10%2F03%2F2025&jornal=604&pagina=1) |
| Secretaria de Comunicação Social | Sidônio Palmeira | [Referência](https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=15%2F01%2F2025&jornal=529&pagina=1) |
| Gabinete de Segurança Institucional | Marcos Antonio Amaro dos Santos | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |
| Advocacia-Geral da União | Jorge Messias | [Referência](https://www.gov.br/casacivil/pt-br/assuntos/noticias/mensagem_pdf/mcn-2025-digital-v1.pdf) |

Mudanças de 2025 incorporadas: Frederico Siqueira Filho, Alexandre Padilha, Márcia Lopes, Wolney Queiroz, Guilherme Boulos, Gleisi Hoffmann e Sidônio Palmeira. Turismo já estava com Gustavo Feliciano desde 23/12/2025. Datas e nomes civis podem aparecer com grafias distintas; o JSON usa nomes públicos conhecidos. A lista-base não é uma fotografia pronta de janeiro de 2026: é uma reconstrução com fontes datadas.
