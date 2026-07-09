"""Motor de regras explicativas da PRA 2026 (Resolução SME nº 561/2026).

Este módulo NÃO calcula valores numéricos de premiação, nem reproduz as
metas reais de cada unidade (elas estão nos Anexos da Resolução, fora do
escopo deste painel). Ele explica, em linguagem simples, como a metodologia
funciona para o cargo e a unidade do servidor: quais indicadores contam,
como a nota de 0 a 1 é calculada a partir do crescimento esperado, e quais
critérios de elegibilidade se aplicam.

Onde o texto da Resolução tem lacunas ou ambiguidades, este módulo expõe
isso explicitamente (`PENDENCIAS_VERIFICACAO`) em vez de tentar adivinhar
uma regra que a norma não deixa clara.
"""

import pandas as pd

REFERENCIA = "Resolução SME nº 561/2026 (PRA 2026)."

# Glossário de siglas usadas nos textos explicativos, para consulta pelo servidor.
GLOSSARIO = {
    "PRA": "Premiação por Resultados de Aprendizagem — o prêmio que este painel explica.",
    "AR": "Acordo de Resultados — outro tipo de premiação da Prefeitura, de outros órgãos. Ninguém recebe PRA e AR ao mesmo tempo.",
    "CRE": "Coordenadoria Regional de Educação — a regional da SME responsável pela sua escola.",
    "CTRH": "Comissão Técnica de Recursos Humanos — setor de RH da sua CRE, que pode esclarecer casos específicos.",
    "PD": "Plano das Dimensões — plano de ação usado pelas modalidades sem prova padronizada (Infantil, EJA, Educação Especial exclusiva, Extensão, Bibliotecas).",
    "IDERio": "Índice de Desenvolvimento da Educação do Rio — combina o Indicador de Rendimento (P) e a Nota Padronizada (N) da prova.",
    "Indicador de Rendimento (P)": "Mede aprovação/fluxo dos alunos — um dos dois insumos do IDERio.",
    "Nota padronizada (N)": "Nota de desempenho na prova (Prova Rio) — o outro insumo do IDERio.",
    "CAEd": "Centro de Políticas Públicas e Avaliação da Educação — aplica a Prova Rio e publica os resultados.",
    "ICG": "Índice de Complexidade da Gestão — usado como critério de desempate entre Planos das Dimensões.",
    "Avalia RJ": "Avaliação municipal aplicada ao 2º ano, usada para medir alfabetização e proficiência em Matemática.",
    "Prova Rio": "Avaliação municipal aplicada ao 4º, 5º, 8º e 9º ano, usada para calcular o IDERio.",
}


def glossario_markdown() -> str:
    """Markdown com a lista de siglas do glossário, para exibição em expander."""
    linhas = [f"- **{sigla}**: {definicao}" for sigla, definicao in GLOSSARIO.items()]
    return "\n".join(linhas)


# Rótulos amigáveis para cada etapa/modalidade.
ETAPA_LABELS = {
    "AI": "Anos Iniciais (1º ao 5º ano)",
    "AF": "Anos Finais (6º ao 9º ano)",
    "EI": "Educação Infantil",
    "EJA": "Educação de Jovens e Adultos (EJA)",
    "EE": "Educação Especial",
    "UE": "Unidade de Extensão",
    "BI": "Biblioteca",
}

# Ícones para exibir cada etapa/modalidade como "chip" na interface.
ETAPA_ICONS = {
    "AI": "",
    "AF": "",
    "EI": "🧸",
    "EJA": "",
    "EE": "♿",
    "UE": "🏫",
    "BI": "📚",
}

# Rótulos de exibição para "Tipo de Unidade" (apenas para mostrar ao
# servidor - a lógica interna continua usando o valor original de dp_sme.xlsx).
TIPO_UNIDADE_DISPLAY = {
    "exclusivo fund i": "Exclusivo AI",
    "exclusivo fund ii": "Exclusivo AF",
}


def formatar_tipo_unidade(tipo_unidade) -> str:
    """Converte o "Tipo de Unidade" para um rótulo mais claro ao servidor."""
    tipo_unidade = str(tipo_unidade)
    return TIPO_UNIDADE_DISPLAY.get(tipo_unidade.strip().lower(), tipo_unidade)


def formatar_cre(cre) -> str:
    """Formata a CRE como ordinal (ex.: 1 -> "1ª CRE"), evitando o "1.0" que
    aparece quando o valor vem como float da planilha."""
    try:
        numero = int(cre)
    except (TypeError, ValueError):
        return str(cre)
    return f"{numero}ª CRE"


