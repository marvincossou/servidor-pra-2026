"""Perguntas frequentes do servidor sobre a PRA 2026.

Cada pergunta tem um "status":
- "documentado": o conteúdo está fundamentado na Resolução SME nº 561/2026
  e pode ser exibido no app.
- "operacional": conteúdo fundamentado em prática operacional confirmada
  (folha de pagamento/CTRH), mas que NÃO está escrito na Resolução. É
  exibido no app, sempre orientando o canal oficial (CTRH e/ou e-mail
  institucional) para o detalhamento do caso, e nunca cita a Resolução
  como fonte dessa regra.
- "pendente_ctrh": pergunta real do servidor cuja resposta NÃO está na
  Resolução (ou depende de circulares/portarias externas ainda não
  incorporadas). O texto é honesto (orienta o canal oficial, não inventa
  regra) mas só deve ser exibido no app depois de validado com a CTRH.
  `faq_visivel()` já filtra essas entradas por padrão.
"""

FAQ: list[dict] = [
    {
        "pergunta": "Trabalhei em mais de uma escola em 2026. E agora?",
        "resposta": (
            "O valor final é calculado por lotação: para cada unidade/etapa "
            "em que você atuou, a nota daquela modalidade é multiplicada pela "
            "fração de carga horária dedicada a ela. Busque cada escola "
            "neste painel para verificar a elegibilidade coletiva e os "
            "indicadores de cada uma."
        ),
        "status": "documentado",
    },
    {
        "pergunta": "Dou aula em mais de uma etapa na mesma escola. Como funciona?",
        "resposta": (
            "Sua nota final é calculada de forma **proporcional à carga "
            "horária** dedicada a cada etapa/modalidade (Art. 16, §1º). O "
            "detalhamento da sua carga horária será informado pelo e-mail "
            "institucional."
        ),
        "status": "documentado",
    },
    {
        "pergunta": "Posso receber a PRA e o Acordo de Resultados (AR) juntos?",
        "resposta": (
            "Não. O Art. 7º, III exclui expressamente quem já é elegível ao "
            "Acordo de Resultados — cada servidor recebe apenas **um** dos dois."
        ),
        "status": "documentado",
    },
    {
        "pergunta": "Fui Diretor IV em 2026. Isso muda algo na minha elegibilidade?",
        "resposta": (
            "Sim: além dos critérios gerais do Art. 7º, quem ocupou o cargo "
            "de Diretor IV em qualquer período de 2026 não pode ter tido "
            "resultado insatisfatório na última avaliação do Programa de "
            "Avaliação Periódica de Desempenho e Competências para Gestores "
            "das Unidades Escolares (Portaria E/CTRH nº 21/2026)."
        ),
        "status": "documentado",
    },
    {
        "pergunta": "Estive de licença/afastado em 2026. Isso muda algo no meu cálculo?",
        "resposta": (
            "O Art. 8º, III diz apenas que 'ter apresentado falta em 2026' "
            "tira o direito à PRA, sem detalhar quantidade, tipo ou se é "
            "cumulativo. Este painel não tem seu registro funcional — "
            "consulte a CTRH da sua CRE ou aguarde o detalhamento pelo "
            "e-mail institucional."
        ),
        "status": "pendente_ctrh",
    },
    {
        "pergunta": "Quando o pagamento da PRA será feito?",
        "resposta": (
            "A data de pagamento depende de disponibilidade orçamentária "
            "(Art. 2º) e não é definida por este painel. Acompanhe o e-mail "
            "institucional e os canais oficiais da SME."
        ),
        "status": "pendente_ctrh",
    },
    {
        "pergunta": "Não concordo com meu enquadramento. Como contestar?",
        "resposta": (
            "Procure a direção da sua escola ou a CTRH da sua CRE pelos "
            "canais oficiais para verificar seu caso. Casos omissos são "
            "decididos pela Comissão de Premiação por Resultados de "
            "Aprendizagem (Art. 18)."
        ),
        "status": "pendente_ctrh",
    },
]


def faq_visivel() -> list[dict]:
    """Perguntas já validadas e prontas para exibição no app."""
    return [item for item in FAQ if item["status"] in ("documentado", "operacional")]
