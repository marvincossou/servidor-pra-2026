"""Textos fixos de interface (não dependem da unidade escolhida).

Fonte única usada por `scripts/build_pwa.py` (gera a versão PWA estática),
para manter os textos consistentes em um único lugar.
"""

TITULO_PAGINA = "Premiação por Resultado de Aprendizagem 2026"

INTRO = (
    "Este painel **explica as regras** da sua Premiação por Resultados de "
    "Aprendizagem (PRA) 2026, de acordo com a unidade onde você está "
    "lotado — ele **não mostra valores** já calculados nem as metas "
    "numéricas reais da sua escola."
)

AVISO_ESCOPO_TITULO = "ℹ️ O que este painel mostra (e o que não mostra)"
AVISO_ESCOPO = (
    "- Mostra apenas a **metodologia** aplicável ao seu cargo e à sua "
    "unidade — não mostra valores numéricos já calculados de premiação, "
    "nem as metas reais de cada indicador da sua escola (elas estão nos "
    "Anexos da Resolução).\n"
    "- **Não é possível receber a PRA e o Acordo de Resultados (AR) ao "
    "mesmo tempo.** Para cada servidor, o pagamento será sempre "
    "referente a **um dos dois** — nunca os dois juntos.\n"
    "- O texto da Resolução SME nº 561/2026 tem pontos ambíguos ou "
    "incompletos. Este painel sinaliza esses pontos na seção "
    "**Transparência sobre o texto da norma**, em vez de tentar adivinhar "
    "a regra que falta."
)

ERRO_CARREGAMENTO_BASE = (
    "😕 Não foi possível carregar a base de unidades. Tente novamente "
    "mais tarde."
)

BUSCA_LABEL = "Busque sua unidade por designação, nome da escola, sigla ou setor"
BUSCA_PLACEHOLDER = "Ex.: 1010001, 10.10.001, Vicente Licínio, E/1ª CRE..."

BUSCA_DICA_VAZIA = (
    "Digite parte do **nome da escola** (ex.: Vicente Licínio), o "
    "**código de designação** (ex.: 10.10.001) ou a **sigla**. "
    "Busque a unidade onde você está lotado **em 2026**."
)

BUSCA_SEM_RESULTADO = (
    "Nenhuma unidade encontrada para esse termo de busca. Tente "
    "digitar só uma palavra do nome, ou o código sem pontos."
)

BUSCA_ASSUNTO_LABEL = "Buscar um assunto sobre a PRA (ex.: IDERio, tenho direito, falta, fator geral)"
BUSCA_ASSUNTO_PLACEHOLDER = "Ex.: tenho direito, o que é IDERio, falta conta contra mim..."

BUSCA_ASSUNTO_DICA_VAZIA = (
    "Digite sua pergunta sobre a PRA (ex.: **tenho direito**, **o que é "
    "IDERio**, **o que conta como falta**) e clique em **Buscar resposta**."
)

BOTAO_PERGUNTAR_IA = "Buscar resposta"
IA_CARREGANDO = "Consultando a IA…"
IA_DISCLAIMER = (
    "⚠️ Resposta gerada por IA a partir dos textos deste painel — pode conter erros."
)
IA_ERRO = (
    "😕 Não foi possível obter uma resposta da IA agora. Tente novamente mais "
    "tarde."
)

SEM_ETAPAS_REGENCIA = (
    "Não há etapas/modalidades de regência identificadas para esta "
    "unidade. Selecione 'Estou fora de sala de aula'."
)

RODAPE_FONTE = "Fonte: Resolução SME nº 561/2026 (PRA 2026)."
