# Assinatura digital: o que falta

O instalador ainda não possui assinatura pública Authenticode. Análise antivírus e SHA-256 não substituem um certificado de identidade do editor. Não foi gerado certificado autoassinado para simular confiança pública.

| Caminho | Custo e condição | Situação |
|---|---|---|
| SignPath Foundation | Gratuito para projetos elegíveis, com licença OSI para os componentes e aprovação | Candidato a investigar; não solicitado nem aprovado |
| Certificadora comercial | Certificado, validação do responsável e modalidade de armazenamento; custo depende do produto/país | Exige confirmar elegibilidade brasileira e orçamento antes de contratar |
| Microsoft Artifact Signing Public Trust | Plano Basic anunciado a US$ 9,99/mês | A lista de países de identidade pública consultada não inclui Brasil; a região técnica Brazil South não elimina essa restrição |

Recomendação: verificar primeiro a elegibilidade do projeto para SignPath Foundation; se não couber, comparar certificado comercial para a identidade legal do responsável. Nenhum serviço foi contratado, chave criada, documento enviado ou certificado instalado.

A assinatura válida identifica o editor e permite verificar a integridade assinada. Ela não garante que todo aviso do SmartScreen desapareça imediatamente: reputação do arquivo/editor também participa da decisão. Assinar depois muda o hash do EXE; os arquivos assinados precisariam de novos hashes, análises e publicação identificada.

Fontes oficiais consultadas em 01/11/2026:

- [Microsoft: reputação do SmartScreen](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation)
- [Microsoft: países elegíveis e regiões técnicas](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart)
- [Microsoft: preço anunciado do serviço](https://azure.microsoft.com/en-us/products/artifact-signing)
- [SignPath Foundation: condições](https://signpath.org/terms.html)
- [Certum: famílias de certificado](https://www.certum.eu/en/code-signing-certificates/)
