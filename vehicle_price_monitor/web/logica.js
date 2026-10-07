(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var interi = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 });
  var dec2 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var eur = function (n) { return interi.format(Math.round(n)) + " €"; };
  var eurSegno = function (n) { return (n >= 0 ? "+" : "−") + interi.format(Math.abs(Math.round(n))) + " €"; };

  /* 1. Dati e campi ------------------------------------------------------ */
  var D = JSON.parse($("dati").textContent), M = D.modelli;
  var INTERVALLI = { anni: [0, 30], km: [0, 500000], cv: [30, 700], prezzo: [500, 300000] };
  var NOMI = { anni: "Anni", km: "Chilometraggio", cv: "Potenza", cambio: "Cambio", carb: "Carburante", allest: "Allestimento", area: "Zona" };
  var AREE = { "Nord-est": null, "Nord-ovest": "is NO vs NE", "Centro": "is Centro vs NE", "Sud": "is Sud_Isole vs NE", "Isole": "is Sud_Isole vs NE" };
  var RADIO = {
    cambio: [["0", "Manuale"], ["1", "Automatico"]],
    area: Object.keys(AREE).map(function (a) { return [a, a]; })
  };
  var NUMERICI = Object.keys(INTERVALLI);
  var GRUPPO = function (col) {
    if (col === "Anni") return "anni";
    if (col === "Chilometraggio") return "km";
    if (col === "CV") return "cv";
    if (col === "Cambio") return "cambio";
    if (/ vs Benzina$/.test(col)) return "carb";
    if (/ vs base$/.test(col)) return "allest";
    return "area";
  };

  function segmenti(id, opzioni) {
    $("seg-" + id).innerHTML = opzioni.map(function (o) {
      return '<label class="segmento"><input type="radio" name="' + id + '" value="' + o[0] + '"><span>' + o[1] + "</span></label>";
    }).join("");
  }
  segmenti("cambio", RADIO.cambio);
  segmenti("area", RADIO.area);
  $("modello").innerHTML = D.ordine.map(function (n) { return '<option value="' + n + '">' + M[n].titolo + "</option>"; }).join("");

  function aggiungiNumero(contenitore, id, html, unita) {
    var r = INTERVALLI[id];
    contenitore.insertAdjacentHTML("beforeend", html.replace("{input}",
      '<input id="' + id + '" type="number" min="' + r[0] + '" max="' + r[1] + '" step="' + (unita === "anni" ? 1 : "any") + '" inputmode="' +
      (unita === "anni" ? "numeric" : "decimal") + '" aria-describedby="' + id + '-aiuto ' + id + '-err">') +
      '<p class="aiuto" id="' + id + '-aiuto"></p><p class="errore-campo" id="' + id + '-err" hidden></p>');
  }
  document.querySelectorAll("[data-contatore]").forEach(function (c) {
    var id = c.dataset.contatore;
    aggiungiNumero(c, id, '<div class="contatore"><button type="button" data-passo="-1" aria-label="Diminuisci ' + NOMI[id].toLowerCase() +
      '">−</button>{input}<button type="button" data-passo="1" aria-label="Aumenta ' + NOMI[id].toLowerCase() + '">+</button></div>', "anni");
  });
  document.querySelectorAll("[data-numero]").forEach(function (c) {
    var id = c.dataset.numero;
    aggiungiNumero(c, id, '<div class="con-unita">{input}<span class="unita">' + c.dataset.unita + "</span></div>", "num");
  });

  /* 2. Lettura, scrittura, validazione ----------------------------------- */
  function leggi(id) {
    if (RADIO[id] || id === "carb") { var s = document.querySelector('input[name="' + id + '"]:checked'); return s ? s.value : null; }
    return $(id).value;
  }
  function imposta(id, v) {
    if (RADIO[id] || id === "carb") { var r = document.querySelector('input[name="' + id + '"][value="' + v + '"]'); if (r) r.checked = true; }
    else $(id).value = v;
  }
  function errore(id) {
    var v = String($(id).value).trim(), r = INTERVALLI[id];
    if (v === "") return "Inserisci un valore";
    var n = Number(v);
    if (!isFinite(n)) return "Inserisci un numero";
    if (n < r[0] || n > r[1]) return "Inserisci un valore tra " + interi.format(r[0]) + " e " + interi.format(r[1]);
    if (id === "anni" && n % 1 !== 0) return "Inserisci un numero intero";
    return null;
  }
  function mostraErrori(campoModificato) {
    var errati = [];
    NUMERICI.forEach(function (id) {
      var e = errore(id);
      if (e) errati.push(id);
      var giaSegnalato = $(id).getAttribute("aria-invalid") === "true";
      if (campoModificato && campoModificato !== id && !giaSegnalato) return;
      if (e) $(id).setAttribute("aria-invalid", "true"); else $(id).removeAttribute("aria-invalid");
      $(id + "-err").textContent = e || "";
      $(id + "-err").hidden = !e;
    });
    return errati;
  }
  function modelloAttuale() { return M[$("modello").value]; }

  function preparaModello(m, conservaAuto) {
    var allest = conservaAuto ? $("allest").value : null, carb = conservaAuto ? leggi("carb") : null;
    $("allest").innerHTML = Object.keys(m.allestimenti).map(function (a) { return '<option value="' + a + '">' + a + "</option>"; }).join("");
    segmenti("carb", m.carburanti.map(function (c) { return [c, c]; }));
    if (allest && m.allestimenti[allest]) $("allest").value = allest;
    imposta("carb", carb && m.carburanti.indexOf(carb) >= 0 ? carb : m.carburanti[0]);
    $("tipico").textContent = "Valori tipici di " + m.titolo + ": " + m.tipico.anni + " anni, " + interi.format(m.tipico.km) + " km, " + m.tipico.cv + " CV";
    var pillole = [["Annunci", interi.format(m.n)], ["Prezzo medio", eur(m.prezzo_medio)], ["R² lineare", dec2.format(m.r2_lin)],
      ["Errore tipico", "±" + eur(m.rmse_lin)], ["Dati del", m.aggiornato]];
    $("dati-modello").innerHTML = pillole.map(function (p) { return "<li>" + p[0] + " <b>" + p[1] + "</b></li>"; }).join("");
  }
  function valoriTipici(m) {
    imposta("anni", m.tipico.anni); imposta("km", m.tipico.km); imposta("cv", m.tipico.cv); imposta("prezzo", m.tipico.prezzo);
    imposta("cambio", "0"); imposta("area", "Nord-est");
    $("allest").selectedIndex = 0;
  }
  function aggiornaAiuti(m) {
    ["anni", "km", "cv"].forEach(function (id) {
      var o = m.oss[id], n = Number($(id).value);
      var fuori = $(id).value !== "" && isFinite(n) && (n < o[0] || n > o[1]);
      $(id + "-aiuto").textContent = "Valori più comuni: " + interi.format(o[0]) + "–" + interi.format(o[1]) + (fuori ? " · fuori dal campione, stima meno affidabile" : "");
    });
    $("prezzo-aiuto").textContent = "Valori più comuni: " + eur(m.oss.prezzo[0]) + " – " + eur(m.oss.prezzo[1]);
    document.querySelectorAll(".contatore").forEach(function (c) {
      var inp = c.querySelector("input"), n = Number(inp.value);
      c.querySelector('[data-passo="-1"]').disabled = !(n > Number(inp.min));
      c.querySelector('[data-passo="1"]').disabled = !(n < Number(inp.max));
    });
  }

  /* 3. Calcolo e disegno -------------------------------------------------- */
  function calcola(m) {
    var f = { Anni: Number($("anni").value), Chilometraggio: Number($("km").value), CV: Number($("cv").value), Cambio: Number(leggi("cambio")) };
    f["is_" + leggi("carb") + " vs Benzina"] = 1;
    f["is_" + m.allestimenti[$("allest").value] + " vs base"] = 1;
    var colArea = AREE[leggi("area")];
    if (colArea) f[colArea] = 1;
    var gruppi = {}, base = m.intercept, previsto = m.intercept;
    m.cols.forEach(function (c, i) {
      var media = m.medie[c];
      base += m.coef[i] * media;
      previsto += m.coef[i] * (f[c] || 0);
      var g = GRUPPO(c);
      gruppi[g] = (gruppi[g] || 0) + m.coef[i] * ((f[c] || 0) - media);
    });
    return { previsto: previsto, base: base, gruppi: gruppi };
  }
  function descrizione(id) {
    if (id === "anni") return interi.format(Number($("anni").value)) + " anni";
    if (id === "km") return interi.format(Number($("km").value)) + " km";
    if (id === "cv") return interi.format(Number($("cv").value)) + " CV";
    if (id === "cambio") return leggi("cambio") === "1" ? "automatico" : "manuale";
    if (id === "carb") return leggi("carb");
    if (id === "allest") return $("allest").value;
    return leggi("area");
  }

  var precedente = null;
  function disegnaKpi(m, r, prezzo) {
    var delta = r.previsto - prezzo, soglia = m.rmse_lin;
    var frazione = Math.max(0, Math.min(1, 0.5 + delta / (4 * soglia)));
    $("arco").setAttribute("stroke-dasharray", (frazione * 100).toFixed(2) + " 100");
    $("arco").classList.toggle("basso", delta < 0);
    $("valore-grande").textContent = eurSegno(delta);
    var tipo = delta > soglia ? ["bev", "Sotto prezzata: buon affare"] : delta < -soglia ? ["altro", "Sovra prezzata"] : ["neutro", "Prezzo in linea con il mercato"];
    $("verdetto").className = "verdetto " + tipo[0];
    $("verdetto").textContent = tipo[1];
    $("delta").textContent = "Stimato " + eur(r.previsto) + " · richiesto " + eur(prezzo);
    $("confronto").innerHTML = '<span class="tacca"></span>Errore tipico del modello: ±' + eur(soglia) + ". Una differenza più piccola dell'errore non è significativa.";
    $("mob-p").textContent = eurSegno(delta);
    $("mob-delta").textContent = "stima " + eur(r.previsto);
  }

  function passoAsse(intervallo) {
    var grezzo = intervallo / 3, ordine = Math.pow(10, Math.floor(Math.log10(grezzo))), f = grezzo / ordine;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * ordine;
  }
  function disegnaCascata(m, r, prezzo) {
    var voci = Object.keys(r.gruppi).map(function (id) { return { id: id, v: r.gruppi[id] }; })
      .sort(function (a, b) { return Math.abs(b.v) - Math.abs(a.v); });
    var s = r.base, punti = [r.base, prezzo];
    voci.forEach(function (x) { x.da = s; s += x.v; x.a = s; punti.push(x.a); });
    var passo = passoAsse(Math.max.apply(null, punti) - Math.min.apply(null, punti) || 1000);
    var lo = Math.floor((Math.min.apply(null, punti) - passo * 0.3) / passo) * passo;
    var hi = Math.ceil((Math.max.apply(null, punti) + passo * 0.3) / passo) * passo;
    var X = function (p) { return ((p - lo) / (hi - lo) * 100).toFixed(2) + "%"; };

    var html = '<div class="riga estremo" role="listitem"><span class="nome"><b>Auto media</b><span>riferimento del modello</span></span>' +
      '<span class="pista"><span class="segno" style="left:' + X(r.base) + '"></span></span><span class="val">' + eur(r.base) + "</span></div>";
    voci.forEach(function (x) {
      var su = x.a >= x.da;
      html += '<div class="riga" role="listitem"><span class="nome"><b>' + NOMI[x.id] + "</b><span>" + descrizione(x.id) + "</span></span>" +
        '<span class="pista"><span class="seg ' + (su ? "su" : "giu") + '" style="left:' + X(Math.min(x.da, x.a)) + ";width:calc(" +
        X(Math.max(x.da, x.a)) + " - " + X(Math.min(x.da, x.a)) + ')"></span></span>' +
        '<span class="val ' + (su ? "su" : "giu") + '">' + (su ? "▲ " : "▼ ") + interi.format(Math.abs(Math.round(x.v))) +
        '<span class="solo-lettori"> euro ' + (su ? "in più" : "in meno") + "</span></span></div>";
    });
    html += '<div class="riga estremo finale" role="listitem"><span class="nome"><b>Prezzo stimato</b><span>questa auto</span></span>' +
      '<span class="pista"><span class="segno" style="left:' + X(r.previsto) + '"></span>' +
      '<span class="segno" style="left:' + X(prezzo) + ';background:var(--arancio)" title="Prezzo richiesto"></span></span><span class="val">' + eur(r.previsto) + "</span></div>";
    $("cascata").innerHTML = html;

    var tacche = "";
    for (var v = lo; v <= hi + 1e-6; v += passo) tacche += '<span style="left:' + X(v) + '">' + (v / 1000).toLocaleString("it-IT", { maximumFractionDigits: 1 }) + "k</span>";
    $("tacche").innerHTML = tacche;
    $("sottotitolo-cascata").textContent = "Dall'auto media di " + m.titolo + " (" + eur(r.base) + ") a questa: quanto pesa ogni caratteristica sul prezzo, in euro. Il segno arancio è il prezzo richiesto.";
  }

  function aggiorna(campoModificato) {
    var m = modelloAttuale();
    aggiornaAiuti(m);
    var errati = mostraErrori(campoModificato), bloccato = errati.length > 0;
    $("blocco-risultato").classList.toggle("inattivo", bloccato);
    $("cascata").classList.toggle("inattivo", bloccato);
    $("avviso").innerHTML = bloccato ? '<p class="avviso" role="alert">Correggi ' + (errati.length === 1 ? "il campo evidenziato" :
      "i " + errati.length + " campi evidenziati") + ": la stima si riferisce all'ultimo valore valido.</p>" : "";
    if (bloccato) return;
    var prezzo = Number($("prezzo").value), r = calcola(m);
    disegnaKpi(m, r, prezzo);
    disegnaCascata(m, r, prezzo);
    precedente = r.previsto;
    salvaNelLink();
  }

  /* 4. Stato nel link ----------------------------------------------------- */
  var CAMPI = ["modello", "allest", "carb", "cambio", "anni", "km", "cv", "prezzo", "area"];
  function salvaNelLink() {
    var q = new URLSearchParams();
    CAMPI.forEach(function (id) { q.set(id, leggi(id)); });
    try { history.replaceState(null, "", "#" + q.toString()); } catch (e) { /* file:// in alcuni browser */ }
  }
  function leggiDalLink() {
    var q = new URLSearchParams(location.hash.slice(1));
    if (!q.has("modello") || !M[q.get("modello")]) return false;
    $("modello").value = q.get("modello");
    var m = modelloAttuale();
    preparaModello(m, false);
    valoriTipici(m);
    if (m.allestimenti[q.get("allest")]) $("allest").value = q.get("allest");
    ["carb", "cambio", "area"].forEach(function (id) { if (q.has(id)) imposta(id, q.get(id)); });
    NUMERICI.forEach(function (id) { if (q.has(id) && q.get(id) !== "") $(id).value = q.get(id); });
    return true;
  }

  /* 5. Eventi -------------------------------------------------------------- */
  $("profilo").addEventListener("input", function (e) {
    var id = e.target.id || e.target.name;
    if (id === "modello") { var m = modelloAttuale(); preparaModello(m, true); valoriTipici(m); }
    aggiorna(id);
  });
  $("profilo").addEventListener("submit", function (e) { e.preventDefault(); });
  $("profilo").addEventListener("click", function (e) {
    var b = e.target.closest("[data-passo]");
    if (!b) return;
    var inp = b.parentNode.querySelector("input");
    var n = Math.round(Number(inp.value) || 0) + Number(b.dataset.passo);
    inp.value = Math.min(Number(inp.max), Math.max(Number(inp.min), n));
    aggiorna(inp.id);
  });
  $("ripristina").addEventListener("click", function () { valoriTipici(modelloAttuale()); aggiorna(); });
  $("copia").addEventListener("click", function () {
    var b = $("copia"), testo = b.textContent;
    var fatto = function () { b.textContent = "Link copiato"; setTimeout(function () { b.textContent = testo; }, 1600); };
    try { navigator.clipboard.writeText(location.href).then(fatto, function () { window.prompt("Copia il link", location.href); }); }
    catch (e) { window.prompt("Copia il link", location.href); }
  });

  /* Tabella delle migliori offerte (in fondo alla pagina) */
  function tabellaOfferte() {
    var m = M[$("o-modello").value], corpo = $("top-corpo");
    corpo.replaceChildren();
    if (!m.top.length) {
      var tr0 = document.createElement("tr"), td0 = document.createElement("td");
      td0.colSpan = 10; td0.textContent = "Nessuna offerta disponibile (modello non ancora addestrato?)";
      tr0.append(td0); corpo.append(tr0);
      return;
    }
    m.top.forEach(function (o) {
      var tr = document.createElement("tr");
      [[dec2.format(o.indice), "n"], [eur(o.prezzo), "n"], [eur(o.previsto), "n"], ["+" + eur(o.previsto - o.prezzo), "n su"], [o.anni, "n"],
        [interi.format(o.km), "n"], [o.dist, "n"], [o.allest, ""], [o.carb, ""]].forEach(function (c) {
        var td = document.createElement("td"); td.textContent = c[0]; if (c[1]) td.className = c[1]; tr.append(td);
      });
      var a = document.createElement("a"), td = document.createElement("td");
      a.href = o.link; a.target = "_blank"; a.rel = "noopener"; a.textContent = "Apri"; td.append(a); tr.append(td);
      corpo.append(tr);
    });
  }
  $("o-modello").innerHTML = $("modello").innerHTML;
  $("o-modello").addEventListener("change", tabellaOfferte);

  /* Avvio */
  if (!leggiDalLink()) {
    var m0 = modelloAttuale();
    preparaModello(m0, false);
    valoriTipici(m0);
  }
  aggiorna();
  tabellaOfferte();

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (voci) {
      $("barra-mobile").classList.toggle("visibile", !voci[0].isIntersecting && voci[0].boundingClientRect.top > 0);
    }).observe($("risultato"));
  }
})();
