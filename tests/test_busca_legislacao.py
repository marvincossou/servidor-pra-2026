"""Testes do índice de documentos para a busca por assunto (src/busca_legislacao.py)."""

import re

from src.busca_legislacao import documentos_busca
from src.faq import FAQ, faq_visivel
from src.regras_pra_2026 import GLOSSARIO, INDICADORES, PENDENCIAS_VERIFICACAO

PADRAO_VALOR_MONETARIO = re.compile(r"R\$\s*\d")


def test_ids_sao_unicos():
    documentos = documentos_busca()
    ids = [doc["id"] for doc in documentos]
    assert len(ids) == len(set(ids))


def test_cobre_todo_o_glossario():
    documentos = documentos_busca()
    titulos = {doc["titulo"] for doc in documentos}
    for sigla in GLOSSARIO:
        assert sigla in titulos


def test_cobre_todos_os_indicadores():
    documentos = documentos_busca()
    titulos = {doc["titulo"] for doc in documentos}
    for numero in INDICADORES:
        assert f"Indicador {numero}" in titulos


def test_cobre_todas_as_pendencias_de_verificacao():
    documentos = documentos_busca()
    titulos = {doc["titulo"] for doc in documentos}
    for item in PENDENCIAS_VERIFICACAO:
        assert item["titulo"] in titulos


def test_cobre_o_faq_visivel():
    documentos = documentos_busca()
    titulos = {doc["titulo"] for doc in documentos}
    for item in faq_visivel():
        assert item["pergunta"] in titulos


def test_nao_expoe_faq_pendente_ctrh():
    documentos = documentos_busca()
    titulos = {doc["titulo"] for doc in documentos}
    perguntas_pendentes = {item["pergunta"] for item in FAQ if item["status"] == "pendente_ctrh"}
    assert not (titulos & perguntas_pendentes)


def test_nenhum_documento_contem_valor_monetario():
    for doc in documentos_busca():
        assert not PADRAO_VALOR_MONETARIO.search(doc["texto"])
        assert not PADRAO_VALOR_MONETARIO.search(doc["titulo"])


def test_documento_cargo_especifico_nao_depende_de_unidade():
    documentos = {doc["id"]: doc for doc in documentos_busca()}
    assert "cargo-especifico" in documentos
    assert "escola" in documentos["cargo-especifico"]["texto"].lower()
