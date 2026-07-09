# Regras da PRA 2026 (referência resumida)

> Fonte: **Resolução SME nº 561, de 02/07/2026** — cópia em
> `pwa/legislacao/resolucao-sme-561-2026-pra.pdf`.
> Este documento resume as regras usadas pela PWA para **explicar** o
> cálculo da Premiação por Resultados de Aprendizagem (PRA) 2026, com
> referência aos artigos correspondentes. A PWA não exibe valores numéricos
> já calculados de premiação (R$) nem a nota/score final. As metas reais de
> cada indicador por escola (Resultado, Meta 2026, Crescimento Esperado) são
> exibidas na aba "Metas 2026" — convertidas de
> `pwa/legislacao/pra-2026-anexos-metas.pdf` (Anexos I e II) para
> `base/metas_pra_2026.csv`, lido por `src/metas_pra_2026.py`. São dados
> públicos, já publicados oficialmente.
>
> Em caso de dúvida sobre um caso específico, consulte sempre a Resolução
> SME nº 561/2026 e a CTRH da sua unidade.

## Indicadores I a IX (Art. 9º)

| Indicador | Descrição | Etapa/Modalidade |
|---|---|---|
| I | % de alunos alfabetizados (Leitura e Escrita) no 2º ano | AI |
| II | % de alunos proficientes em Matemática no 2º ano | AI |
| III | IDERio do 4º ano | AI |
| IV | IDERio do 5º ano | AI |
| V | IDERio do 8º ano | AF |
| VI | IDERio do 9º ano | AF |
| VII | Indicador de Rendimento dos Anos Iniciais (substitui III/IV quando não há Prova Rio suficiente, Art. 9º §3º) | AI |
| VIII | Indicador de Rendimento dos Anos Finais (substitui V/VI nas mesmas condições) | AF |
| IX | Taxa de execução das ações válidas do Plano das Dimensões (PD) da modalidade | EI/EJA/EE/Extensão/Biblioteca |

Conforme o **Art. 15**, a nota de cada indicador varia de 0,00 a 1,00:
abaixo de 80% do crescimento esperado = 0,00; entre 80% e 100% = nota
proporcional entre 0,80 e 1,00; acima de 100% (ou meta já alcançada, quando
não há crescimento esperado) = 1,00. A nota da unidade, por
modalidade/etapa, é a **média** das notas dos indicadores considerados
(Art. 15, §1º).

## Professor regente e cargos de modalidade (Art. 13, §§1º a 5º)

- **Anos Iniciais (1º ao 5º ano)**: nota = média dos Indicadores I, II, III
  e IV (ou VII, quando não há Prova Rio suficiente).
- **Anos Finais (6º ao 9º ano)**: nota = média dos Indicadores V e VI (ou
  VIII, nas mesmas condições).
- **Agente de Educação Infantil** (§4º): nota = Indicador IX (PD de
  Educação Infantil).
- **Professor Orientador de EJA** (§5º): nota = Indicador IX (PD de EJA).
- **Classe Especial / Sala de Recursos em unidade COM turmas de EF** (§2º):
  segue o **Fator Geral** da unidade.
- **Classe Especial / Sala de Recursos em unidade SEM turmas de EF** (§3º):
  nota = Indicador IX (PD de Educação Especial).
- **Professor que atua em mais de uma modalidade/etapa** (Art. 16, §1º):
  nota calculada de forma proporcional à fração da carga horária dedicada a
  cada uma.

## Fator Geral (cargos fora de sala de aula, Art. 13, §6º)

Aplica-se a direção, secretaria, inspeção, apoio administrativo e demais
cargos que não se enquadram nas regras específicas acima.

1. **Unidade exclusivamente de EF Regular** (alínea "a"): Fator Geral =
   média dos Indicadores I a VIII das etapas oferecidas.
2. **Unidade com EF concomitante a Infantil e/ou EJA** (alínea "b"): mesma
   média do item 1, podendo receber um acréscimo (Art. 16, §2º):
   - **+0,10** se a unidade alcançar mais de 80% em 1 Plano das Dimensões;
   - **+0,20** se alcançar em 2 Planos das Dimensões.
3. **Unidade sem turmas de EF** (alínea "c"): Fator Geral = Indicador IX.

⚠️ **Lacuna identificada**: unidades que combinam EF com Educação Especial,
Unidade de Extensão ou Biblioteca (sem Infantil/EJA) não se encaixam
claramente em nenhuma das três alíneas. A PWA sinaliza esse caso ao
servidor em vez de aplicar uma regra por conta própria.

## Elegibilidade individual (Arts. 7º e 8º)

Precisa cumprir **todos**:
- Pleno exercício na SME-RJ por pelo menos ¾ do ano letivo de 2026;
- Lotado em Unidade Escolar/Extensão/Biblioteca em 2026;
- Não ser elegível ao Acordo de Resultados (AR) — mutuamente excludente com a PRA;
- Não ter sofrido penalidade disciplinar no período de apuração;
- Não ter sido exonerado/demitido antes do pagamento;
- Não ter apresentado falta em 2026 (Art. 8º, III — sem detalhamento de
  quantidade/tipo no texto da norma).

Diretor IV tem condição extra: não pode ter tido resultado insatisfatório
na última avaliação do Programa de Avaliação Periódica de Desempenho e
Competências para Gestores (Portaria E/CTRH nº 21/2026).

## Cálculo final (Art. 16)

PRA = (Nota de premiação da modalidade/etapa) × (Fração da carga horária) ×
(13º salário bruto de 2026 — critérios de remuneração do Art. 2º)

Bônus possíveis (não cumulativos):
- +0,10/+0,20 para quem responde pelo Fator Geral de unidades mistas (ver acima);
- +0,10 para quem não responde pelo Fator Geral e foi certificado na trilha
  formativa (Circular Conjunta E/SUBE-E/CTRH nº 01/2026).

## Pendências de verificação

O texto da Resolução 561/2026 tem pontos ambíguos ou incompletos, listados
integralmente em `src/regras_pra_2026.py::PENDENCIAS_VERIFICACAO` e exibidos
na seção "Transparência sobre o texto da norma" da PWA:

1. Relação entre esta Resolução e o Decreto Rio nº 58.106/2026 não está estabelecida no texto.
2. Numeração pula do Art. 13 para o Art. 15 (falta o Art. 14).
3. Ano-base divergente: Art. 10, II usa 2025; Art. 15, §2º usa 2024, para as
   mesmas metas de alfabetização/Matemática.
4. Art. 16, §2º associa o bônus de fator geral misto ao "indicador do inciso
   VII", que na verdade é o Indicador de Rendimento dos Anos Iniciais, e não
   o Plano das Dimensões (inciso IX).
5. Fator Geral de unidades com EF + Educação Especial/Extensão/Biblioteca
   (sem Infantil/EJA) não está coberto pelas três alíneas do Art. 13, §6º.
6. Art. 8º, III ("apresentado falta em 2026") não detalha quantidade, tipo
   ou natureza cumulativa.
7. Várias remissões a circulares/portarias externas ainda não incorporadas
   ao texto da Resolução (critérios técnicos do PD, avaliação de gestores,
   trilha formativa).

## Fora de escopo deste MVP

- Metas reais por indicador/unidade (dependem dos Anexos da Resolução, em
  PDF — parsing não incluído nesta primeira versão).
- Cálculo de valores monetários (nunca será exibido — guard-rail de build).
