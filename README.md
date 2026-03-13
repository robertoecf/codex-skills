# Codex Skills

Colecao de skills pessoais para uso com Codex.

## Skills

### `learning`

Skill para ajudar o agente a:

- entender como um trecho de codigo funciona;
- explicar a logica por tras de um modulo ou fluxo;
- avaliar decisoes arquiteturais e tradeoffs;
- conectar implementacao a fundamentos de engenharia de software.

Foco da skill:

- separar fato, inferencia e recomendacao;
- explicar arquitetura a partir do codigo real;
- evitar opiniao vaga ou preferencia estilistica sem evidencia;
- usar uma lente de fundamentos, fluxo, estado, efeitos colaterais e limites de abstracao.

## Como usar

Exemplos de prompt:

- `Use $learning to explain this code path and why it was structured this way.`
- `Use $learning to evaluate whether this architecture is a good fit for the current constraints.`
- `Use $learning to compare this design with a service-layer alternative.`
- `Use $learning to teach me the fundamentals behind this module.`

## Estrutura

- `learning/SKILL.md`: instrucoes principais da skill
- `learning/agents/openai.yaml`: metadata para interface
- `learning/references/`: criterios de arquitetura e fundamentos de codigo
- `learning/scripts/session-bootstrap.sh`: checklist curto para o inicio de sessoes tecnicas

## Observacao

Esta repo contem a skill em formato portavel. No meu ambiente local, eu tambem reforco o uso automatico da `learning` via configuracao global do Codex.
