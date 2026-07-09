# Session Handoff

## Status (2026-07-09)

MVP da PRA 2026 + busca por assunto (TF-IDF client-side) + resposta em
linguagem natural via IA (Groq) citando a legislação. Netlify já conectado
ao GitHub (deploy contínuo) — falta só o usuário configurar a API key da
Groq para a parte de IA funcionar em produção (ver "Pendências").

## Pendências (só o usuário consegue fazer)

1. Criar conta em **console.groq.com**, gerar uma API key.
2. Adicionar `GROQ_API_KEY` (e opcionalmente `GROQ_MODEL`, padrão
   `llama-3.3-70b-versatile`) em **Netlify → servidor-pra-2026 → Site
   configuration → Environment variables**. Sem isso, o botão "🤖 Perguntar
   para a IA" sempre cai no fallback de erro amigável (comportamento já
   verificado e correto, só falta a chave para responder de verdade).

## Resposta por IA (Groq) — 2026-07-09

- `netlify/functions/perguntar.js` (novo): Netlify Function (Node, sem
  dependências novas) que busca `dist/dados/busca.json` (mesmo índice da
  busca por palavra-chave, fonte única `src/busca_legislacao.py`), monta um
  prompt de sistema instruindo o modelo a responder SÓ com base nesses
  trechos, sempre citando o título do documento, dizendo "não sei, consulte
  a CTRH" quando não souber, e nunca mencionar R$/metas. Chama a API da Groq
  (`llama-3.3-70b-versatile` por padrão). Guard-rail defensivo: se a
  resposta do modelo contiver `R$\d`, é bloqueada antes de chegar ao cliente.
- `netlify.toml`: `[functions] directory = "netlify/functions"`.
- `pwa/index.html` + `pwa/js/app.js`: botão "🤖 Perguntar para a IA" abaixo da
  busca por assunto (reaproveita o texto já digitado), chama
  `/.netlify/functions/perguntar`, destaca títulos de documentos conhecidos
  na resposta, mostra disclaimer fixo, e cai num fallback amigável se a
  function falhar/estiver offline — sem quebrar o resto do app.
- Verificado com Playwright headless (script ad-hoc, não commitado): botão
  aparece/some corretamente ao digitar, e o fallback de erro funciona
  (testado sem a function rodando — só dá pra testar a resposta real da IA
  depois que a `GROQ_API_KEY` estiver configurada no Netlify).
- Limitações conhecidas, aceitas para este MVP: sem rate limiting real (só
  cap de tamanho da pergunta), sem teste automatizado da function (projeto
  não tem infra de teste JS).

## O que foi feito na sessão anterior (2026-07-09, busca por assunto)

- `src/busca_legislacao.py` (novo): monta o índice de documentos pesquisáveis
  — glossário, indicadores I-IX, pendências de verificação, elegibilidade,
  nota do indicador, fórmula final, FAQ visível — mais um documento
  "ponteiro" (`cargo-especifico`) que direciona o servidor à busca por
  escola quando o assunto (Fator Geral/professor por cargo) depende do
  perfil da unidade. Sinônimos curados em `SINONIMOS`.
- `scripts/build_pwa.py`: nova `_gerar_busca_json()` gera `dist/dados/busca.json`,
  passa pelo mesmo guard-rail de valores monetários.
- `pwa/index.html` + `pwa/js/app.js`: nova caixa de busca (`#busca-assunto-input`)
  independente da busca por escola, com índice TF-IDF construído no carregamento
  (`construirIndiceBusca`/`buscarAssunto`) e resultados em `<details>` (mesmo
  padrão do FAQ).
- `pwa/sw.js`: `busca.json` adicionado ao precache.
- Testes novos: `tests/test_busca_legislacao.py` (cobertura do índice, sem
  vazar FAQ `pendente_ctrh`, guard-rail monetário) + extensão de
  `tests/test_build_pwa.py` para o novo `busca.json`. Total: 89 testes,
  todos passando.
- Verificado ponta-a-ponta com Playwright headless (script ad-hoc, não
  commitado): busca por "IDERio", "tenho direito", "fator geral" (aciona o
  documento ponteiro e foca a busca por escola) e termo sem resultado —
  tudo funcionando, sem erros de console. **Não existe ainda um smoke test
  de Playwright commitado no repo** — se quiser rodar de novo, seria preciso
  escrever um novo script ou script de skill.

## O que foi feito no MVP inicial

- Estrutura completa do projeto (`src/`, `scripts/`, `pwa/`, `base/`, `docs/`, `tests/`).
- `src/dados.py`: leitura de `base/dp_sme.xlsx` (cadastro de unidades), sem
  overlay de "Fator de Premiação" (esse arquivo é específico de 2025 e não
  existe para 2026) — logo, sem distinção "turma carioca" aqui.
- `src/regras_pra_2026.py`: motor de regras explicativas da Resolução
  561/2026 — indicadores I a IX, nota por faixa de crescimento (Art. 15),
  Fator Geral (Art. 13 §6º + Art. 16 §2º), cargos por modalidade (Art. 13
  §§1º-5º), elegibilidade (Arts. 7º-8º), fórmula final (Art. 16). Inclui
  `PENDENCIAS_VERIFICACAO`: 7 ambiguidades reais do texto da norma,
  encontradas ao ler a versão comentada da Resolução e ao implementar o
  motor (ex.: Art. 16 §2º referencia o indicador errado; Fator Geral de
  unidades EF+EE/UE/BI sem Infantil/EJA não está previsto em nenhuma das
  três alíneas do Art. 13 §6º).
- `scripts/build_pwa.py`: pré-renderiza tudo em `dist/dados/*.json`, com o
  mesmo guard-rail de 2025 contra valores monetários.
- `pwa/`: app shell copiado/adaptado de 2025 — nova seção "Transparência
  sobre o texto da norma" e um explicador visual (gauge de 3 zonas) para a
  régua de nota 0–80–100%+.
- 80 testes (`pytest tests/`), todos passando. Build local validado (`dist/`
  gerado e servido via `http.server`, todos os arquivos respondendo 200).
- Legislação: `pwa/legislacao/resolucao-sme-561-2026-pra.pdf` copiada.

## Decisões tomadas

- Pasta nova (`pra-2026-pwa`, irmã de `dashboard-servidor`), repo git
  independente — ainda **não inicializado** (próximo passo).
- Escopo do MVP = explicador geral, sem parsear o PDF de Anexos (metas reais
  por escola) — isso é fase 2.
- Reaproveitado `base/dp_sme.xlsx` do projeto de 2025 como fonte cadastral
  (não é específico de um ano de PRA).

## Próximos passos

1. Deploy de teste no Netlify (site novo) — ainda não confirmado que já
   subiu com a busca por assunto.
2. Escrever um smoke test de Playwright commitado (hoje só foi validado
   manualmente, script descartado ao final da sessão).
3. Fase 2 (fora deste MVP): extrair as metas por indicador dos Anexos da
   Resolução (PDF) e mostrar a meta real de cada unidade.
4. Considerar expandir `SINONIMOS` em `src/busca_legislacao.py` conforme
   servidores reais usarem a busca (termos que não estão sendo encontrados).

## Nota

`pwa/assets/og-image.png` já foi regenerada para 2026 (`scripts/gerar_og_image_pwa.py`,
que lê `assets/logo_sme_rio.png` na raiz — copiado do projeto de 2025). Os
ícones (`pwa/icons/`) foram reaproveitados sem alteração (mesma marca visual).
