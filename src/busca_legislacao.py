"""Índice de documentos para a busca por assunto na legislação da PRA 2026.

Reúne, em uma lista de documentos pequenos e independentes de unidade
(glossário, indicadores, pendências de verificação, elegibilidade, fórmula
final, FAQ visível), o conteúdo que a PWA indexa no navegador (TF-IDF sobre
título + texto + sinônimos, calculado em JavaScript — nenhuma chamada de IA
em tempo de execução). Cada documento carrega o texto em markdown; quem gera
o HTML final é `scripts/build_pwa.py`, reaproveitando `_md_para_html`.

Conteúdo que depende do perfil da unidade (Fator Geral, professor por
cargo/etapa) fica fora deste índice — tem seu próprio fluxo (busca por
escola). O documento "cargo-especifico" apenas direciona o servidor para lá.
"""

from src.faq import faq_visivel
from src.regras_pra_2026 import (
    GLOSSARIO,
    INDICADORES,
    PENDENCIAS_VERIFICACAO,
    explicar_elegibilidade,
    explicar_formula_final,
    explicar_nota_indicador,
)

# Termos coloquiais/sinônimos que o servidor pode digitar, por id de documento.
# Não precisa cobrir todo documento — só os que têm vocabulário não-óbvio.
SINONIMOS: dict[str, list[str]] = {
    "glossario-cre": ["regional", "coordenadoria"],
    "glossario-ctrh": ["reclamar", "duvida", "contestar", "rh"],
    "glossario-iderio": ["prova rio", "nota da prova", "avaliacao", "desempenho"],
    "glossario-pd": ["plano de acao", "plano das dimensoes"],
    "glossario-avalia-rj": ["prova do segundo ano", "prova de alfabetizacao"],
    "elegibilidade": [
        "tenho direito",
        "vou receber",
        "quem recebe o premio",
        "quem tem direito",
        "vou ganhar",
        "falta",
        "penalidade",
        "exonerado",
    ],
    "formula-final": ["valor final", "quanto vou receber", "carga horaria", "bonus"],
    "nota-indicador": ["nota", "crescimento esperado", "meta", "como e calculada"],
    "cargo-especifico": [
        "professor",
        "regente",
        "fator geral",
        "meu cargo",
        "diretor",
        "fora de sala de aula",
    ],
}


def _slug(texto: str) -> str:
    return texto.strip().lower().replace(" ", "-").replace("º", "").replace("(", "").replace(")", "")


def documentos_busca() -> list[dict]:
    """Monta os documentos indexáveis para a busca por assunto.

    Cada documento: `{"id", "titulo", "texto" (markdown), "sinonimos"}`.
    """
    documentos: list[dict] = []

    for sigla, definicao in GLOSSARIO.items():
        doc_id = f"glossario-{_slug(sigla)}"
        documentos.append(
            {
                "id": doc_id,
                "titulo": sigla,
                "texto": definicao,
                "sinonimos": SINONIMOS.get(doc_id, []),
            }
        )

    for numero, dados in INDICADORES.items():
        documentos.append(
            {
                "id": f"indicador-{numero.lower()}",
                "titulo": f"Indicador {numero}",
                "texto": dados["descricao"],
                "sinonimos": SINONIMOS.get(f"indicador-{numero.lower()}", []),
            }
        )

    for item in PENDENCIAS_VERIFICACAO:
        doc_id = f"pendencia-{_slug(item['titulo'])}"
        documentos.append(
            {
                "id": doc_id,
                "titulo": item["titulo"],
                "texto": item["texto"],
                "sinonimos": SINONIMOS.get(doc_id, []),
            }
        )

    documentos.append(
        {
            "id": "nota-indicador",
            "titulo": "Como a nota de cada indicador é calculada",
            "texto": explicar_nota_indicador(),
            "sinonimos": SINONIMOS.get("nota-indicador", []),
        }
    )
    documentos.append(
        {
            "id": "elegibilidade",
            "titulo": "Tenho direito à PRA?",
            "texto": explicar_elegibilidade(),
            "sinonimos": SINONIMOS.get("elegibilidade", []),
        }
    )
    documentos.append(
        {
            "id": "formula-final",
            "titulo": "Como o valor final é calculado",
            "texto": explicar_formula_final(),
            "sinonimos": SINONIMOS.get("formula-final", []),
        }
    )

    for i, item in enumerate(faq_visivel()):
        documentos.append(
            {
                "id": f"faq-{i}",
                "titulo": item["pergunta"],
                "texto": item["resposta"],
                "sinonimos": [],
            }
        )

    documentos.append(
        {
            "id": "cargo-especifico",
            "titulo": "Como funciona meu cálculo por cargo (Fator Geral / Professor regente)",
            "texto": (
                "Isso depende do seu cargo **e** da sua escola — o cálculo do "
                "Fator Geral e das regras por cargo/etapa (professor regente, "
                "Agente de Educação Infantil, Orientador de EJA, professor de "
                "Classe Especial/Sala de Recursos) é diferente para cada "
                "unidade. Use a **busca por escola** no topo desta página "
                "para ver a explicação específica do seu caso."
            ),
            "sinonimos": SINONIMOS.get("cargo-especifico", []),
        }
    )

    return documentos
