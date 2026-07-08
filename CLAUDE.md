# 🧠 PROJECT BRAIN
> Lido automaticamente no início de cada sessão. Manter abaixo de 200 linhas / 5k tokens.

---

## 📌 Projeto
- **Nome:** pra-2026-pwa
- **Objetivo:** PWA (instalável, offline-first) publicada no Netlify onde o servidor busca sua unidade e entende, em linguagem simples, como funciona sua Premiação por Resultados de Aprendizagem (PRA) 2026 — quais indicadores contam para o seu cargo, como a nota de 0 a 1 é calculada a partir do crescimento esperado, e se tem direito. NÃO exibe valores numéricos calculados de premiação nem as metas reais de cada indicador por escola (essas estão nos Anexos da Resolução, fora do escopo deste MVP).
- **Projeto irmão:** `dashboard-servidor` (painel Streamlit + PWA da PRA 2025, pasta separada). Este projeto é independente — nenhum arquivo de lá é referenciado ou modificado a partir daqui.
- **Status atual:** MVP implementado — motor de regras em `src/`, build estático em `scripts/build_pwa.py`, PWA em `pwa/`, 80 testes passando.

## 🛠️ Stack Tecnológica
- **Build:** Python 3.13 (pandas, openpyxl, markdown) — só gera os dados/HTML em tempo de build, não roda em produção.
- **Frontend:** PWA vanilla JS (sem framework), service worker com cache-busting por hash.
- **Hospedagem:** Netlify (`netlify.toml` roda o build Python e publica `dist/`).

## 📂 Estrutura de Arquivos Importantes
```
/
├── netlify.toml                → build command (scripts/build_pwa.py) + headers no-cache
├── requirements-build.txt      → pandas, openpyxl, markdown (dependências do build no Netlify)
├── scripts/
│   └── build_pwa.py            → pré-renderiza HTML/JSON estático a partir do motor Python
├── src/
│   ├── dados.py                → carregar_unidades/buscar_unidades (decodifica bits de base/dp_sme.xlsx)
│   ├── regras_pra_2026.py      → motor de regras explicativas da PRA 2026 (não calcula valores)
│   ├── ausencias.py            → tabela operacional de tipos de afastamento (base/Ausencias.xlsx)
│   ├── faq.py                  → perguntas frequentes (com status documentado/operacional/pendente_ctrh)
│   └── textos_ui.py            → textos fixos de interface, fonte única para o build
├── pwa/                        → app shell (index.html, css/, js/app.js, sw.js, manifest, icons/, assets/)
│   └── legislacao/
│       └── resolucao-sme-561-2026-pra.pdf
├── base/                       → dados de entrada
│   ├── dp_sme.xlsx             → cadastro de unidades (CRE, denominação, etapas/modalidades) — não é específico de um ano de PRA
│   └── Ausencias.xlsx          → tabela operacional de afastamentos (sem dados pessoais)
├── docs/
│   ├── REGRAS_PRA_2026.md      → referência resumida das regras da PRA 2026
│   └── SESSION_HANDOFF.md
└── tests/                      → pytest (regras + paridade PWA/Python)
```

## 🔑 Conceitos-chave
- Colunas `Tipo_Metas`/`Fatores` em DeParaUnidades2: string de 7 bits, ordem fixa **AI, AF, EI, EJA, EE, UE(Extensão), BI(Biblioteca)**.
- Diferente do painel de 2025, **não há overlay** com um arquivo de "Fator de Premiação" — os bits vêm direto de `dp_sme.xlsx`. Isso significa que não há distinção "turma carioca" aqui (a Resolução 561/2026 não menciona esse conceito no texto analisado).
- Indicadores I a IX (Art. 9º da Resolução 561/2026): alfabetização/Matemática do 2º ano, IDERio do 4º/5º/8º/9º ano, Indicador de Rendimento (substitui IDERio quando não há Prova Rio suficiente), e execução do Plano das Dimensões (PD).
- Nota de cada indicador (Art. 15): 0,00 abaixo de 80% do crescimento esperado; proporcional entre 80–100%; 1,00 acima de 100%. Nota da unidade = média das notas dos indicadores considerados.
- Fator Geral (Art. 13, §6º): três alíneas — (a) só EF, (b) EF + Infantil/EJA (com bônus do Art. 16 §2º), (c) sem EF. **Unidades que misturam EF com EE/UE/BI (sem Infantil/EJA) não se encaixam em nenhuma alínea** — sinalizado como pendência de verificação, não "resolvido" por conta própria.
- `PENDENCIAS_VERIFICACAO` em `src/regras_pra_2026.py`: lista de ambiguidades reais do texto da Resolução (Art. 14 ausente, ano-base divergente, referência trocada no Art. 16 §2º, etc.) exibidas na seção "Transparência" da PWA — nunca "corrigidas" silenciosamente pelo código.
- Regras completas em `docs/REGRAS_PRA_2026.md` (fonte: Resolução SME nº 561/2026).

## 🎯 Convenções de Código
- **Nomenclatura:** snake_case para Python
- **Encoding:** UTF-8 sempre
- **Commits:** feat/fix/docs + descrição em PT-BR
- **Testes:** pytest — rodar antes de qualquer commit

## ⚙️ Comandos Essenciais
```bash
pip install -r requirements.txt        # instalar dependências (inclui pytest)
python scripts/build_pwa.py --saida dist   # gerar a PWA estática em dist/
python -m http.server 8000 --directory dist  # servir localmente para testar
pytest tests/                          # rodar testes
```

## 🐛 Bugs Conhecidos
- Nenhum registrado até o momento.

## 🚫 Restrições Importantes
- NÃO modificar arquivos do projeto irmão `dashboard-servidor` a partir daqui.
- NÃO exibir valores numéricos calculados de premiação, nem metas reais de indicador por escola (guard-rail testado em `scripts/build_pwa.py::_verificar_sem_valores_monetarios`).
- NÃO "corrigir" silenciosamente ambiguidades do texto da Resolução — sinalizar em `PENDENCIAS_VERIFICACAO` e na seção de Transparência da PWA.
- SEMPRE confirmar antes de: expor dados pessoais de servidores (atenção à LGPD) ou alterar a interpretação de um artigo sem checar o Diário Oficial.

## 📋 Compact Instructions
> O Claude usa estas instruções ao executar /compact

Ao compactar, preservar obrigatoriamente:
- Objetivo da tarefa atual
- Arquivos modificados nesta sessão
- Próximos passos definidos
- Decisões arquiteturais tomadas
- Erros encontrados e como foram resolvidos

---
## 🔄 Continuidade de Sessão
**Ao iniciar qualquer sessão:**
1. Leia este CLAUDE.md
2. Leia docs/SESSION_HANDOFF.md
3. Confirme o estado atual antes de começar qualquer tarefa

**Ao encerrar qualquer sessão:**
1. Atualize docs/SESSION_HANDOFF.md com: status das tarefas, arquivos modificados, próximos passos e decisões tomadas.
