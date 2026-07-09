"""Testes de decodificação de bits e classificação de Fator Geral (PRA 2026).

Usa amostras reais de `base/dp_sme.xlsx` (aba DeParaUnidades2) cobrindo os
principais tipos de unidade. Diferente do painel de 2025, este projeto não
sobrepõe os bits com o arquivo de "Fator de Premiação" — por isso não há
distinção "carioca" aqui (ver `src/dados.py`).
"""

import pytest

from src.dados import carregar_unidades
from src.faq import FAQ, faq_visivel
from src.regras_pra_2026 import (
    CRITERIOS_ELEGIBILIDADE,
    GLOSSARIO,
    PENDENCIAS_VERIFICACAO,
    avaliar_elegibilidade,
    cargos_disponiveis,
    classificar_fator_geral,
    combinacoes_respostas_elegibilidade,
    conclusao_elegibilidade_markdown,
    explicar_elegibilidade,
    explicar_fator_geral,
    explicar_formula_final,
    explicar_nota_indicador,
    explicar_professor,
    formatar_cre,
    pendencias_verificacao_markdown,
    questionario_elegibilidade,
)


@pytest.fixture(scope="module")
def df():
    return carregar_unidades("base/dp_sme.xlsx")


def _unidade(df, designacao):
    linhas = df[df["designacao"] == designacao]
    assert not linhas.empty, f"Designação {designacao} não encontrada na base"
    return linhas.iloc[0]


# Designação -> (tem_AI, tem_AF, tem_EI, tem_EJA, tem_EE, tem_UE, tem_BI)
CASOS_BITS = {
    1001: (False, False, False, False, False, False, True),  # Biblioteca
    101001: (False, True, False, False, True, False, False),  # Mistas (AF + EE)
    102504: (False, False, False, True, True, False, False),  # Mistas (EJA + EE)
    102505: (True, False, True, True, False, False, False),  # Mistas (AI + EI + EJA)
    103001: (True, True, False, False, False, False, False),  # Mistas (AI + AF)
    204001: (False, True, False, False, False, False, False),  # Exclusivo Fund II
    204006: (True, False, False, False, False, False, False),  # Exclusivo Fund I
    204801: (False, False, True, False, False, False, False),  # Exclusiva EI
    206014: (False, False, False, False, True, False, False),  # Exclusiva EE
    430701: (False, False, False, True, False, False, False),  # Exclusiva EJA
    817701: (False, False, False, False, False, True, False),  # Unidade de Extensão
}


@pytest.mark.parametrize("designacao,esperado", CASOS_BITS.items())
def test_decodificacao_bits(df, designacao, esperado):
    unidade = _unidade(df, designacao)
    obtido = (
        unidade["tem_AI"],
        unidade["tem_AF"],
        unidade["tem_EI"],
        unidade["tem_EJA"],
        unidade["tem_EE"],
        unidade["tem_UE"],
        unidade["tem_BI"],
    )
    assert obtido == esperado


# Designação -> tipo esperado de Fator Geral
CASOS_CLASSIFICACAO = {
    1001: "PD",  # Biblioteca
    101001: "MISTA",  # AF + EE (sem EI/EJA -> lacuna sinalizada)
    102504: "PD",  # EJA + EE, sem AI/AF
    102505: "MISTA",  # AI + EI + EJA
    103001: "EF",  # AI + AF, sem PD
    204001: "EF",  # só AF
    204006: "EF",  # só AI
    204801: "PD",  # Exclusiva EI
    206014: "PD",  # Exclusiva EE
    430701: "PD",  # Exclusiva EJA
    817701: "PD",  # Unidade de Extensão
}


@pytest.mark.parametrize("designacao,tipo_esperado", CASOS_CLASSIFICACAO.items())
def test_classificacao_fator_geral(df, designacao, tipo_esperado):
    unidade = _unidade(df, designacao)
    classificacao = classificar_fator_geral(unidade)
    assert classificacao["tipo"] == tipo_esperado


