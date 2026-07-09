// Servidor autônomo (sem dependências externas) para auto-hospedar a PWA da
// PRA 2026 fora do Netlify — pensado para rodar atrás do Tailscale Funnel no
// servidor de casa do usuário. Serve os arquivos estáticos de dist/ (gerados
// por scripts/build_pwa.py) e a rota POST /api/perguntar, reaproveitando a
// mesma lógica de IA de lib/perguntar-core.js usada pela Netlify Function.
//
// Uso: GROQ_API_KEY=... node server/server.js
// Variáveis de ambiente: GROQ_API_KEY (obrigatória), GROQ_MODEL (opcional),
// PORT (padrão 8787), DIST_DIR (padrão ../dist relativo a este arquivo).

const http = require("node:http");
const fs = require("node:fs/promises");
const path = require("node:path");

const { responderPergunta } = require("../lib/perguntar-core");

const PORTA = Number(process.env.PORT) || 8787;
const PASTA_DIST = path.resolve(__dirname, process.env.DIST_DIR || "../dist");
const TAMANHO_MAXIMO_CORPO = 10_000;

const TIPOS_MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".png": "image/png",
  ".pdf": "application/pdf",
  ".ico": "image/x-icon",
};

let documentosCache = null;

async function obterDocumentos() {
  if (documentosCache) return documentosCache;
  const bruto = await fs.readFile(path.join(PASTA_DIST, "dados", "busca.json"), "utf-8");
  const { documentos } = JSON.parse(bruto);
  documentosCache = documentos;
  return documentos;
}

async function lerCorpo(req) {
  const partes = [];
  let tamanho = 0;
  for await (const parte of req) {
    tamanho += parte.length;
    if (tamanho > TAMANHO_MAXIMO_CORPO) throw new Error("Corpo da requisição muito grande.");
    partes.push(parte);
  }
  return Buffer.concat(partes).toString("utf-8");
}

async function tratarPerguntar(req, res) {
  let pergunta;
  let contextoUnidadeBruto;
  try {
    const corpo = await lerCorpo(req);
    ({ pergunta, contexto_unidade: contextoUnidadeBruto } = JSON.parse(corpo || "{}"));
  } catch {
    res.writeHead(400, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ erro: "Corpo da requisição inválido." }));
    return;
  }

  const { statusCode, corpo } = await responderPergunta({ pergunta, contextoUnidadeBruto, obterDocumentos });
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(corpo));
}

async function tratarEstatico(req, res) {
  const urlPath = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
  const caminhoRelativo = urlPath === "/" ? "index.html" : urlPath.replace(/^\/+/, "");
  const caminhoAbsoluto = path.join(PASTA_DIST, caminhoRelativo);

  // Nunca servir arquivo fora de dist/ (ex.: "../../etc/passwd" na URL).
  if (!caminhoAbsoluto.startsWith(PASTA_DIST)) {
    res.writeHead(400);
    res.end("Requisição inválida.");
    return;
  }

  try {
    const conteudo = await fs.readFile(caminhoAbsoluto);
    const extensao = path.extname(caminhoAbsoluto);
    const headers = { "Content-Type": TIPOS_MIME[extensao] || "application/octet-stream" };
    if (urlPath === "/sw.js" || urlPath.startsWith("/dados/")) {
      headers["Cache-Control"] = "no-cache";
    }
    res.writeHead(200, headers);
    res.end(conteudo);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Não encontrado.");
  }
}

const servidor = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/api/perguntar") {
    tratarPerguntar(req, res).catch(() => {
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ erro: "Erro interno." }));
    });
    return;
  }

  if (req.method === "GET" || req.method === "HEAD") {
    tratarEstatico(req, res).catch(() => {
      res.writeHead(500);
      res.end("Erro interno.");
    });
    return;
  }

  res.writeHead(405);
  res.end("Método não permitido.");
});

servidor.listen(PORTA, "127.0.0.1", () => {
  console.log(`PRA 2026 PWA rodando em http://127.0.0.1:${PORTA} (servindo ${PASTA_DIST})`);
});
