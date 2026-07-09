"""Gera a versão PWA estática do painel PRA 2026 a partir do motor Python.

Usa o mesmo motor de regras de `src/regras_pra_2026.py` (testado em
`tests/test_regras_pra_2026.py`) para pré-renderizar, em tempo de build, todos
os textos explicativos como HTML. A PWA em si (vanilla JS) só faz busca e
exibição — nenhuma regra de negócio é reescrita em JavaScript.

Uso:
    python scripts/build_pwa.py [--saida dist]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

import markdown
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.ausencias import INTRO_AUSENCIAS, carregar_ausencias  # noqa: E402
from src.busca_legislacao import documentos_busca  # noqa: E402
from src.dados import ETAPAS_BITS, MODALIDADES_PD, carregar_unidades  # noqa: E402
from src.faq import faq_visivel  # noqa: E402
from src.regras_pra_2026 import (  # noqa: E402
    ETAPA_ICONS,
    ETAPA_LABELS,
    cargos_disponiveis,
    explicar_elegibilidade,
    explicar_fator_geral,
    explicar_formula_final,
    explicar_nota_indicador,
    explicar_professor,
    formatar_cre,
    formatar_tipo_unidade,
    glossario_markdown,
    pendencias_verificacao_markdown,
)
from src.textos_ui import (
    AVISO_ESCOPO,
    AVISO_ESCOPO_TITULO,
    BOTAO_PERGUNTAR_IA,
    BUSCA_ASSUNTO_DICA_VAZIA,
    BUSCA_ASSUNTO_LABEL,
    BUSCA_ASSUNTO_PLACEHOLDER,
    BUSCA_ASSUNTO_SEM_RESULTADO,
    BUSCA_DICA_VAZIA,
    BUSCA_LABEL,
    BUSCA_PLACEHOLDER,
    BUSCA_SEM_RESULTADO,
    IA_CARREGANDO,
    IA_DISCLAIMER,
    IA_ERRO,
    INTRO,
    RODAPE_FONTE,
    SEM_ETAPAS_REGENCIA,
    TITULO_PAGINA,
)

PWA_SRC = RAIZ / "pwa"
PADRAO_VALOR_MONETARIO = re.compile(r"R\$\s*\d")


def _cabecalho_regex(md_texto: str) -> str:
    """Rebaixa um nível os cabeçalhos markdown (## -> ###, #### -> #####).

    Os textos do motor assumem que serão o único conteúdo da página (por
    isso usam "##"/"####" como títulos de topo). Como a PWA os injeta dentro
    de uma seção que já tem h1/h2 próprios, rebaixamos um nível para manter
    a hierarquia de acessibilidade correta.
    """
    return re.sub(r"(?m)^(#+)(\s)", r"#\1\2", md_texto)


def _md_para_html(md_texto: str) -> str:
    md_texto = _cabecalho_regex(md_texto)
    return markdown.markdown(md_texto, extensions=["tables", "sane_lists"])


def _chave_perfil(linha: pd.Series) -> tuple:
    return (
        bool(linha["tem_AI"]),
        bool(linha["tem_AF"]),
        bool(linha["tem_EI"]),
        bool(linha["tem_EJA"]),
        bool(linha["tem_EE"]),
        bool(linha["tem_UE"]),
        bool(linha["tem_BI"]),
    )


def _gerar_perfis(df: pd.DataFrame) -> tuple[dict[tuple, int], list[dict]]:
    """Agrupa as unidades por perfil (as flags que determinam o texto) e
    pré-renderiza, uma única vez por perfil, todo o HTML explicativo.
    """
    chaves = df.apply(_chave_perfil, axis=1)
    chaves_unicas = sorted(set(chaves))
    indice_por_chave = {chave: indice for indice, chave in enumerate(chaves_unicas)}

    perfis = []
    for chave in chaves_unicas:
        posicao = chaves[chaves == chave].index[0]
        unidade = df.loc[posicao]

        etapas = [etapa for etapa in ETAPAS_BITS if unidade[f"tem_{etapa}"]]
        modalidades_pd = [m for m in MODALIDADES_PD if unidade[f"tem_{m}"]]
        cargos = [c for c in cargos_disponiveis(unidade) if c[0] != "GERAL"]

        html_professor = {
            codigo: _md_para_html(explicar_professor(unidade, codigo))
            for codigo, _ in cargos
        }

        perfis.append(
            {
                "etapas": etapas,
                "modalidades_pd": modalidades_pd,
                "tem_pd": bool(unidade["tem_pd"]),
                "cargos": cargos,
                "html": {
                    "fator_geral": _md_para_html(explicar_fator_geral(unidade)),
                    "professor": html_professor,
                },
            }
        )

    return indice_por_chave, perfis


def _gerar_unidades_json(df: pd.DataFrame, indice_por_chave: dict[tuple, int]) -> dict:
    tipos_brutos = sorted(df["tipo_unidade"].astype(str).unique())
    indice_por_tipo = {tipo: i for i, tipo in enumerate(tipos_brutos)}
    tipos_formatados = [formatar_tipo_unidade(t) for t in tipos_brutos]

    linhas = []
    for _, unidade in df.iterrows():
        perfil_idx = indice_por_chave[_chave_perfil(unidade)]
        tipo_idx = indice_por_tipo[str(unidade["tipo_unidade"])]
        cre = unidade["cre"]
        cre_num = int(cre) if pd.notna(cre) else None
        linhas.append(
            [
                int(unidade["designacao"]),
                str(unidade["designacao_antiga"]),
                str(unidade["denominacao"]),
                str(unidade["sigla"]),
                cre_num,
                formatar_cre(cre),
                tipo_idx,
                perfil_idx,
            ]
        )

    return {
        "colunas": [
            "designacao",
            "designacao_antiga",
            "denominacao",
            "sigla",
            "cre_num",
            "cre_formatada",
            "tipo_idx",
            "perfil_idx",
        ],
        "tipos": tipos_formatados,
        "unidades": linhas,
    }


def _gerar_estaticos_json() -> dict:
    return {
        "glossario_html": _md_para_html(glossario_markdown()),
        "elegibilidade_html": _md_para_html(explicar_elegibilidade()),
        "formula_final_html": _md_para_html(explicar_formula_final()),
        "nota_indicador_html": _md_para_html(explicar_nota_indicador()),
        "pendencias_verificacao_html": _md_para_html(pendencias_verificacao_markdown()),
        "faq": [
            {"pergunta": item["pergunta"], "resposta_html": _md_para_html(item["resposta"])}
            for item in faq_visivel()
        ],
        "etapa_labels": ETAPA_LABELS,
        "etapa_icons": ETAPA_ICONS,
        "ausencias_intro_html": _md_para_html(INTRO_AUSENCIAS),
        "ausencias": carregar_ausencias(),
        "textos_ui": {
            "titulo_pagina": TITULO_PAGINA,
            "intro_html": _md_para_html(INTRO),
            "aviso_escopo_titulo": AVISO_ESCOPO_TITULO,
            "aviso_escopo_html": _md_para_html(AVISO_ESCOPO),
            "busca_label": BUSCA_LABEL,
            "busca_placeholder": BUSCA_PLACEHOLDER,
            "busca_dica_vazia_html": _md_para_html(BUSCA_DICA_VAZIA),
            "busca_sem_resultado": BUSCA_SEM_RESULTADO,
            "sem_etapas_regencia_html": _md_para_html(SEM_ETAPAS_REGENCIA),
            "rodape_fonte": RODAPE_FONTE,
            "busca_assunto_label": BUSCA_ASSUNTO_LABEL,
            "busca_assunto_placeholder": BUSCA_ASSUNTO_PLACEHOLDER,
            "busca_assunto_dica_vazia_html": _md_para_html(BUSCA_ASSUNTO_DICA_VAZIA),
            "busca_assunto_sem_resultado": BUSCA_ASSUNTO_SEM_RESULTADO,
            "botao_perguntar_ia": BOTAO_PERGUNTAR_IA,
            "ia_carregando": IA_CARREGANDO,
            "ia_disclaimer": IA_DISCLAIMER,
            "ia_erro": IA_ERRO,
        },
    }


def _gerar_busca_json() -> dict:
    """Índice de documentos para a busca por assunto (TF-IDF calculado no
    navegador, ver `pwa/js/app.js`). Fonte: `src/busca_legislacao.py`."""
    documentos = [
        {
            "id": doc["id"],
            "titulo": doc["titulo"],
            "texto": doc["texto"],
            "sinonimos": doc["sinonimos"],
            "html": _md_para_html(doc["texto"]),
        }
        for doc in documentos_busca()
    ]
    return {"documentos": documentos}


def _verificar_sem_valores_monetarios(*dados: dict) -> None:
    """Guarda-corpo: a PWA nunca deve exibir valores calculados de premiação."""
    for bloco in dados:
        texto = json.dumps(bloco, ensure_ascii=False)
        achado = PADRAO_VALOR_MONETARIO.search(texto)
        if achado:
            trecho = texto[max(0, achado.start() - 40) : achado.start() + 40]
            raise SystemExit(
                f"ERRO: padrão de valor monetário encontrado no build ({trecho!r}). "
                "A PWA não pode exibir valores calculados de premiação."
            )


def _calcular_hash(pasta: Path) -> str:
    hash_geral = hashlib.sha256()
    for caminho in sorted(pasta.rglob("*")):
        if caminho.is_file():
            hash_geral.update(caminho.relative_to(pasta).as_posix().encode("utf-8"))
            hash_geral.update(caminho.read_bytes())
    return hash_geral.hexdigest()[:12]


def gerar_build(pasta_saida: Path) -> dict:
    """Executa o build completo e devolve um resumo (para log/testes)."""
    df = carregar_unidades()

    if df["designacao"].duplicated().any():
        raise SystemExit("ERRO: há designações duplicadas na base de unidades.")

    indice_por_chave, perfis = _gerar_perfis(df)
    unidades_json = _gerar_unidades_json(df, indice_por_chave)
    estaticos_json = _gerar_estaticos_json()
    busca_json = _gerar_busca_json()

    if len(unidades_json["unidades"]) != len(df):
        raise SystemExit("ERRO: nem toda unidade recebeu uma linha em unidades.json.")
    if any(linha[-1] >= len(perfis) for linha in unidades_json["unidades"]):
        raise SystemExit("ERRO: unidade referenciando perfil inexistente.")

    _verificar_sem_valores_monetarios({"perfis": perfis}, unidades_json, estaticos_json, busca_json)

    dados_de = datetime.date.today().strftime("%d/%m/%Y")
    unidades_json["dados_de"] = dados_de
    unidades_json["fonte"] = RODAPE_FONTE

    pasta_dados = pasta_saida / "dados"
    pasta_dados.mkdir(parents=True, exist_ok=True)
    (pasta_dados / "unidades.json").write_text(
        json.dumps(unidades_json, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (pasta_dados / "perfis.json").write_text(
        json.dumps({"perfis": perfis}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (pasta_dados / "estaticos.json").write_text(
        json.dumps(estaticos_json, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (pasta_dados / "busca.json").write_text(
        json.dumps(busca_json, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )

    # Copia o app shell quando existir; o build de dados funciona mesmo
    # antes de pwa/ existir.
    if PWA_SRC.exists():
        for item in PWA_SRC.iterdir():
            destino = pasta_saida / item.name
            if item.is_dir():
                shutil.copytree(item, destino, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destino)

        versao = _calcular_hash(pasta_saida)
        sw_path = pasta_saida / "sw.js"
        if sw_path.exists():
            sw_path.write_text(
                sw_path.read_text(encoding="utf-8").replace("__VERSAO__", versao),
                encoding="utf-8",
            )
    else:
        versao = None

    return {
        "total_unidades": len(df),
        "total_perfis": len(perfis),
        "dados_de": dados_de,
        "versao": versao,
        "tamanho_unidades_json": (pasta_dados / "unidades.json").stat().st_size,
        "tamanho_perfis_json": (pasta_dados / "perfis.json").stat().st_size,
        "tamanho_estaticos_json": (pasta_dados / "estaticos.json").stat().st_size,
        "tamanho_busca_json": (pasta_dados / "busca.json").stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", default="dist", help="Pasta de saída (padrão: dist)")
    args = parser.parse_args()

    pasta_saida = RAIZ / args.saida
    if pasta_saida.exists():
        # Retry: em pastas sincronizadas pelo OneDrive, um arquivo pode ficar
        # momentaneamente bloqueado por indexação/sync.
        for tentativa in range(3):
            try:
                shutil.rmtree(pasta_saida)
                break
            except PermissionError:
                if tentativa == 2:
                    raise
                time.sleep(1)

    resumo = gerar_build(pasta_saida)

    print(f"Unidades: {resumo['total_unidades']}")
    print(f"Perfis distintos: {resumo['total_perfis']}")
    print(f"Dados de: {resumo['dados_de']}")
    print(f"Versão (hash): {resumo['versao']}")
    print(f"unidades.json: {resumo['tamanho_unidades_json'] / 1024:.1f} KB")
    print(f"perfis.json: {resumo['tamanho_perfis_json'] / 1024:.1f} KB")
    print(f"estaticos.json: {resumo['tamanho_estaticos_json'] / 1024:.1f} KB")
    print(f"busca.json: {resumo['tamanho_busca_json'] / 1024:.1f} KB")


if __name__ == "__main__":
    main()
