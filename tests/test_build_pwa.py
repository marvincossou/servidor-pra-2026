"""Testes de paridade: o JSON gerado para a PWA precisa refletir exatamente
o motor de regras Python (`src/regras_pra_2026.py`), unidade por unidade.

Roda o build inteiro numa pasta temporária (não mexe em `dist/`) e compara
os HTMLs pré-renderizados com o que o motor gera para as mesmas unidades
usadas em `tests/test_regras_pra_2026.py`.
"""

import json
import shutil
import subprocess

import pytest

from scripts.build_pwa import _md_para_html, gerar_build
from src.dados import _normalizar, carregar_unidades
from src.faq import faq_visivel
from src.regras_pra_2026 import (
    cargos_disponiveis,
    combinacoes_respostas_elegibilidade,
    conclusao_elegibilidade_markdown,
    explicar_elegibilidade,
    explicar_fator_geral,
    explicar_formula_final,
    explicar_nota_indicador,
    explicar_professor,
    pendencias_verificacao_markdown,
    questionario_elegibilidade,
)

# Mesmas designações usadas em tests/test_regras_pra_2026.py (CASOS_CLASSIFICACAO).
DESIGNACOES_REPRESENTATIVAS = [
    1001,  # Biblioteca
    101001,  # Mistas (AF + EE)
    102504,  # EJA + EE, sem AI/AF
    102505,  # AI + EI + EJA
    103001,  # AI + AF, sem PD
    204001,  # só AF
    204006,  # só AI
    204801,  # Exclusiva EI
    206014,  # Exclusiva EE
    430701,  # Exclusiva EJA
    817701,  # Unidade de Extensão
]


@pytest.fixture(scope="module")
def df():
    return carregar_unidades("base/dp_sme.xlsx")