# Indicadores I a IX da PRA 2026 (Art. 9º).
INDICADORES = {
    "I": {
        "descricao": "% de alunos alfabetizados (Leitura e Escrita) no 2º ano do Ensino Fundamental",
        "etapa": "AI",
    },
    "II": {
        "descricao": "% de alunos proficientes em Matemática no 2º ano do Ensino Fundamental",
        "etapa": "AI",
    },
    "III": {
        "descricao": "IDERio do 4º ano do Ensino Fundamental",
        "etapa": "AI",
    },
    "IV": {
        "descricao": "IDERio do 5º ano do Ensino Fundamental",
        "etapa": "AI",
    },
    "V": {
        "descricao": "IDERio do 8º ano do Ensino Fundamental",
        "etapa": "AF",
    },
    "VI": {
        "descricao": "IDERio do 9º ano do Ensino Fundamental",
        "etapa": "AF",
    },
    "VII": {
        "descricao": (
            "Indicador de Rendimento dos Anos Iniciais "
            "(substitui III/IV quando não há Prova Rio suficiente)"
        ),
        "etapa": "AI",
    },
    "VIII": {
        "descricao": (
            "Indicador de Rendimento dos Anos Finais "
            "(substitui V/VI quando não há Prova Rio suficiente)"
        ),
        "etapa": "AF",
    },
    "IX": {
        "descricao": "Taxa de execução das ações válidas do Plano das Dimensões (PD) de cada modalidade ofertada",
        "etapa": "PD",
    },
}

# Pendências de verificação identificadas no texto da Resolução 561/2026 —
# ambiguidades que este painel não tenta resolver por conta própria.
PENDENCIAS_VERIFICACAO = [
    {
        "titulo": "Base legal e Decreto Rio nº 58.106/2026",
        "texto": (
            "Esta Resolução tem base legal própria — o Decreto nº 50.863/2022, "
            "alterado pelo nº 55.182/2024 — e não o Decreto Rio nº 58.106/2026 "
            "(que trata de Acordos de Resultados de outros órgãos, como SMDU, "
            "IPLANRIO, GEO-RIO etc.). São dois sistemas de gratificação com "
            "fundamentos legais distintos; o texto não estabelece um dispositivo "
            "que os conecte diretamente."
        ),
    },
    {
        "titulo": "Numeração: falta o Art. 14",
        "texto": (
            "A numeração pula do Art. 13 direto para o Art. 15. Pode ser uma "
            "lacuna da cópia usada nesta análise, ou o artigo pode ter sido "
            "suprimido na publicação oficial. Confirme no Diário Oficial antes "
            "de tratar este material como referência completa."
        ),
    },
    {
        "titulo": "Ano-base divergente para as metas de alfabetização/Matemática",
        "texto": (
            "O Art. 10, II usa o resultado de 2025 (Avalia RJ) como base de "
            "cálculo da meta 2026 de alfabetização e Matemática do 2º ano. Já "
            "o Art. 15, §2º, usa o resultado de 2024 como base do 'crescimento "
            "esperado' desses mesmos indicadores. Essa divergência de ano-base "
            "pode ser um erro de redação — não foi assumida uma correção neste painel."
        ),
    },
    {
        "titulo": "Bônus do fator geral (Art. 16, §2º) cita o indicador errado?",
        "texto": (
            "O Art. 16, §2º concede um bônus (+0,10 ou +0,20) a quem responde "
            "pelo fator geral de unidades mistas (EF + Infantil/EJA), condicionado "
            "a 'alcançar mais de 80% no indicador do inciso VII do art. 9º em "
            "Planos das Dimensões'. Mas o inciso VII do Art. 9º é o Indicador de "
            "Rendimento dos Anos Iniciais — não tem relação direta com Plano das "
            "Dimensões (que é o inciso IX). Pode ser um erro de referência no "
            "texto publicado. Este painel descreve a regra como está escrita e "
            "sinaliza a inconsistência, sem tentar adivinhar a intenção da norma."
        ),
    },
    {
        "titulo": "Falta em 2026 (Art. 8º, III) sem detalhamento",
        "texto": (
            "O Art. 8º, III fala apenas em 'ter apresentado falta no ano de "
            "2026', sem definir quantidade, tipo (justificada ou não) ou se é "
            "cumulativo. O texto não deixa claro se uma única falta abonada já "
            "tira o direito à gratificação."
        ),
    },
    {
        "titulo": "Fator Geral de unidades com EF + Educação Especial/Extensão/Biblioteca",
        "texto": (
            "O Art. 13, §6º define três situações para o Fator Geral: (a) "
            "unidades exclusivamente de EF Regular, (b) unidades com EF "
            "concomitante a Infantil e/ou EJA, e (c) unidades sem EF. Uma "
            "unidade que combine EF com Educação Especial, Unidade de "
            "Extensão ou Biblioteca (sem Infantil/EJA) não se encaixa "
            "claramente em nenhuma das três — este painel sinaliza esse caso "
            "em vez de aplicar por conta própria a regra da alínea 'a' ou 'b'."
        ),
    },
    {
        "titulo": "Circulares e portarias ainda não incorporadas",
        "texto": (
            "Vários critérios técnicos remetem a documentos externos que não "
            "fazem parte do texto da Resolução: as Circulares Conjuntas "
            "E/SUBAIR-E/SUBE-E/CTRH nº 01 (25/02/2026) e nº 02 (01/04/2026) — "
            "critérios técnicos do Plano das Dimensões; a Portaria E/CTRH nº 21 "
            "(16/04/2026) — avaliação de gestores; e a Circular Conjunta "
            "E/SUBE-E/CTRH nº 01/2026 (30/04/2026) — trilha formativa."
        ),
    },
]


