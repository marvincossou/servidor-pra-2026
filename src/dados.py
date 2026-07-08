"""Carregamento e busca de unidades escolares (base/dp_sme.xlsx).

Esta base é cadastral (CRE, denominação, etapas/modalidades oferecidas) e não
é específica de um ano de PRA. Diferente do painel de 2025, este projeto não
sobrepõe os bits de etapa com um arquivo de "Fator de Premiação" — a Resolução
SME nº 561/2026 não define fator por etapa da mesma forma, e o objetivo deste
MVP é explicar a metodologia (quais indicadores contam, como a nota funciona),
não reproduzir com exatidão o enquadramento fino de cada unidade.
"""

import re
import unicodedata

import pandas as pd

try:
    import streamlit as st

    _cache = st.cache_data
except ModuleNotFoundError:
    # Permite importar este módulo fora do Streamlit (ex.: script de build
    # da PWA), sem instalar o pacote inteiro. O cache vira um no-op.
    def _cache(func):
        return func


CAMINHO_PADRAO = "base/dp_sme.xlsx"
ABA = "DeParaUnidades2"

# Ordem dos bits nas colunas Tipo_Metas / Fatores (confirmada empiricamente).
ETAPAS_BITS = ["AI", "AF", "EI", "EJA", "EE", "UE", "BI"]

# Modalidades que podem ter Plano das Dimensões (PD).
MODALIDADES_PD = ["EI", "EJA", "EE", "UE", "BI"]

# Nomes de colunas após leitura com header=1 (linha 2 da planilha).
# A coluna 0 (A) está sempre vazia na planilha original.
NOMES_COLUNAS = [
    "_col_a",
    "designacao",
    "designacao_antiga",
    "mudanca_designacao",
    "codigo_inep",
    "cre",
    "denominacao",
    "sigla",
    "tipo_setor",
    "universo_meta",
    "tipo_unidade",
    "tipo_unidade_2",
    "tipo_metas",
    "fatores",
    "observacoes",
]


def _normalizar(texto) -> str:
    """Remove acentos e normaliza para minúsculas, para busca/comparação."""
    texto = str(texto)
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto.lower().strip()


@_cache
def carregar_unidades(path: str = CAMINHO_PADRAO) -> pd.DataFrame:
    """Lê a aba DeParaUnidades2 e devolve um DataFrame normalizado.

    - Remove o registro "Nível Central / Sede CRE" (linha administrativa).
    - Remove linhas sem designação numérica.
    - Decodifica as colunas Tipo_Metas/Fatores em flags booleanas por etapa.
    """
    df = pd.read_excel(path, sheet_name=ABA, header=1)
    df.columns = NOMES_COLUNAS[: len(df.columns)]

    df = df[df["tipo_unidade"].apply(_normalizar) != "nivel central / sede cre"]

    designacao_numerica = pd.to_numeric(df["designacao"], errors="coerce")
    df = df[designacao_numerica.notna()].copy()
    df["designacao"] = designacao_numerica[designacao_numerica.notna()].astype(int)
    df["cre"] = pd.to_numeric(df["cre"], errors="coerce").astype("Int64")

    fatores = df["fatores"].astype(str).str.zfill(7)
    for posicao, etapa in enumerate(ETAPAS_BITS):
        df[f"tem_{etapa}"] = fatores.str[posicao] == "1"

    df["modalidades_pd"] = df.apply(
        lambda linha: [etapa for etapa in MODALIDADES_PD if linha[f"tem_{etapa}"]],
        axis=1,
    )
    df["tem_pd"] = df["modalidades_pd"].apply(len) > 0
    df["tem_ef"] = df["tem_AI"] | df["tem_AF"]

    return df.reset_index(drop=True)


def buscar_unidades(df: pd.DataFrame, termo: str) -> pd.DataFrame:
    """Busca unidades por designação, designação antiga, denominação ou sigla.

    A busca ignora acentos e maiúsculas/minúsculas e aceita correspondência
    parcial (substring). Designações no formato "xx.xx.xxx" também são
    aceitas sem os pontos (ex.: "10.10.001" encontra a designação 1010001).
    """
    termo_norm = _normalizar(termo)
    if not termo_norm:
        return df.iloc[0:0]

    colunas_busca = ["designacao", "designacao_antiga", "denominacao", "sigla"]
    termo_escapado = re.escape(termo_norm)

    mascara = pd.Series(False, index=df.index)
    for coluna in colunas_busca:
        mascara |= (
            df[coluna]
            .astype(str)
            .apply(_normalizar)
            .str.contains(termo_escapado, na=False, regex=True)
        )

    termo_sem_pontos = termo_norm.replace(".", "")
    if termo_sem_pontos and termo_sem_pontos != termo_norm:
        termo_sem_pontos_escapado = re.escape(termo_sem_pontos)
        for coluna in ("designacao", "designacao_antiga"):
            mascara |= (
                df[coluna]
                .astype(str)
                .apply(_normalizar)
                .str.contains(termo_sem_pontos_escapado, na=False, regex=True)
            )

    return df[mascara]
