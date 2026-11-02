# Prévia da Oficina

A Steam permite visibilidade privada para revisar um item antes da liberação pública. Nesta tentativa, usando o publicador original do jogo e o SDK da instalação licenciada, `CreateItem` retornou **access denied**. Não foi confirmado item nem link. Não foi possível determinar a causa exata apenas com esse retorno.

O erro ocorreu na etapa de criação, antes da atualização de conteúdo. Nenhum aceite de acordo legal foi automatizado. Um diário local impede repetir uma criação ambígua sem conferir os itens da conta. Não há envio público confirmado.

- [Prévia local em HTML](previa-oficina.html), para abrir depois de baixar/clonar o repositório.
- [Captura da prévia local](../imagens/previa-oficina-local.png).
- [Descrição preparada](../oficina/DESCRICAO-STEAM-BBCODE.txt).
- [Documentação Steam de CreateItem e seus resultados](https://partner.steamgames.com/doc/api/ISteamUGC#CreateItem).

Próximo passo: conferir os itens e avisos da Oficina na conta Steam, e testar pelo estúdio nativo quando não houver item anterior pendente. Se a mesma recusa ocorrer, investigar com o suporte da Steam ou com o desenvolvedor a permissão de publicação. O código do erro não demonstra, por si só, banimento, falta de compra ou necessidade de aceitar termos; não afirmamos nenhuma dessas causas.

A visibilidade desejada continua privada. A publicação pública só deverá ocorrer após revisão da fidelidade, licenças e apresentação. O EXE permanece um download externo do GitHub; não é instalado automaticamente pela Oficina.
