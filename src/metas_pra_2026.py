"""Metas reais de cada indicador por escola (Anexos I e II da Resolução SME
nº 561/2026, base/metas_pra_2026.csv).

São dados públicos, já publicados oficialmente nos Anexos da Resolução — não
são calculados por este painel nem antecipam o resultado final de 2026 (que só
existe depois do ano letivo terminar). O painel continua sem calcular valores
de premiação (R$) ou a nota final: aqui só reexibimos Resultado (ano-base),
Meta 2026 e Crescimento Esperado, exatamente como publicados.

O CSV foi gerado a partir do PDF oficial (também disponível em
`pwa/legislacao/pra-2026-anexos-metas.pdf`) com um script de conversão ad-hoc
(não versionado — o CSV é o artefato, no mesmo espírito de `base/dp_sme.xlsx`).
Célula vazia = indicador não se aplica àquela escola (foi substituído pelo
indicador irmão, ex.: III/IV viram vazios quando VII se aplica). Quando
Resultado/Meta estão preenchidos mas o Crescimento Esperado do PDF era "-", a
meta já foi atingida/superada e gravamos crescimento_esperado = 0 (validado
empiricamente: nas 424 ocorrências do PDF, Resultado sempre foi >= Meta).
"""

import pandas as pd

from src.dados import _cache
from src.regras_pra_2026 import INDICADORES

CAMINHO_PADRAO = "base/metas_pra_2026.csv"

# Prefixo de coluna no CSV -> numeral do indicador (mesma chave de INDICADORES
# em src/regras_pra_2026.py) + unidade de exibição.
#   "pp": ponto percentual (indicadores I/II, escala 0-100);
#   "pontos": escala IDERio (0-10, uma casa decimal);
#   "indice": Indicador de Rendimento (escala 0-1, duas casas decimais).
COLUNAS_INDICADOR = [
    ("alf_le", "I", "pp"),
    ("alf_mat", "II", "pp"),
    ("iderio_4", "III", "pontos"),
    ("iderio_5", "IV", "pontos"),
    ("indicador_rendimento_ai", "VII", "indice"),
    ("iderio_8", "V", "pontos"),
    ("iderio_9", "VI", "pontos"),
    ("indicador_rendimento_af", "VIII", "indice"),
]


DISCLAIMER_METAS = (
    "ℹ️ Estas são as **metas oficiais já publicadas** nos Anexos da "
    "Resolução SME nº 561/2026 — não são o resultado final de 2026 (que só "
    "existe depois do ano letivo terminar) nem o valor da premiação: este "
    "painel não calcula nenhum dos dois."
)


@_cache
def carregar_metas(path: str = CAMINHO_PADRAO) -> dict[int, list[dict]]:
    """Lê o CSV e devolve, por designação, a lista dos indicadores aplicáveis.

    Cada indicador: `indicador` (numeral I-VIII), `resultado`, `meta_2026`,
    `crescimento_esperado` (floats). Descrição e unidade de exibição de cada
    indicador não variam por escola — ver `descricoes_indicadores()`.
    """
    df = pd.read_csv(path)

    metas: dict[int, list[dict]] = {}
    for _, linha in df.iterrows():
        designacao = int(linha["designacao"])
        indicadores = []
        for prefixo, numeral, _unidade in COLUNAS_INDICADOR:
            resultado = linha[f"{prefixo}_resultado"]
            meta = linha[f"{prefixo}_meta_2026"]
            if pd.isna(resultado) or pd.isna(meta):
                continue  # indicador não se aplica a esta escola
            crescimento = linha[f"{prefixo}_crescimento_esperado"]
            indicadores.append(
                {
                    "indicador": numeral,
                    "resultado": float(resultado),
                    "meta_2026": float(meta),
                    "crescimento_esperado": float(crescimento) if not pd.isna(crescimento) else 0.0,
                }
            )
        if indicadores:
            metas[designacao] = indicadores
    return metas


def descricoes_indicadores() -> dict[str, dict]:
    """Descrição e unidade de exibição de cada indicador com meta (I-VIII),
    para exibição na PWA sem repetir esse texto por escola."""
    return {
        numeral: {"descricao": INDICADORES[numeral]["descricao"], "unidade": unidade}
        for _prefixo, numeral, unidade in COLUNAS_INDICADOR
    }
