# Session Handoff

## Status (2026-07-08)

Projeto criado do zero, como irmão de `dashboard-servidor` (PRA 2025), sem
alterar nada lá. MVP completo: explicador geral das regras da PRA 2026
(Resolução SME nº 561/2026), sem números calculados nem metas reais por
escola (fase 2, ver "Próximos passos").

## O que foi feito

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

1. `git init` + primeiro commit (aguardando autorização do usuário para
   push/remote).
2. Testar visualmente no navegador (Playwright smoke test não foi
   escrito ainda — `tests/test_pwa_smoke.py` de 2025 pode servir de
   referência).
3. Deploy de teste no Netlify (site novo).
4. Fase 2 (fora deste MVP): extrair as metas por indicador dos Anexos da
   Resolução (PDF) e mostrar a meta real de cada unidade.

## Nota

`pwa/assets/og-image.png` já foi regenerada para 2026 (`scripts/gerar_og_image_pwa.py`,
que lê `assets/logo_sme_rio.png` na raiz — copiado do projeto de 2025). Os
ícones (`pwa/icons/`) foram reaproveitados sem alteração (mesma marca visual).
