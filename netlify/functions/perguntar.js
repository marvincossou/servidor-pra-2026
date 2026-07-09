// Netlify Function: responde perguntas em linguagem natural sobre a PRA 2026,
// usando a API da Groq (tier gratuito) com base SOMENTE nos documentos de
// `dist/dados/busca.json` (mesmo índice usado pela busca por palavra-chave em
// pwa/js/app.js). Fonte única dos documentos continua sendo
// `src/busca_legislacao.py` — esta function nunca inventa conteúdo próprio.

const PADRAO_VALOR_MONETARIO = /R\$\s*\d/;
const TAMANHO_MAXIMO_PERGUNTA = 300;

function montarPromptSistema(documentos) {
  const trechos = documentos.map((doc) => `### ${doc.titulo}\n${doc.texto}`).join("\n\n");
  return `Você é um assistente que explica as regras da Premiação por Resultados de Aprendizagem (PRA) 2026 da SME-Rio (Resolução SME nº 561/2026), com base EXCLUSIVAMENTE nos trechos abaixo.

Regras obrigatórias:
- Responda sempre em português, de forma direta e simples.
- Toda informação que você der precisa citar o título do documento de origem, entre parênteses. Exemplo: "(Fonte: Tenho direito à PRA?)".
- Se a resposta não estiver claramente nos trechos fornecidos, diga isso explicitamente e oriente o servidor a consultar a CTRH (Comissão Técnica de Recursos Humanos) da sua CRE ou os canais oficiais da SME. Nunca invente uma regra que não esteja nos trechos.
- Nunca informe valores em reais (R$) nem metas numéricas de indicadores por escola — esse painel não trabalha com esses dados.

Trechos disponíveis:

${trechos}`;
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: JSON.stringify({ erro: "Método não permitido." }) };
  }

  let pergunta;
  try {
    ({ pergunta } = JSON.parse(event.body || "{}"));
  } catch {
    return { statusCode: 400, body: JSON.stringify({ erro: "Corpo da requisição inválido." }) };
  }

  if (typeof pergunta !== "string" || !pergunta.trim() || pergunta.length > TAMANHO_MAXIMO_PERGUNTA) {
    return { statusCode: 400, body: JSON.stringify({ erro: "Pergunta inválida." }) };
  }

  if (!process.env.GROQ_API_KEY) {
    return { statusCode: 503, body: JSON.stringify({ erro: "Recurso de IA não está configurado neste momento." }) };
  }

  const origem = new URL(event.rawUrl || `https://${event.headers.host}`).origin;

  let documentos;
  try {
    const respostaBusca = await fetch(`${origem}/dados/busca.json`);
    if (!respostaBusca.ok) throw new Error("busca.json indisponível");
    ({ documentos } = await respostaBusca.json());
  } catch {
    return { statusCode: 502, body: JSON.stringify({ erro: "Não foi possível carregar a base de documentos." }) };
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
          { role: "system", content: montarPromptSistema(documentos) },
          { role: "user", content: pergunta },
        ],
        temperature: 0.2,
        max_tokens: 500,
      }),
    });
  } catch {
    return { statusCode: 502, body: JSON.stringify({ erro: "Não foi possível falar com o serviço de IA agora." }) };
  }

  if (!respostaGroq.ok) {
    return { statusCode: 502, body: JSON.stringify({ erro: "Não foi possível gerar uma resposta agora." }) };
  }

  const dados = await respostaGroq.json();
  const resposta = dados.choices?.[0]?.message?.content?.trim();

  if (!resposta) {
    return { statusCode: 502, body: JSON.stringify({ erro: "O serviço de IA não devolveu uma resposta." }) };
  }

  if (PADRAO_VALOR_MONETARIO.test(resposta)) {
    return { statusCode: 502, body: JSON.stringify({ erro: "Resposta bloqueada por guarda-corpo interno." }) };
  }

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resposta }),
  };
};