def pendencias_verificacao_markdown() -> str:
    """Markdown com a lista de pendências de verificação, para a seção de
    transparência da PWA."""
    partes = []
    for item in PENDENCIAS_VERIFICACAO:
        partes.append(f"**{item['titulo']}**\n\n{item['texto']}")
    return "\n\n---\n\n".join(partes)


def explicar_nota_indicador() -> str:
    """Markdown explicando como a nota de 0 a 1 de cada indicador é
    calculada a partir do crescimento esperado (Art. 15)."""
    return (
        "Cada indicador (I a IX) recebe uma **nota de 0,00 a 1,00**, que não "
        "depende do valor absoluto — depende de **quanto a escola cresceu em "
        "relação à meta esperada para 2026**:\n\n"
        "| Faixa de atingimento da meta | Nota |\n"
        "|---|---|\n"
        "| Abaixo de 80% do crescimento esperado | 0,00 |\n"
        "| Entre 80% e 100% do crescimento esperado | proporcional, entre 0,80 e 1,00 |\n"
        "| 100% ou mais (ou meta já alcançada, quando não há crescimento esperado) | 1,00 |\n\n"
        "A nota final da unidade, por modalidade/etapa, é a **média das notas "
        "dos indicadores considerados**.\n\n"
        "⚠️ Este painel não mostra a meta real da sua escola nem o resultado "
        "já apurado — apenas como a régua de 0 a 1 funciona. As metas de cada "
        "unidade estão nos Anexos da Resolução."
    )


def classificar_fator_geral(unidade: pd.Series) -> dict:
    """Classifica a unidade para fins de Fator Geral (Art. 13, §6º).

    Retorna um dicionário com:
    - "tipo": "EF" (só Ensino Fundamental Regular), "PD" (só modalidade(s)
      de PD, sem EF), "MISTA" (EF + Infantil e/ou EJA), "INDEFINIDO".
    - "etapas_ef": lista com as etapas de EF presentes ("AI" e/ou "AF").
    - "modalidades_pd": lista de modalidades de PD presentes na unidade.
    - "modalidades_bonus": subconjunto de modalidades_pd que conta para o
      bônus do Art. 16, §2º (apenas Educação Infantil e EJA).
    """
    etapas_ef = [etapa for etapa in ("AI", "AF") if unidade.get(f"tem_{etapa}")]
    modalidades_pd = list(unidade.get("modalidades_pd", []))
    modalidades_bonus = [m for m in modalidades_pd if m in ("EI", "EJA")]

    if etapas_ef and not modalidades_pd:
        tipo = "EF"
    elif modalidades_pd and not etapas_ef:
        tipo = "PD"
    elif etapas_ef and modalidades_pd:
        tipo = "MISTA"
    else:
        tipo = "INDEFINIDO"

    return {
        "tipo": tipo,
        "etapas_ef": etapas_ef,
        "modalidades_pd": modalidades_pd,
        "modalidades_bonus": modalidades_bonus,
    }