@pytest.fixture(scope="module")
def build(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("dist_teste")
    resumo = gerar_build(pasta)
    unidades_json = json.loads((pasta / "dados" / "unidades.json").read_text(encoding="utf-8"))
    perfis_json = json.loads((pasta / "dados" / "perfis.json").read_text(encoding="utf-8"))
    estaticos_json = json.loads((pasta / "dados" / "estaticos.json").read_text(encoding="utf-8"))
    busca_json = json.loads((pasta / "dados" / "busca.json").read_text(encoding="utf-8"))
    return {
        "resumo": resumo,
        "unidades": unidades_json,
        "perfis": perfis_json["perfis"],
        "estaticos": estaticos_json,
        "busca": busca_json,
    }


def _unidade(df, designacao):
    linhas = df[df["designacao"] == designacao]
    assert not linhas.empty, f"Designação {designacao} não encontrada na base"
    return linhas.iloc[0]


def _linha_unidade(build, designacao):
    colunas = build["unidades"]["colunas"]
    idx_designacao = colunas.index("designacao")
    for linha in build["unidades"]["unidades"]:
        if linha[idx_designacao] == designacao:
            return dict(zip(colunas, linha))
    raise AssertionError(f"Designação {designacao} não encontrada em unidades.json")


def test_build_cobre_todas_as_unidades(df, build):
    assert build["resumo"]["total_unidades"] == len(df)
    assert len(build["unidades"]["unidades"]) == len(df)


def test_build_tem_ao_menos_um_perfil(build):
    assert build["resumo"]["total_perfis"] == len(build["perfis"])
    assert len(build["perfis"]) >= 1


@pytest.mark.parametrize("designacao", DESIGNACOES_REPRESENTATIVAS)
def test_paridade_fator_geral(df, build, designacao):
    unidade = _unidade(df, designacao)
    esperado = _md_para_html(explicar_fator_geral(unidade))
    linha = _linha_unidade(build, designacao)
    perfil = build["perfis"][linha["perfil_idx"]]
    assert perfil["html"]["fator_geral"] == esperado


@pytest.mark.parametrize("designacao", DESIGNACOES_REPRESENTATIVAS)
def test_paridade_professor_por_cargo(df, build, designacao):
    unidade = _unidade(df, designacao)
    linha = _linha_unidade(build, designacao)
    perfil = build["perfis"][linha["perfil_idx"]]

    cargos_esperados = [c for c in cargos_disponiveis(unidade) if c[0] != "GERAL"]
    assert sorted(codigo for codigo, _ in cargos_esperados) == sorted(perfil["html"]["professor"])

    for codigo, _ in cargos_esperados:
        esperado = _md_para_html(explicar_professor(unidade, codigo))
        assert perfil["html"]["professor"][codigo] == esperado


def test_paridade_estaticos(build):
    assert build["estaticos"]["elegibilidade_html"] == _md_para_html(explicar_elegibilidade())
    assert build["estaticos"]["formula_final_html"] == _md_para_html(explicar_formula_final())
    assert build["estaticos"]["nota_indicador_html"] == _md_para_html(explicar_nota_indicador())
    assert build["estaticos"]["pendencias_verificacao_html"] == _md_para_html(
        pendencias_verificacao_markdown()
    )


def test_faq_do_build_bate_com_faq_visivel(build):
    esperado = [item["pergunta"] for item in faq_visivel()]
    obtido = [item["pergunta"] for item in build["estaticos"]["faq"]]
    assert obtido == esperado


def test_faq_do_build_nao_contem_pendente_ctrh(build):
    perguntas_visiveis = {item["pergunta"] for item in build["estaticos"]["faq"]}
    perguntas_pendentes = {
        "Estive de licença/afastado em 2026. Isso muda algo no meu cálculo?",
        "Quando o pagamento da PRA será feito?",
        "Não concordo com meu enquadramento. Como contestar?",
    }
    assert not (perguntas_visiveis & perguntas_pendentes)


def test_nenhum_json_contem_valor_monetario(build):
    import re

    for bloco in (build["unidades"], {"perfis": build["perfis"]}, build["estaticos"], build["busca"]):
        texto = json.dumps(bloco, ensure_ascii=False)
        assert not re.search(r"R\$\s*\d", texto)


def test_busca_json_tem_documentos(build):
    assert len(build["busca"]["documentos"]) > 0
    for doc in build["busca"]["documentos"]:
        assert doc["id"]
        assert doc["titulo"]
        assert doc["html"]


def test_toda_unidade_referencia_perfil_valido(build):
    colunas = build["unidades"]["colunas"]
    idx_perfil = colunas.index("perfil_idx")
    total_perfis = len(build["perfis"])
    for linha in build["unidades"]["unidades"]:
        assert 0 <= linha[idx_perfil] < total_perfis


def test_toda_unidade_referencia_tipo_valido(build):
    colunas = build["unidades"]["colunas"]
    idx_tipo = colunas.index("tipo_idx")
    total_tipos = len(build["unidades"]["tipos"])
    for linha in build["unidades"]["unidades"]:
        assert 0 <= linha[idx_tipo] < total_tipos


def test_dados_de_no_formato_dd_mm_aaaa(build):
    import re

    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", build["unidades"]["dados_de"])


def test_normalizacao_js_bate_com_python(df):
    """A busca da PWA (pwa/js/app.js) reimplementa `_normalizar` em JS —
    compara as duas para os textos reais (com acento) da base, usando Node.
    Pula silenciosamente se o Node não estiver disponível."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js não disponível neste ambiente")

    amostras = set()
    for coluna in ("denominacao", "sigla"):
        amostras.update(df[coluna].astype(str).unique()[:200])
    amostras = [a for a in amostras if any(ord(c) > 127 for c in a)][:60]
    assert amostras, "esperava ao menos uma amostra com acento na base"

    script_js = """
    const REGEX_NAO_ASCII = new RegExp("[^\\\\x00-\\\\x7F]", "g");
    function normalizar(texto) {
      return String(texto).normalize("NFKD").replace(REGEX_NAO_ASCII, "").toLowerCase().trim();
    }
    const entrada = JSON.parse(require("fs").readFileSync(0, "utf-8"));
    process.stdout.write(JSON.stringify(entrada.map(normalizar)));
    """
    resultado = subprocess.run(
        [node, "-e", script_js],
        input=json.dumps(amostras),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert resultado.returncode == 0, resultado.stderr
    normalizados_js = json.loads(resultado.stdout)
    normalizados_py = [_normalizar(a) for a in amostras]
    assert normalizados_js == normalizados_py


def test_questionario_perguntas_batem_com_o_motor(build):
    questionario_build = build["estaticos"]["questionario_elegibilidade"]
    questionario_motor = questionario_elegibilidade()
    assert [p["id"] for p in questionario_build["perguntas"]] == [
        p["id"] for p in questionario_motor["perguntas"]
    ]
    for p_build, p_motor in zip(
        questionario_build["perguntas"], questionario_motor["perguntas"]
    ):
        assert p_build["texto_html"] == _md_para_html(p_motor["texto"])
        assert p_build["depende_de"] == p_motor["depende_de"]
    assert questionario_build["disclaimer_html"] == _md_para_html(
        questionario_motor["disclaimer"]
    )


def test_tabela_de_conclusoes_e_exaustiva_e_bate_com_o_motor(build):
    questionario = build["estaticos"]["questionario_elegibilidade"]
    tabela = questionario["tabela"]
    conclusoes = questionario["conclusoes"]
    combinacoes = combinacoes_respostas_elegibilidade()

    assert set(tabela) == {chave for chave, _ in combinacoes}
    assert set(tabela.values()) == set(range(len(conclusoes))), (
        "índices de conclusão com buracos ou sobras"
    )

    for chave, respostas in combinacoes:
        _, md = conclusao_elegibilidade_markdown(respostas)
        assert _md_para_html(md) in conclusoes[tabela[chave]], (
            f"conclusão divergente para a chave {chave}"
        )