def test_explicacao_fator_geral_nao_quebra_para_todos_os_tipos(df):
    for designacao in CASOS_CLASSIFICACAO:
        unidade = _unidade(df, designacao)
        texto = explicar_fator_geral(unidade)
        assert "Fator Geral" in texto


def test_mista_com_ei_ou_eja_recebe_texto_de_bonus(df):
    unidade = _unidade(df, 102505)  # AI + EI + EJA
    texto = explicar_fator_geral(unidade)
    assert "+0,10" in texto or "+0,20" in texto


def test_mista_sem_ei_eja_sinaliza_lacuna_em_vez_de_bonus(df):
    unidade = _unidade(df, 101001)  # AF + EE, sem EI/EJA
    texto = explicar_fator_geral(unidade)
    assert "não está coberto" in texto
    assert "+0,10" not in texto
    assert "+0,20" not in texto


def test_classe_especial_segue_fator_geral_quando_unidade_tem_ef(df):
    unidade = _unidade(df, 101001)  # tem AF -> tem_ef True
    texto = explicar_professor(unidade, "EE_CE_SRM")
    assert "Fator Geral" in texto


def test_classe_especial_usa_pd_quando_unidade_sem_ef(df):
    unidade = _unidade(df, 206014)  # Exclusiva EE, sem EF
    texto = explicar_professor(unidade, "EE_CE_SRM")
    assert "Indicador IX" in texto


def test_cargos_disponiveis_inclui_geral_sempre(df):
    for designacao in CASOS_CLASSIFICACAO:
        unidade = _unidade(df, designacao)
        codigos = [codigo for codigo, _ in cargos_disponiveis(unidade)]
        assert codigos[-1] == "GERAL"


@pytest.mark.parametrize(
    "cre,esperado",
    [(1, "1ª CRE"), (10, "10ª CRE"), (None, "None")],
)
def test_formatar_cre(cre, esperado):
    assert formatar_cre(cre) == esperado


def test_glossario_cobre_siglas_usadas_nos_textos():
    siglas_essenciais = ["CRE", "CTRH", "PD", "IDERio", "CAEd", "AR", "ICG"]
    for sigla in siglas_essenciais:
        assert sigla in GLOSSARIO


def test_explicar_elegibilidade_nao_quebra():
    texto = explicar_elegibilidade()
    assert "¾" in texto
    assert "Diretor IV" in texto


# Respostas que atendem a todos os critérios (sem ter sido Diretor IV).
RESPOSTAS_TUDO_OK = {
    "pleno_exercicio": "sim",
    "lotacao_ue": "sim",
    "elegivel_ar": "não",
    "penalidade": "não",
    "exonerado": "não",
    "falta": "não",
    "foi_diretor_iv": "não",
}


def test_avaliar_elegibilidade_tudo_ok_atende():
    resultado, falhos = avaliar_elegibilidade(RESPOSTAS_TUDO_OK)
    assert resultado == "atende"
    assert falhos == []


def test_avaliar_elegibilidade_ar_torna_inelegivel():
    respostas = {**RESPOSTAS_TUDO_OK, "elegivel_ar": "sim"}
    resultado, falhos = avaliar_elegibilidade(respostas)
    assert resultado == "inelegivel"
    assert falhos == ["elegivel_ar"]


def test_avaliar_elegibilidade_falta_encaminha_para_ctrh():
    respostas = {**RESPOSTAS_TUDO_OK, "falta": "sim"}
    resultado, falhos = avaliar_elegibilidade(respostas)
    assert resultado == "ctrh"
    assert falhos == ["falta"]


def test_avaliar_elegibilidade_diretor_iv_insatisfatorio_vai_para_ctrh():
    respostas = {
        **RESPOSTAS_TUDO_OK,
        "foi_diretor_iv": "sim",
        "gestor_insatisfatorio": "sim",
    }
    resultado, falhos = avaliar_elegibilidade(respostas)
    assert resultado == "ctrh"
    assert falhos == ["gestor_insatisfatorio"]