def _indicadores_ef(etapas_ef: list[str]) -> str:
    """Markdown listando os indicadores (I a VIII) aplicáveis às etapas de
    EF informadas."""
    partes = []
    if "AI" in etapas_ef:
        partes.append(
            "- **Anos Iniciais**: indicadores I (alfabetização, 2º ano), II "
            "(Matemática, 2º ano), III (IDERio do 4º ano), IV (IDERio do 5º "
            "ano) — ou VII (Indicador de Rendimento) quando não há Prova Rio "
            "suficiente no 4º/5º ano."
        )
    if "AF" in etapas_ef:
        partes.append(
            "- **Anos Finais**: indicadores V (IDERio do 8º ano) e VI (IDERio "
            "do 9º ano) — ou VIII (Indicador de Rendimento) quando não há "
            "Prova Rio suficiente no 8º/9º ano."
        )
    return "\n".join(partes)


def explicar_fator_geral(unidade: pd.Series) -> str:
    """Markdown explicando o cálculo do Fator Geral para a unidade informada
    (Art. 13, §6º e Art. 16, §2º)."""
    classificacao = classificar_fator_geral(unidade)
    tipo = classificacao["tipo"]
    etapas_ef = classificacao["etapas_ef"]
    modalidades_pd = classificacao["modalidades_pd"]
    modalidades_bonus = classificacao["modalidades_bonus"]

    texto = (
        "## Fator Geral\n\n"
        "O **Fator Geral** é a regra que vale para os servidores que não são "
        "professor regente, Agente de Educação Infantil, Orientador de EJA "
        "nem professor de Classe Especial/Sala de Recursos (esses têm regra "
        "própria — veja a aba \"Meu caso\"). Ele descreve como a nota da "
        "unidade é formada a partir do perfil educacional da escola.\n\n"
    )

    if tipo == "EF":
        texto += (
            "Como esta unidade é **exclusivamente de Ensino Fundamental "
            "Regular**, sua nota de Fator Geral é a **média dos indicadores "
            "I a VIII** aplicáveis às etapas que a unidade oferece:\n\n"
            f"{_indicadores_ef(etapas_ef)}\n\n"
        )

    elif tipo == "PD":
        modalidades_fmt = ", ".join(ETAPA_LABELS[m] for m in modalidades_pd)
        texto += (
            "Como esta unidade **não tem turmas de Ensino Fundamental**, seu "
            f"Fator Geral segue apenas o **indicador IX** — a taxa de execução "
            f"das ações válidas do Plano das Dimensões (PD) da(s) "
            f"modalidade(s): **{modalidades_fmt}**.\n\n"
        )

    elif tipo == "MISTA":
        texto += (
            "Esta unidade combina **Ensino Fundamental** com outra(s) "
            f"modalidade(s) de Plano das Dimensões. A nota-base do Fator "
            f"Geral é a **média dos indicadores I a VIII** das etapas de "
            f"EF:\n\n"
            f"{_indicadores_ef(etapas_ef)}\n\n"
        )
        if modalidades_bonus:
            modalidades_bonus_fmt = ", ".join(ETAPA_LABELS[m] for m in modalidades_bonus)
            texto += (
                "Além disso, o Art. 16, §2º prevê um **acréscimo (bônus)** na "
                f"nota para unidades com EF concomitante a Infantil e/ou EJA "
                f"— o caso desta unidade, na(s) modalidade(s): "
                f"**{modalidades_bonus_fmt}**:\n\n"
                "- **+0,10** se a unidade alcançar mais de 80% em **1** Plano das Dimensões\n"
                "- **+0,20** se alcançar em **2** Planos das Dimensões\n\n"
                "⚠️ O texto do Art. 16, §2º associa esse bônus ao \"indicador do "
                "inciso VII do art. 9º\", mas o inciso VII trata do Indicador de "
                "Rendimento dos Anos Iniciais, não do Plano das Dimensões (que é "
                "o inciso IX). Este painel descreve a regra como publicada, sem "
                "tentar corrigir a referência.\n\n"
            )
        else:
            modalidades_fmt = ", ".join(ETAPA_LABELS[m] for m in modalidades_pd)
            texto += (
                f"⚠️ Esta unidade combina Ensino Fundamental com **"
                f"{modalidades_fmt}** — não com Educação Infantil nem EJA. O "
                "Art. 13, §6º só define regra explícita para unidades "
                "exclusivamente de EF (alínea 'a'), unidades com EF "
                "concomitante a Infantil e/ou EJA (alínea 'b'), e unidades "
                "sem EF (alínea 'c'). Este caso específico não está coberto "
                "por nenhuma das três alíneas.\n\n"
            )

    else:
        texto += (
            "⚠️ Não foi possível identificar etapas de Ensino Fundamental "
            "nem modalidades de Plano das Dimensões para esta unidade.\n\n"
        )

    texto += f"_Referência: {REFERENCIA}_"
    return texto


