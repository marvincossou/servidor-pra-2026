// Service worker da PWA PRA 2026.
// __VERSAO__ é substituído pelo hash do conteúdo em scripts/build_pwa.py —
// qualquer mudança nos dados ou no app shell gera uma versão nova de cache.
const CACHE = "pra2026-__VERSAO__";
const PREFIXO_CACHE = "pra2026-";

const ARQUIVOS_PRECACHE = [
  "./",
  "./index.html",
  "./css/app.css",
  "./js/app.js",
  "./manifest.webmanifest",
  "./assets/logo_sme_rio.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
  "./dados/unidades.json",
  "./dados/perfis.json",
  "./dados/estaticos.json",
  "./dados/busca.json",
];

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ARQUIVOS_PRECACHE))
  );
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches
      .keys()
      .then((chaves) =>
        Promise.all(
          chaves
            .filter((chave) => chave.startsWith(PREFIXO_CACHE) && chave !== CACHE)
            .map((chave) => caches.delete(chave))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evento) => {
  if (evento.request.method !== "GET") return;

  evento.respondWith(
    caches.match(evento.request).then((respostaCache) => {
      if (respostaCache) return respostaCache;
      return fetch(evento.request).catch(() => {
        if (evento.request.mode === "navigate") {
          return caches.match("./index.html");
        }
        return Response.error();
      });
    })
  );
});

self.addEventListener("message", (evento) => {
  if (evento.data && evento.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});
