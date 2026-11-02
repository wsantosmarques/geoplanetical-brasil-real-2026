# Brasil Real 2026 | 0.7.0 experimental

![Capa](imagens/capa.png)

[**Baixar instalador único para Windows**](https://github.com/wsantosmarques/geoplanetical-brasil-real-2026/releases/download/v0.7.0-experimental/BrasilReal2026-Instalador-0.7.0.exe)

Brasil em **1º de janeiro de 2026**: 20 partidos em campanhas novas, Câmara com 513 cadeiras e Senado com 81. A versão 0.7 acrescenta 47 identidades históricas e 42 fotos reais, com fontes, créditos e licenças individuais.

## Instalação

Feche o Geoplanetical, execute o `.exe`, confira a pasta detectada e clique em **Instalar / atualizar**. Depois, abra **Novo jogo → Brasil**. Em **Política → Personalidades**, o quadro histórico apresenta presidências nacionais, líderes na Câmara, presidente, vice e ministros compatíveis com o motor.

Requer Windows e os arquivos exatos da versão **1.0.7 estudada**. Esta atualização recusa versões diferentes antes de substituir o jogo. O instalador detecta a Steam, inclui os arquivos necessários e dispensa Python. Reserve cerca de 12 GB para cópias temporárias e backups; o executável ainda não possui assinatura digital.

## O que funciona

- Escolha dos 20 partidos desde Novo jogo, inclusive PT; também é possível liderar o país.
- Os mesmos 20 partidos na simulação, nas câmaras e nas intenções de voto dos 17 grupos sociais brasileiros.
- Estúdio com os 20 partidos e indicadores de esquerda/direita.
- 47 pessoas distintas: direções nacionais, lideranças na Câmara, presidente, vice e quatro titulares ministeriais nativos. REDE tem dois co-porta-vozes; PCdoB distingue presidência interina de Nádia Campeão e presidência licenciada de Luciana Santos.
- Talíria Petrone aparece uma única vez, filiada ao PSOL, com liderança compartilhada da federação PSOL–REDE. Lindbergh Farias mantém filiação ao PT e referência da Federação Brasil da Esperança.
- Nomes e retratos nas telas nativas de pessoas e governo, além do quadro histórico com fontes. A chave do retrato acompanha a pessoa e persiste no save; sucessores gerados pelo motor não herdam a foto por ocupar o cargo.
- Fazenda: Fernando Haddad; Defesa: José Múcio Monteiro; Relações Exteriores: Mauro Vieira; Justiça: Ricardo Lewandowski. O jogo usa cinco pastas abstratas, sem representar todas as pastas brasileiras.

## Limitações desta versão

**Cinco fotos pendentes de fonte reutilizável confirmada:** Antonio Rueda, Paula Coradi, Marcus Vinícius de Vasconcelos Ferreira, Iaraci Dias e Eduardo Ribeiro. Eles têm nome e referência histórica, com o aviso “Foto pendente”. As 42 imagens existentes são fotografias, sem retratos gerados por IA. Algumas são anteriores a 2025.

**Interior permanece fictício:** não foi atribuída uma equivalência brasileira que o motor não estabelece. Luciana Santos aparece com sua função histórica de ministra de Ciência, Tecnologia e Inovação no quadro, mas esta versão não cria uma nova pasta executável de CT&I. Demais personagens auxiliares e civis do jogo podem continuar genéricos.

O quadro documenta cargos de 01/01/2026; não impõe as trocas reais dos meses seguintes. O motor pode dar outros cargos às pessoas durante a campanha. Atributos, comportamento e ideologias individuais são parâmetros de jogo, não avaliações factuais. Parentes fictícios herdados são desvinculados na inicialização; eventos familiares futuros continuam sendo simulação. Datas de nascimento não confirmadas ficam sem informação.

O apoio inicial é calibrado a partir das cadeiras, não é pesquisa eleitoral. Ideologias, cores, organização partidária, núcleo de governo e regras eleitorais incluem aproximações. Não é um cadastro de todos os deputados e senadores nem uma reprodução integral das instituições brasileiras. A versão 0.7 não amplia o número de ministérios do motor.

## Partidas existentes

**As identidades novas exigem nova campanha.** O instalador não abre, converte nem regrava saves. Campanhas iniciadas na versão 0.6 ou antes conservam seus personagens. O cenário antigo distribuído separadamente também não recebe as 47 identidades.

O mod de apresentação de nomes e retrato de Lula pode mudar a apresentação visual de campanhas anteriores enquanto estiver ativo, sem regravar o save. Para removê-lo, desative o mod no gerenciador.

## Oficina e complemento

| Instalação | Resultado |
|---|---|
| Mod de apresentação da Oficina, sozinho | Nomes/siglas e apresentação de Lula. Não cria 20 partidos ou os demais dirigentes/ministros. |
| Instalador completo `.exe` | Mod de apresentação + integração 0.3.0, novos presets, 47 identidades e 42 fotos. Requer nova campanha para esses dados. |

A publicação Steam é separada. A Oficina não instala o patch do executável/ASAR. As versões anteriores permanecem em [Releases](https://github.com/wsantosmarques/geoplanetical-brasil-real-2026/releases).

## Backups e restauração

Originais do jogo ficam em `%LOCALAPPDATA%/BrasilRealEditor/backups`; arquivos anteriores do mod e configuração em `mod-backups`. **Restaurar jogo** recupera os arquivos do jogo, preservando mods e saves. Atualizações da Steam podem remover a integração e exigem nova conferência de compatibilidade. Recibos e hashes impedem restauração sobre arquivos de outra versão. Os fuses e a verificação de integridade do Electron continuam ativos.

## Fontes e direitos das imagens

[Cadastro e fontes de cada pessoa](fontes/identidades/pessoas-2026.json) · [Créditos e licenças dos 42 retratos](fontes/identidades/CREDITOS.md).

As licenças de cada fotografia permanecem aplicáveis, incluindo atribuição e compartilhamento pela mesma licença quando exigido. Arquivos baixados do Commons são preservados sem edição local, com enquadramento por CSS. O uso não indica apoio de pessoas ou instituições ao projeto. A capa do mod foi criada com IA; os retratos de políticos são fotografias reais.

O código calcula o patch a partir da instalação local. Este repositório e o instalador não redistribuem o executável ou o ASAR original do jogo.

## Validação

Testes isolados da 0.7: duas sementes, 47 identidades, filiações, quatro ministros, salvar/recarregar e avanço de um dia. Teste desktop em cópia separada: 20 opções no Novo jogo, Câmara/Senado 513/81, 47 registros históricos, 42 retratos carregados tanto no quadro quanto nos cartões nativos, eleitorado com 20 legendas nos 17 grupos e nenhum erro de execução. O instalador empacotado verifica 47 pessoas e 42 fotos sem depender de Python externo.

Na 0.6 foram testados 310 dias com eleições e recarga na 1.0.6 e 31 dias na 1.0.7. Essas provas anteriores não são um teste de longo prazo das identidades da 0.7. Esta é uma versão experimental para novas campanhas.

## Capturas

![Presidências e líderes na Câmara com fotos e fontes](imagens/liderancas-2026.png)

![Ministros nos cartões nativos do governo](imagens/ministros-2026.png)

![20 opções de partido](imagens/escolha-20.png)
