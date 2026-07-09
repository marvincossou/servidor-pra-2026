"""Testes do carregador de metas reais por escola (Anexos I/II da Resolução
SME nº 561/2026, base/metas_pra_2026.csv).

Os valores esperados foram conferidos manualmente linha a linha no PDF
oficial (via `pdftotext -layout`) antes de gerar o CSV.
"""

import pytest

from src.metas_pra_2026 import carregar_metas, descricoes_indicadores


@pytest.fixture(scope="module")
def metas():
    return carregar_metas()


def _indicador(indicadores, numeral):
    encontrados = [i for i in indicadores if i["indicador"] == numeral]
    assert encontrados, f"indicador {numeral} não encontrado"
    return encontrados[0]


def test_total_de_designacoes_com_metas(metas):
    assert len(metas) == 996


def test_designacao_101003_alfabetizacao(metas):
    item = _indicador(metas[101003], "I")
    assert item["resultado"] == 64.0
    assert item["meta_2026"] == 69.0
    assert item["crescimento_esperado"] == 5.0

    item = _indicador(metas[101003], "II")
    assert item["resultado"] == 65.0
    assert item["meta_2026"] == 69.0
    assert item["crescimento_esperado"] == 4.0


def test_designacao_107008_indicador_rendimento_substitui_iderio(metas):
    ids = {i["indicador"] for i in metas[107008]}
    assert "III" not in ids, "IDERio 4º não deveria se aplicar (substituído por VII)"
    assert "IV" not in ids, "IDERio 5º não deveria se aplicar (substituído por VII)"

    item = _indicador(metas[107008], "VII")
    assert item["resultado"] == 0.98
    assert item["meta_2026"] == 0.99
    assert item["crescimento_esperado"] == 0.01


def test_designacao_206001_meta_ja_atingida_vira_crescimento_zero(metas):
    item = _indicador(metas[206001], "VII")
    assert item["resultado"] == 1.0
    assert item["meta_2026"] == 0.99
    assert item["crescimento_esperado"] == 0.0


def test_escola_so_infantil_nao_tem_metas(metas):
    # 1001 é uma Biblioteca Escolar exclusiva (ver CASOS_BITS em
    # test_regras_pra_2026.py) — não tem AI/AF, logo sem indicador nesta fonte.
    assert 1001 not in metas


def test_descricoes_indicadores_cobre_todos_os_indicadores_com_meta():
    descricoes = descricoes_indicadores()
    assert set(descricoes) == {"I", "II", "III", "IV", "V", "VI", "VII", "VIII"}
    for numeral, info in descricoes.items():
        assert info["descricao"]
        assert info["unidade"] in ("pp", "pontos", "indice")


def test_todos_os_indicadores_usados_tem_descricao(metas):
    descricoes = descricoes_indicadores()
    for indicadores in metas.values():
        for item in indicadores:
            assert item["indicador"] in descricoes
