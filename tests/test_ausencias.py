"""Testes do carregamento da tabela de tipos de afastamento (Ausencias.xlsx)."""

import pytest

from src.ausencias import INTRO_AUSENCIAS, carregar_ausencias


@pytest.fixture(scope="module")
def registros():
    return carregar_ausencias("base/Ausencias.xlsx")


def _por_codigo(registros, cod):
    encontrados = [r for r in registros if r["cod"] == cod]
    assert encontrados, f"código {cod} não encontrado"
    return encontrados[0]


def test_carrega_registros(registros):
    assert len(registros) == 56


def test_campos_esperados(registros):
    campos = {"cod", "descricao", "conta_como_ausencia", "falta_nao_justificada", "observacoes"}
    for registro in registros:
        assert campos == set(registro.keys())


def test_codigo_formatado_com_zeros_a_esquerda(registros):
    ferias = _por_codigo(registros, "000")
    assert "FÉRIAS" in ferias["descricao"].upper()
    assert ferias["conta_como_ausencia"] is False
    assert ferias["falta_nao_justificada"] is False


def test_falta_nao_justificada_verdadeira_para_codigo_991(registros):
    falta = _por_codigo(registros, "991")
    assert falta["conta_como_ausencia"] is True
    assert falta["falta_nao_justificada"] is True


def test_licenca_gestante_conta_como_ausencia_mas_nao_e_falta(registros):
    licencas = [r for r in registros if "GESTANTE" in r["descricao"].upper()]
    assert licencas, "esperava ao menos uma licença gestante na base"
    for licenca in licencas:
        assert licenca["conta_como_ausencia"] is True
        assert licenca["falta_nao_justificada"] is False


def test_observacao_preservada_quando_existe(registros):
    pleito = _por_codigo(registros, "112")
    assert pleito["observacoes"] == "PLEITO ELETIVO"


def test_observacao_none_quando_ausente(registros):
    ferias = _por_codigo(registros, "000")
    assert ferias["observacoes"] is None


def test_intro_ausencias_nao_cita_resolucao_como_fonte():
    # A introdução pode citar o artigo que deixa a regra aberta, mas não deve
    # apresentar as regras operacionais desta tabela como se fossem da Resolução.
    assert "Art. 8º" in INTRO_AUSENCIAS