def explicar_professor(unidade: pd.Series, etapa: str) -> str:
    """Markdown explicando o cálculo da nota para o cargo/etapa informado
    (Art. 13, §§1º a 5º)."""
    tipo_unidade = str(unidade.get("tipo_unidade", "")).strip().lower()
    tem_ef = bool(unidade.get("tem_AI")) or bool(unidade.get("tem_AF"))

    if etapa == "AI":
        texto = (
            "## Professor regente - Anos Iniciais\n\n"
            "Sua nota de PRA reflete o desempenho da sua etapa (Art. 13, §1º): "
            "alfabetização e Matemática no 2º ano, e o IDERio (ou Indicador de "
            "Rendimento) do 4º e 5º ano.\n\n"
            "Os componentes são:\n\n"
            "- **Indicador I**: % de alunos alfabetizados no 2º ano\n"
            "- **Indicador II**: % de alunos proficientes em Matemática no 2º ano\n"
            "- **Indicador III**: IDERio do 4º ano (ou **VII**, Indicador de "
            "Rendimento, quando não há Prova Rio suficiente)\n"
            "- **Indicador IV**: IDERio do 5º ano (ou **VII**, nas mesmas condições)\n\n"
            "**Elegibilidade individual:** aplica-se a servidores lotados como "
            "professor regente de turma regular de Anos Iniciais. Caso "
            "contrário, sua nota segue o Fator Geral da unidade.\n\n"
        )

    elif etapa == "AF":
        texto = (
            "## Professor regente - Anos Finais\n\n"
            "Sua nota de PRA reflete o IDERio (ou Indicador de Rendimento) do "
            "8º e 9º ano (Art. 13, §1º).\n\n"
            "Os componentes são:\n\n"
            "- **Indicador V**: IDERio do 8º ano (ou **VIII**, Indicador de "
            "Rendimento, quando não há Prova Rio suficiente)\n"
            "- **Indicador VI**: IDERio do 9º ano (ou **VIII**, nas mesmas condições)\n\n"
            "**Elegibilidade individual:** aplica-se a servidores lotados como "
            "professor regente de turma regular de Anos Finais. Caso "
            "contrário, sua nota segue o Fator Geral da unidade.\n\n"
        )

    elif etapa == "EI":
        texto = (
            "## Agente de Educação Infantil\n\n"
            "Sua nota de PRA corresponde ao **Plano das Dimensões (PD) de "
            "Educação Infantil** desta unidade (Art. 13, §4º).\n\n"
            "O componente é:\n\n"
            "- **Indicador IX**: taxa de execução das ações válidas do PD de "
            "Educação Infantil\n\n"
            "**Elegibilidade individual:** aplica-se a Agentes de Educação "
            "Infantil lotados na unidade.\n\n"
        )

    elif etapa == "EJA":
        texto = (
            "## Professor Orientador de EJA\n\n"
            "Sua nota de PRA corresponde ao **Plano das Dimensões (PD) de "
            "EJA** desta unidade (Art. 13, §5º).\n\n"
            "O componente é:\n\n"
            "- **Indicador IX**: taxa de execução das ações válidas do PD de EJA\n\n"
            "**Elegibilidade individual:** aplica-se a Professores "
            "Orientadores de EJA lotados na unidade.\n\n"
        )

    elif etapa == "EE_CE_SRM":
        if tem_ef:
            texto = (
                "## Professor de Classe Especial / Sala de Recursos\n\n"
                "Como esta unidade **tem turmas de Ensino Fundamental**, sua "
                "nota de PRA segue o **Fator Geral da unidade** (Art. 13, §2º) "
                "— não um PD específico de Educação Especial.\n\n"
                "Selecione a opção \"Fora de sala de aula (Fator Geral)\" para "
                "ver como isso é calculado nesta unidade.\n\n"
                "**Elegibilidade individual:** aplica-se a professores de "
                "Classe Especial e Sala de Recursos em unidades com turmas de "
                "Ensino Fundamental.\n\n"
            )
        else:
            texto = (
                "## Professor de Classe Especial / Sala de Recursos\n\n"
                "Como esta unidade **não tem turmas de Ensino Fundamental**, "
                "sua nota de PRA corresponde ao **Plano das Dimensões (PD) de "
                "Educação Especial** desta unidade (Art. 13, §3º).\n\n"
                "O componente é:\n\n"
                "- **Indicador IX**: taxa de execução das ações válidas do PD "
                "de Educação Especial\n\n"
                "**Elegibilidade individual:** aplica-se a professores de "
                "Classe Especial e Sala de Recursos em unidades sem turmas de "
                "Ensino Fundamental.\n\n"
            )

    else:
        texto = (
            "## Cargo não reconhecido\n\n"
            "Não há regra específica cadastrada para esta etapa/cargo. "
            f"Consulte a {REFERENCIA}\n\n"
        )

    texto += f"_Referência: {REFERENCIA}_"
    return texto