def test_avaliar_elegibilidade_inelegivel_tem_precedencia_sobre_ctrh():
    respostas = {**RESPOSTAS_TUDO_OK, "penalidade": "sim", "falta": "sim"}
    resultado, falhos = avaliar_elegibilidade(respostas)
    assert resultado == "inelegivel"
    assert set(falhos) == {"penalidade", "falta"}


def test_avaliar_elegibilidade_lista_todas_as_falhas():
    respostas = {**RESPOSTAS_TUDO_OK, "pleno_exercicio": "não", "exonerado": "sim"}
    resultado, falhos = avaliar_elegibilidade(respostas)
    assert resultado == "inelegivel"
    assert set(falhos) == {"pleno_exercicio", "exonerado"}


def test_conclusao_sempre_contem_disclaimer():
    for respostas in (
        RESPOSTAS_TUDO_OK,
        {**RESPOSTAS_TUDO_OK, "falta": "sim"},
        {**RESPOSTAS_TUDO_OK, "elegivel_ar": "sim"},
    ):
        _, markdown = conclusao_elegibilidade_markdown(respostas)
        assert "orientativo" in markdown
        assert "CTRH" in markdown


def test_conclusao_inelegivel_menciona_tambem_pontos_ctrh():
    respostas = {**RESPOSTAS_TUDO_OK, "penalidade": "sim", "falta": "sim"}
    resultado, markdown = conclusao_elegibilidade_markdown(respostas)
    assert resultado == "inelegivel"
    assert "penalidade" in markdown
    assert "falta" in markdown


def test_combinacoes_respostas_cobrem_todo_o_espaco():
    combinacoes = combinacoes_respostas_elegibilidade()
    chaves = [chave for chave, _ in combinacoes]
    assert len(chaves) == len(set(chaves)), "chaves duplicadas"
    n_perguntas = len(CRITERIOS_ELEGIBILIDADE)
    assert all(len(chave) == n_perguntas for chave in chaves)
    # 6 independentes + foi_diretor_iv: quando "não", a condicional vira "x";
    # quando "sim", desdobra em sim/não -> 2^6 * (1 + 2) = 192 combinações.
    assert len(chaves) == 192
    # O "x" só pode aparecer na posição da pergunta condicional.
    posicoes_condicionais = {
        i for i, c in enumerate(CRITERIOS_ELEGIBILIDADE) if c["depende_de"]
    }
    for chave in chaves:
        for i, letra in enumerate(chave):
            assert letra in ("s", "n", "x")
            if letra == "x":
                assert i in posicoes_condicionais


def test_questionario_elegibilidade_espelha_criterios():
    questionario = questionario_elegibilidade()
    assert [p["id"] for p in questionario["perguntas"]] == [
        c["id"] for c in CRITERIOS_ELEGIBILIDADE
    ]
    # O contrato público não expõe a interpretação dos critérios.
    for pergunta in questionario["perguntas"]:
        assert "resposta_ok" not in pergunta
        assert "consequencia_falha" not in pergunta
    assert "CTRH" in questionario["disclaimer"]


def test_explicar_formula_final_contem_formula():
    texto = explicar_formula_final()
    assert "Fração da carga" in texto


def test_explicar_nota_indicador_descreve_as_tres_faixas():
    texto = explicar_nota_indicador()
    assert "80%" in texto
    assert "0,00" in texto
    assert "1,00" in texto


def test_pendencias_verificacao_nao_vazias():
    assert len(PENDENCIAS_VERIFICACAO) >= 5
    texto = pendencias_verificacao_markdown()
    for item in PENDENCIAS_VERIFICACAO:
        assert item["titulo"] in texto


def test_faq_pendente_ctrh_nao_afirma_regra_nao_documentada():
    for item in FAQ:
        if item["status"] == "pendente_ctrh":
            resposta = item["resposta"]
            assert "CTRH" in resposta or "e-mail institucional" in resposta


def test_faq_visivel_so_traz_itens_documentados_ou_operacionais():
    for item in faq_visivel():
        assert item["status"] in ("documentado", "operacional")
