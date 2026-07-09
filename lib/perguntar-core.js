// Lógica compartilhada da busca por IA (usada tanto pela Netlify Function em
// netlify/functions/perguntar.js quanto pelo servidor autônomo em
// server/server.js). Responde perguntas em linguagem natural sobre a PRA
// 2026 usando a API da Groq (tier gratuito), com base SOMENTE nos documentos
// de busca.json (fonte única: src/busca_legislacao.py) — nunca inventa
// conteúdo próprio.

const PADRAO_VALOR_MONETARIO = /R\$\s*\d/;
const TAMANHO_MAXIMO_PERGUNTA = 300;
const TAMANHO_MAXIMO_CONTEXTO_UNIDADE = 2000;

function montarPromptSistema(documentos, contextoUnidade) {
  const trechos = documentos.map((doc) => `### ${doc.titulo}\n${doc.texto}`).join("\n\n");

  const blocoContexto = contextoUnidade
    ? `\n\nContexto da escola e do cargo do servidor que está perguntando (use isso para personalizar a resposta; é o mesmo texto que o painel já mostra para o caso dele — não precisa citar isso como documento, mas pode citar os documentos gerais quando também se aplicarem):\n\nEscola: ${contextoUnidade.escola}\n\n${contextoUnidade.explicacao_do_caso}`
    : "";

  return `Você é um assistente que explica as regras da Premiação por Resultados de Aprendizagem (PRA) 2026 da SME-Rio (Resolução SME nº 561/2026), com base EXCLUSIVAMENTE nos trechos abaixo${contextoUnidade ? " e no contexto da escola/cargo do servidor, quando fornecido" : ""}.

Regras obrigatórias:
- Responda sempre em português, de forma direta e simples. Não comece com saudações genéricas ("Olá!", "Claro, posso ajudar!") — vá direto à resposta.
- Toda informação que você der precisa citar o título do documento de origem, entre parênteses. Exemplo: "(Fonte: Tenho direito à PRA?)".
- Se a resposta não estiver claramente nos trechos fornecidos, diga isso explicitamente. Nunca invente uma regra que não esteja nos trechos. Não sugira contato com a CTRH, com outros setores ou com canais externos — apenas informe que essa informação não está disponível neste painel.
- Se o servidor comparar o caso dele com o de um colega (ex.: "fulano recebeu e eu não"), não tente adivinhar o motivo da diferença — apenas explique os critérios de elegibilidade que se aplicam.
- Nunca informe valores em reais (R$) nem metas numéricas de indicadores por escola — esse painel não trabalha com esses dados.

Trechos disponíveis:

${trechos}${blocoContexto}`;
}

function validarContextoUnidade(bruto) {
  if (!bruto || typeof bruto !== "object") return null;
  const { escola, explicacao_do_caso: explicacaoDoCaso } = bruto;
  if (typeof escola !== "string" || typeof explicacaoDoCaso !== "string") return null;
  if (!escola.trim() || !explicacaoDoCaso.trim()) return null;
  return {
    escola: escola.slice(0, TAMANHO_MAXIMO_CONTEXTO_UNIDADE),
    explicacao_do_caso: explicacaoDoCaso.slice(0, TAMANHO_MAXIMO_CONTEXTO_UNIDADE),
  };
}

// `obterDocumentos` é injetado por quem chama: no Netlify busca via HTTP no
// próprio deploy (com cache em memória do processo); no servidor autônomo lê
// o busca.json direto do disco. Mantém a lógica de IA em um único lugar.
async function responderPergunta({ pergunta, contextoUnidadeBruto, obterDocumentos }) {
  if (typeof pergunta !== "string" || !pergunta.trim() || pergunta.length > TAMANHO_MAXIMO_PERGUNTA) {
    return { statusCode: 400, corpo: { erro: "Pergunta inválida." } };
  }

  const contextoUnidade = validarContextoUnidade(contextoUnidadeBruto);

  if (!process.env.GROQ_API_KEY) {
    return { statusCode: 503, corpo: { erro: "Recurso de IA não está configurado neste momento." } };
  }

  let documentos;
  try {
    documentos = await obterDocumentos();
  } catch {
    return { statusCode: 502, corpo: { erro: "Não foi possível carregar a base de documentos." } };
  }

  let respostaGroq;
  try {
    respostaGroq = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: process.env.GROQ_MODEL || "llama-3.3-70b-versatile",
        messages: [
          { role: "system", content: montarPromptSistema(documentos, contextoUnidade) },
          { role: "user", content: pergunta },
        ],
        temperature: 0.2,
        max_tokens: 500,
      }),
    });
  } catch {
    return { statusCode: 502, corpo: { erro: "Não foi possível falar com o serviço de IA agora." } };
  }

  if (!respostaGroq.ok) {
    return { statusCode: 502, corpo: { erro: "Não foi possível gerar uma resposta agora." } };
  }

  const dados = await respostaGroq.json();
  const resposta = dados.choices?.[0]?.message?.content?.trim();

  if (!resposta) {
    return { statusCode: 502, corpo: { erro: "O serviço de IA não devolveu uma resposta." } };
  }

  if (PADRAO_VALOR_MONETARIO.test(resposta)) {
    return { statusCode: 502, corpo: { erro: "Resposta bloqueada por guarda-corpo interno." } };
  }

  return { statusCode: 200, corpo: { resposta } };
}

module.exports = { montarPromptSistema, validarContextoUnidade, responderPergunta, TAMANHO_MAXIMO_PERGUNTA };