def cargos_disponiveis(unidade: pd.Series) -> list[tuple[str, str]]:
    """Lista de opções (código, rótulo) de cargos "por etapa/modalidade"
    disponíveis na unidade, sempre incluindo a opção de Fator Geral ao final.
    """
    opcoes: list[tuple[str, str]] = []

    if unidade.get("tem_AI"):
        opcoes.append(("AI", f"Professor regente - {ETAPA_LABELS['AI']}"))
    if unidade.get("tem_AF"):
        opcoes.append(("AF", f"Professor regente - {ETAPA_LABELS['AF']}"))
    if unidade.get("tem_EI"):
        opcoes.append(("EI", "Agente de Educação Infantil"))
    if unidade.get("tem_EJA"):
        opcoes.append(("EJA", "Professor Orientador de EJA"))
    if unidade.get("tem_EE"):
        opcoes.append(("EE_CE_SRM", "Professor de Classe Especial / Sala de Recursos"))

    opcoes.append(("GERAL", "Fora de sala de aula (Fator Geral)"))
    return opcoes


def explicar_elegibilidade() -> str:
    """Markdown com o checklist de elegibilidade individual (Arts. 7º e 8º),
    em forma de pergunta direta ao servidor."""
    return (
        "A PRA só é devida se você atender a **todos** os critérios abaixo, "
        "referentes ao ano letivo de 2026:\n\n"
        "- ✅ Você esteve em **pleno exercício** na SME-RJ por pelo menos "
        "**¾ (três quartos)** do ano letivo de 2026?\n"
        "- ✅ Você esteve **lotado** em Unidade Escolar, Unidade de Extensão "
        "e/ou Biblioteca Escolar em 2026?\n"
        "- ❌ Você é elegível à gratificação do **Acordo de Resultados (AR)**?\n"
        "- ❌ Você sofreu **penalidade disciplinar** durante o período de apuração?\n"
        "- ❌ Você foi **exonerado com perda do vínculo ou demitido** antes da "
        "data de pagamento da gratificação?\n"
        "- ❌ Você **apresentou falta** em 2026? *(o texto da norma não detalha "
        "quantidade/tipo)*\n\n"
        "As marcadas com ✅ precisam ser \"sim\"; as marcadas com ❌ precisam "
        "ser \"não\".\n\n"
        "**Se você foi Diretor IV em algum momento de 2026:** há uma condição "
        "extra — não pode ter tido resultado insatisfatório na última "
        "avaliação do Programa de Avaliação Periódica de Desempenho e "
        "Competências para Gestores das Unidades Escolares.\n\n"
        f"_Referência: {REFERENCIA}_"
    )


def explicar_formula_final() -> str:
    """Markdown com o cálculo final do valor da gratificação (Art. 16)."""
    return (
        "#### Como o valor final é calculado (Art. 16)\n\n"
        "PRA = (Nota de premiação da modalidade/etapa) × (Fração da carga "
        "horária na etapa) × (Critérios de remuneração)\n\n"
        "ℹ️ Se você atuou em **mais de uma modalidade/etapa** ao mesmo tempo, "
        "a fração de carga horária de cada uma leva em conta a proporção da "
        "sua distribuição de carga horária entre elas.\n\n"
        "**Bônus possíveis** (não se acumulam — cada servidor se enquadra em "
        "no máximo um deles):\n\n"
        "- **+0,10 ou +0,20** para quem responde pelo **Fator Geral** de "
        "unidades mistas (EF + Infantil/EJA) — ver aba \"Fora de sala de "
        "aula\".\n"
        "- **+0,10** para quem **não** responde pelo Fator Geral e foi "
        "certificado nos cursos escolhidos da própria trilha formativa "
        "(conforme Circular Conjunta E/SUBE-E/CTRH nº 01/2026)."
    )
