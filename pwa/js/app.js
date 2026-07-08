(() => {
  "use strict";

  const ETAPAS_BITS = ["AI", "AF", "EI", "EJA", "EE", "UE", "BI"];

  const els = {
    tituloPagina: document.getElementById("titulo-pagina"),
    intro: document.getElementById("intro"),
    avisoEscopoTitulo: document.getElementById("aviso-escopo-titulo"),
    avisoEscopoConteudo: document.getElementById("aviso-escopo-conteudo"),
    erroCarregamento: document.getElementById("erro-carregamento"),
    buscaLabel: document.getElementById("busca-label"),
    buscaInput: document.getElementById("busca-input"),
    buscaDicaVazia: document.getElementById("busca-dica-vazia"),
    buscaSemResultado: document.getElementById("busca-sem-resultado"),
    resultadosLista: document.getElementById("resultados-lista"),
    fichaUnidade: document.getElementById("ficha-unidade"),
    fichaTitulo: document.getElementById("ficha-titulo"),
    metricCre: document.getElementById("metric-cre"),
    metricDesignacao: document.getElementById("metric-designacao"),
    metricTipo: document.getElementById("metric-tipo"),
    chipsEtapas: document.getElementById("chips-etapas"),
    glossarioConteudo: document.getElementById("glossario-conteudo"),
    tabCaso: document.getElementById("tab-caso"),
    tabCalculo: document.getElementById("tab-calculo"),
    tabElegibilidade: document.getElementById("tab-elegibilidade"),
    painelCaso: document.getElementById("painel-caso"),
    painelCalculo: document.getElementById("painel-calculo"),
    painelElegibilidade: document.getElementById("painel-elegibilidade"),
    fieldsetPapel: document.getElementById("fieldset-papel"),
    selectEtapaContainer: document.getElementById("select-etapa-container"),
    selectEtapa: document.getElementById("select-etapa"),
    semEtapasRegencia: document.getElementById("sem-etapas-regencia"),
    conteudoCaso: document.getElementById("conteudo-caso"),
    conteudoNotaIndicador: document.getElementById("conteudo-nota-indicador"),
    conteudoFormulaFinal: document.getElementById("conteudo-formula-final"),
    conteudoElegibilidade: document.getElementById("conteudo-elegibilidade"),
    conteudoAusenciasIntro: document.getElementById("conteudo-ausencias-intro"),
    buscaAusencia: document.getElementById("busca-ausencia"),
    tabelaAusenciasCorpo: document.getElementById("tabela-ausencias-corpo"),
    ausenciasSemResultado: document.getElementById("ausencias-sem-resultado"),
    faqLista: document.getElementById("faq-lista"),
    transparenciaLista: document.getElementById("transparencia-lista"),
    rodapeFonte: document.getElementById("rodape-fonte"),
    rodapeDadosDe: document.getElementById("rodape-dados-de"),
    rodapeInstalar: document.getElementById("rodape-instalar"),
    toast: document.getElementById("toast-atualizacao"),
    toastBtn: document.getElementById("toast-atualizar-btn"),
  };

  let dados = null; // { unidades, perfis, estaticos }
  let unidadeAtual = null; // linha (objeto) da unidade selecionada
  let perfilAtual = null;
  let debounceId = null;
  let debounceAusenciasId = null;

  const REGEX_NAO_ASCII = new RegExp("[^\\x00-\\x7F]", "g");

  // Replica src/dados.py:_normalizar (NFKD + descarte de tudo fora do ASCII),
  // inclusive convertendo "ª"/"º" em "a"/"o" — mesma paridade usada nos
  // testes de build (tests/test_build_pwa.py).
  function normalizar(texto) {
    return String(texto)
      .normalize("NFKD")
      .replace(REGEX_NAO_ASCII, "")
      .toLowerCase()
      .trim();
  }

  async function carregarDados() {
    const [unidades, perfis, estaticos] = await Promise.all([
      fetch("./dados/unidades.json").then((r) => r.json()),
      fetch("./dados/perfis.json").then((r) => r.json()),
      fetch("./dados/estaticos.json").then((r) => r.json()),
    ]);
    return { unidades, perfis: perfis.perfis, estaticos };
  }

  function linhaParaObjeto(colunas, linha) {
    const obj = {};
    colunas.forEach((nome, i) => {
      obj[nome] = linha[i];
    });
    return obj;
  }

  function buscarUnidades(termo) {
    const termoNorm = normalizar(termo);
    if (!termoNorm) return [];

    const { colunas, unidades } = dados.unidades;
    const campos = ["designacao", "designacao_antiga", "denominacao", "sigla"];
    const idx = Object.fromEntries(colunas.map((c, i) => [c, i]));

    const termoSemPontos = termoNorm.replace(/\./g, "");
    const buscarSemPontos = termoSemPontos !== termoNorm;

    const encontrados = [];
    for (const linha of unidades) {
      let bate = campos.some((campo) => normalizar(linha[idx[campo]]).includes(termoNorm));
      if (!bate && buscarSemPontos) {
        bate =
          normalizar(linha[idx.designacao]).includes(termoSemPontos) ||
          normalizar(linha[idx.designacao_antiga]).includes(termoSemPontos);
      }
      if (bate) encontrados.push(linhaParaObjeto(colunas, linha));
    }

    encontrados.sort((a, b) => {
      const creA = a.cre_num ?? Infinity;
      const creB = b.cre_num ?? Infinity;
      if (creA !== creB) return creA - creB;
      return a.denominacao.localeCompare(b.denominacao, "pt-BR");
    });

    return encontrados;
  }

  function renderResultados(lista) {
    els.resultadosLista.innerHTML = "";
    if (lista.length <= 1) {
      els.resultadosLista.hidden = true;
      return;
    }
    els.resultadosLista.hidden = false;
    for (const unidade of lista) {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "resultado-btn";
      btn.textContent = `${unidade.designacao} — ${unidade.denominacao} (${unidade.cre_formatada})`;
      btn.addEventListener("click", () => selecionarUnidade(unidade));
      li.appendChild(btn);
      els.resultadosLista.appendChild(li);
    }
  }

  function chipHtml(codigo, rotulo, icone) {
    const prefixo = icone ? `<span aria-hidden="true">${icone}</span> ` : "";
    return `<span class="chip">${prefixo}${rotulo}</span>`;
  }

  function renderFicha(unidade) {
    perfilAtual = dados.perfis[unidade.perfil_idx];

    els.fichaTitulo.textContent = `${unidade.designacao} — ${unidade.denominacao}`;
    els.metricCre.textContent = unidade.cre_formatada;
    els.metricDesignacao.textContent = unidade.designacao;
    els.metricTipo.textContent = dados.unidades.tipos[unidade.tipo_idx];

    const { etapa_labels: labels, etapa_icons: icons } = dados.estaticos;
    const etapasPresentes = ETAPAS_BITS.filter((e) => perfilAtual.etapas.includes(e));
    els.chipsEtapas.innerHTML = etapasPresentes.length
      ? etapasPresentes.map((e) => chipHtml(e, labels[e], icons[e])).join("")
      : "<em>Nenhuma etapa identificada para esta unidade.</em>";

    renderPainelCaso();

    els.fichaUnidade.hidden = false;
    els.fichaUnidade.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderPainelCaso() {
    const papelRegente = els.fieldsetPapel.querySelector('input[value="regente"]').checked;
    const cargos = perfilAtual.cargos; // já sem GERAL

    if (papelRegente) {
      els.selectEtapaContainer.hidden = cargos.length === 0;
      els.semEtapasRegencia.hidden = cargos.length > 0;
      els.conteudoCaso.innerHTML = "";

      if (cargos.length > 0) {
        const valorAtual = els.selectEtapa.value;
        els.selectEtapa.innerHTML = cargos
          .map(([codigo, rotulo]) => `<option value="${codigo}">${rotulo}</option>`)
          .join("");
        const aindaExiste = cargos.some(([codigo]) => codigo === valorAtual);
        els.selectEtapa.value = aindaExiste ? valorAtual : cargos[0][0];
        els.conteudoCaso.innerHTML = perfilAtual.html.professor[els.selectEtapa.value] || "";
      }
    } else {
      els.selectEtapaContainer.hidden = true;
      els.semEtapasRegencia.hidden = true;
      els.conteudoCaso.innerHTML = perfilAtual.html.fator_geral;
    }
  }

  function ativarTab(tabId) {
    const tabs = [
      [els.tabCaso, els.painelCaso],
      [els.tabCalculo, els.painelCalculo],
      [els.tabElegibilidade, els.painelElegibilidade],
    ];
    for (const [tab, painel] of tabs) {
      const ativo = tab.id === tabId;
      tab.setAttribute("aria-selected", String(ativo));
      painel.hidden = !ativo;
    }
  }

  function configurarTabs() {
    const tabs = [els.tabCaso, els.tabCalculo, els.tabElegibilidade];
    tabs.forEach((tab, i) => {
      tab.addEventListener("click", () => ativarTab(tab.id));
      tab.addEventListener("keydown", (ev) => {
        if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
        ev.preventDefault();
        const proximo = ev.key === "ArrowRight" ? (i + 1) % tabs.length : (i - 1 + tabs.length) % tabs.length;
        tabs[proximo].focus();
        ativarTab(tabs[proximo].id);
      });
    });
  }

  function configurarPainelCaso() {
    els.fieldsetPapel.addEventListener("change", renderPainelCaso);
    els.selectEtapa.addEventListener("change", () => {
      els.conteudoCaso.innerHTML = perfilAtual.html.professor[els.selectEtapa.value] || "";
    });
  }

  function selecionarUnidade(unidade) {
    unidadeAtual = unidade;
    els.resultadosLista.hidden = true;
    renderFicha(unidade);
  }

  function tratarBusca() {
    const termo = els.buscaInput.value;
    els.fichaUnidade.hidden = true;

    if (!termo) {
      els.buscaDicaVazia.hidden = false;
      els.buscaSemResultado.hidden = true;
      els.resultadosLista.hidden = true;
      return;
    }
    els.buscaDicaVazia.hidden = true;

    const resultados = buscarUnidades(termo);
    if (resultados.length === 0) {
      els.buscaSemResultado.hidden = false;
      els.resultadosLista.hidden = true;
      return;
    }
    els.buscaSemResultado.hidden = true;

    if (resultados.length === 1) {
      selecionarUnidade(resultados[0]);
    } else {
      renderResultados(resultados);
    }
  }

  function renderTextosEstaticos() {
    const { textos_ui: t, faq } = dados.estaticos;

    els.tituloPagina.textContent = t.titulo_pagina;
    els.intro.innerHTML = t.intro_html;
    els.avisoEscopoTitulo.textContent = t.aviso_escopo_titulo;
    els.avisoEscopoConteudo.innerHTML = t.aviso_escopo_html;
    els.buscaLabel.textContent = t.busca_label;
    els.buscaInput.placeholder = t.busca_placeholder;
    els.buscaDicaVazia.innerHTML = t.busca_dica_vazia_html;
    els.buscaSemResultado.textContent = t.busca_sem_resultado;
    els.semEtapasRegencia.innerHTML = t.sem_etapas_regencia_html;
    els.rodapeFonte.textContent = t.rodape_fonte;
    els.rodapeDadosDe.textContent = `Dados de ${dados.unidades.dados_de}.`;

    els.glossarioConteudo.innerHTML = dados.estaticos.glossario_html;
    els.conteudoNotaIndicador.innerHTML = dados.estaticos.nota_indicador_html;
    els.conteudoFormulaFinal.innerHTML = dados.estaticos.formula_final_html;
    els.conteudoElegibilidade.innerHTML = dados.estaticos.elegibilidade_html;
    els.conteudoAusenciasIntro.innerHTML = dados.estaticos.ausencias_intro_html;
    els.transparenciaLista.innerHTML = dados.estaticos.pendencias_verificacao_html;
    renderTabelaAusencias("");

    els.faqLista.innerHTML = "";
    for (const item of faq) {
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = item.pergunta;
      const div = document.createElement("div");
      div.className = "conteudo-md";
      div.innerHTML = item.resposta_html;
      details.appendChild(summary);
      details.appendChild(div);
      els.faqLista.appendChild(details);
    }
  }

  function renderTabelaAusencias(termo) {
    const termoNorm = normalizar(termo);
    const linhas = dados.estaticos.ausencias.filter((a) => normalizar(a.descricao).includes(termoNorm));

    els.tabelaAusenciasCorpo.innerHTML = "";
    els.ausenciasSemResultado.hidden = linhas.length > 0;

    for (const a of linhas) {
      const tr = document.createElement("tr");
      const descricao = a.observacoes ? `${a.descricao} (${a.observacoes})` : a.descricao;
      tr.innerHTML = `
        <td>${descricao}</td>
        <td>${a.conta_como_ausencia ? "Sim" : "Não"}</td>
        <td>${a.falta_nao_justificada ? "Sim" : "Não"}</td>
      `;
      els.tabelaAusenciasCorpo.appendChild(tr);
    }
  }

  function mostrarToastAtualizacao(registro) {
    els.toast.hidden = false;
    els.toastBtn.onclick = () => {
      if (registro.waiting) {
        registro.waiting.postMessage({ type: "SKIP_WAITING" });
      }
    };
  }

  function registrarServiceWorker() {
    if (!("serviceWorker" in navigator)) return;
    const base = new URL(".", window.location.href);

    let recarregando = false;
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (recarregando) return;
      recarregando = true;
      window.location.reload();
    });

    navigator.serviceWorker
      .register(new URL("sw.js", base), { scope: base.pathname })
      .then((registro) => {
        if (registro.waiting && navigator.serviceWorker.controller) {
          mostrarToastAtualizacao(registro);
        }
        registro.addEventListener("updatefound", () => {
          const instalando = registro.installing;
          if (!instalando) return;
          instalando.addEventListener("statechange", () => {
            if (instalando.state === "installed" && navigator.serviceWorker.controller) {
              mostrarToastAtualizacao(registro);
            }
          });
        });
      })
      .catch(() => {
        // Falha ao registrar o SW não impede o uso online normal do app.
      });
  }

  function mostrarDicaInstalacaoIOS() {
    const ehIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    const jaInstalado = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
    if (ehIOS && !jaInstalado) {
      els.rodapeInstalar.hidden = false;
      els.rodapeInstalar.textContent =
        "📲 Para instalar: toque em Compartilhar e depois em \"Adicionar à Tela de Início\".";
    }
  }

  async function iniciar() {
    try {
      dados = await carregarDados();
    } catch (erro) {
      els.erroCarregamento.hidden = false;
      els.erroCarregamento.textContent =
        "😕 Não foi possível carregar a base de unidades. Verifique sua conexão e tente novamente.";
      return;
    }

    renderTextosEstaticos();
    configurarTabs();
    configurarPainelCaso();

    els.buscaInput.addEventListener("input", () => {
      clearTimeout(debounceId);
      debounceId = setTimeout(tratarBusca, 150);
    });

    els.buscaAusencia.addEventListener("input", () => {
      clearTimeout(debounceAusenciasId);
      debounceAusenciasId = setTimeout(() => renderTabelaAusencias(els.buscaAusencia.value), 150);
    });

    tratarBusca();
    registrarServiceWorker();
    mostrarDicaInstalacaoIOS();
  }

  iniciar();
})();
