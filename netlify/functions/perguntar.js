// Netlify Function: adaptador fino sobre lib/perguntar-core.js (lógica de IA
// compartilhada com server/server.js, usado no auto-hospedagem alternativa).

const { responderPergunta } = require("../../lib/perguntar-core");

// Cache em memória do processo: containers "quentes" do Netlify reaproveitam
// esta variável entre chamadas, evitando refazer a busca de busca.json a
// cada pergunta. Um novo deploy sempre cria um container novo (cache vazio).
let documentosCache = null;

async function obterDocumentos(origem) {
  if (documentosCache) return documentosCache;
  const respostaBusca = await fetch(`${origem}/dados/busca.json`);
  if (!respostaBusca.ok) throw new Error("busca.json indisponível");
  const { documentos } = await respostaBusca.json();
  documentosCache = documentos;
  return documentos;
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: JSON.stringify({ erro: "Método não permitido." }) };
  }

  let pergunta;
  let contextoUnidadeBruto;
  try {
    ({ pergunta, contexto_unidade: contextoUnidadeBruto } = JSON.parse(event.body || "{}"));
  } catch {
    return { statusCode: 400, body: JSON.stringify({ erro: "Corpo da requisição inválido." }) };
  }

  const origem = new URL(event.rawUrl || `https://${event.headers.host}`).origin;

  const { statusCode, corpo } = await responderPergunta({
    pergunta,
    contextoUnidadeBruto,
    obterDocumentos: () => obterDocumentos(origem),
  });

  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  };
};
