"""Carregamento da tabela de tipos de afastamento (base/Ausencias.xlsx).

Referência operacional (códigos de movimento do sistema de RH/ponto) sobre
quais tipos de afastamento contam como dia não trabalhado ("ausência",
afeta o critério de tempo mínimo de efetivo exercício) e quais contam como
falta.

NÃO é um artigo da Resolução SME nº 561/2026 — é conhecimento operacional.
O Art. 8º, III da Resolução 561/2026 apenas diz que o servidor perde o
direito à PRA se tiver "apresentado falta no ano de 2026", sem detalhar
quantidade, tipo ou natureza cumulativa (ver pendência de verificação em
`docs/REGRAS_PRA_2026.md`). Em caso de dúvida sobre um código específico, o
servidor deve confirmar com a CTRH da sua CRE. O arquivo não contém dados
pessoais de servidores — é só uma tabela de referência dos tipos de movimento.
"""

import pandas as pd

from src.dados import _cache

CAMINHO_PADRAO = "base/Ausencias.xlsx"

NOMES_COLUNAS = [
    "_col_a",
    "cod",
    "descricao",
    "conta_como_ausencia",
    "falta_nao_justificada",
    "prioridade",
    "cod_mov",
    "art_64",
    "observacoes",
]

INTRO_AUSENCIAS = (
    "Cada tipo de afastamento tem um código no sistema de ponto/RH. A "
    "Resolução SME nº 561/2026 (Art. 8º, III) diz apenas que **ter "
    "apresentado falta em 2026** tira o direito à PRA, sem detalhar "
    "quantidade ou tipo — por isso, use esta tabela apenas como referência "
    "operacional, e confirme seu caso específico com a CTRH da sua CRE."
)


def _para_bool(valor) -> bool:
    return str(valor).strip().upper() == "SIM"


@_cache
def carregar_ausencias(path: str = CAMINHO_PADRAO) -> list[dict]:
    """Lê a aba única do Ausencias.xlsx e devolve uma lista de registros.

    Cada registro: cod (str, com zeros à esquerda quando aplicável),
    descricao, conta_como_ausencia (bool), falta_nao_justificada (bool),
    observacoes (str ou None).
    """
    df = pd.read_excel(path, sheet_name="Planilha1", header=1)
    df.columns = NOMES_COLUNAS[: len(df.columns)]
    df = df[df["cod"].notna()]

    registros = []
    for _, linha in df.iterrows():
        observacoes = linha["observacoes"]
        registros.append(
            {
                "cod": f"{int(linha['cod']):03d}",
                "descricao": str(linha["descricao"]).strip(),
                "conta_como_ausencia": _para_bool(linha["conta_como_ausencia"]),
                "falta_nao_justificada": _para_bool(linha["falta_nao_justificada"]),
                "observacoes": None if pd.isna(observacoes) else str(observacoes).strip(),
            }
        )
    return registros
