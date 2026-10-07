"""Genera app/dashboard.html: pagina unica e autonoma (dati incorporati, nessun server, nessun modello ML da caricare)."""
import html
import json
from datetime import datetime
from urllib.parse import quote

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .paths import APP, MODELS, PROCESSED, load_config, modelli

ESCLUSE = ["Prezzo", "Distanza", "Venditore"]  # colonne escluse da X, come in train()
FAVICON = "data:image/svg+xml," + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='#101a33'/>"
    "<text x='16' y='23' font-size='20' font-weight='900' text-anchor='middle' fill='#e0a82e' font-family='Georgia,serif'>€</text></svg>")


def _dati_modello(nome):
    """Coefficienti della regressione lineare (usata dal calcolatore nel browser), metriche e migliori offerte."""
    cfg = load_config(nome)
    data = pd.read_csv(PROCESSED / nome / f"data_{nome}.csv")
    dummy = pd.read_csv(PROCESSED / nome / f"data_dummy_{nome}.csv")
    cols = [c for c in dummy.columns if c not in ESCLUSE]
    Xtr, Xte, ytr, yte = train_test_split(dummy[cols], dummy["Prezzo"], test_size=0.2, random_state=42)
    lr = LinearRegression().fit(Xtr, ytr)
    pred = lr.predict(Xte)
    tier = {a: t for t, lst in [("performance", cfg.allestimento_performance), ("sport", cfg.allestimento_sport),
                                ("middle", cfg.allestimento_middle), ("base", cfg.allestimento_base)] for a in lst}
    m = {
        "nome": nome, "titolo": f"{cfg.marca} {cfg.modello}", "n": len(data), "prezzo_medio": round(data["Prezzo"].mean()),
        "aggiornato": datetime.fromtimestamp((PROCESSED / nome / f"data_{nome}.csv").stat().st_mtime).strftime("%d/%m/%Y"),
        "cols": cols, "coef": lr.coef_.tolist(), "intercept": float(lr.intercept_),
        "r2_lin": r2_score(yte, pred), "rmse_lin": mean_squared_error(yte, pred) ** 0.5,
        "allestimenti": tier, "carburanti": sorted(data["Carburante"].unique()), "top": [],
        "r2_rf": None, "rmse_rf": None,
    }
    if (MODELS / nome / "modello_rf.pkl").exists():
        from .pipeline import valuta
        m["r2_rf"], m["rmse_rf"] = float(joblib.load(MODELS / nome / "r2_rf.pkl")), float(joblib.load(MODELS / nome / "rmse_rf.pkl"))
        df = valuta(nome)
        best = df[df["is_conveniente"] == 1].nlargest(20, "Indice_Appetibilità")
        m["top"] = [{"indice": r["Indice_Appetibilità"], "prezzo": int(r["Prezzo"]), "previsto": round(r["prezzo_previsto"]),
                     "anni": int(r["Anni"]), "km": int(r["Chilometraggio"]), "dist": int(r["Distanza"]),
                     "allest": r["Allestimento"], "carb": r["Carburante"], "link": r["Link"]} for _, r in best.iterrows()]
    return m


def _riga_modello(m):
    r2_rf = "" if m["r2_rf"] is None else f"{m['r2_rf']:.2f}"
    prezzo = f"{m['prezzo_medio']:,}".replace(",", ".")
    return (f"<tr><td>{html.escape(m['titolo'])}</td><td class='num'>{m['n']}</td><td class='num'>{prezzo} €</td>"
            f"<td class='num'>{r2_rf}</td><td class='num'>{m['r2_lin']:.2f}</td><td>{m['aggiornato']}</td></tr>")


def _capitoli(ms):
    righe = "".join(_riga_modello(m) for m in ms)
    opzioni = "".join(f"<option value='{m['nome']}'>{html.escape(m['titolo'])}</option>" for m in ms)
    dati = json.dumps(ms, ensure_ascii=False).replace("</", "<\\/")
    return f'''
<section class="capitolo" id="c0" data-titolo="Sintesi" data-parte=""><h2 data-n="Sintesi">Sovra o sotto prezzata?</h2>
  <p>Vehicle Price Monitor raccoglie gli annunci di auto usate da <strong>Autoscout24, Automobile.it, Autosupermarket e Subito</strong>,
  li pulisce e stima il prezzo di mercato con modelli statistici. Se il prezzo stimato è più alto di quello richiesto, l'auto è <strong>sotto prezzata</strong>: un buon affare.</p>
  <div class="tabella"><table><thead><tr><th>Modello</th><th>Annunci</th><th>Prezzo medio</th><th>R² Random Forest</th><th>R² lineare</th><th>Dati del</th></tr></thead><tbody>{righe}</tbody></table></div>
</section>
<section class="capitolo parte-a" id="c1" data-titolo="1. Calcola" data-parte="a"><h2 data-n="Capitolo 01">Calcola il prezzo giusto</h2>
  <p>Inserisci i dati dell'annuncio che hai trovato: il calcolo avviene nel tuo browser.</p>
  <div class="form">
    <label>Modello<select id="f-modello">{opzioni}</select></label>
    <label>Prezzo annuncio (€)<input id="f-prezzo" type="number" min="0" value="10000"></label>
    <label>Anni<input id="f-anni" type="number" min="0" max="30" value="3"></label>
    <label>Chilometraggio<input id="f-km" type="number" min="0" value="50000"></label>
    <label>CV<input id="f-cv" type="number" min="0" value="100"></label>
    <label>Cambio<select id="f-cambio"><option value="0">Manuale</option><option value="1">Automatico</option></select></label>
    <label>Allestimento<select id="f-allest"></select></label>
    <label>Carburante<select id="f-carb"></select></label>
    <label>Macro regione<select id="f-area"><option>Nord-est</option><option>Nord-ovest</option><option>Centro</option><option>Sud</option><option>Isole</option></select></label>
  </div>
  <button class="bottone" id="calcola" type="button">Calcola</button>
  <div class="esito" id="esito" hidden aria-live="polite"></div>
</section>
<section class="capitolo parte-b" id="c2" data-titolo="2. Migliori offerte" data-parte="b"><h2 data-n="Capitolo 02">Le migliori offerte</h2>
  <p>Annunci sotto prezzati secondo la Random Forest, ordinati per <strong>indice di appetibilità</strong> (prezzo, km, anni, distanza, allestimento, cambio, CV: pesi in <code>data/config/utente.toml</code>).</p>
  <div class="form"><label>Modello<select id="o-modello">{opzioni}</select></label></div>
  <div class="tabella"><table><thead><tr><th>Indice</th><th>Prezzo</th><th>Previsto</th><th>Risparmio</th><th>Anni</th><th>Km</th><th>Dist. km</th><th>Allestimento</th><th>Alim.</th><th></th></tr></thead><tbody id="top-corpo"></tbody></table></div>
</section>
<section class="capitolo" id="c3" data-titolo="3. Come funziona" data-parte=""><h2 data-n="Capitolo 03">Come funziona</h2>
  <p>Due modelli per ogni auto, addestrati sugli annunci raccolti: una <strong>Random Forest</strong> (più precisa, usata per la classifica) e una <strong>regressione lineare</strong>
  (i cui coefficienti sono incorporati in questa pagina, così il calcolatore funziona senza caricare nulla). Per questo il calcolatore può differire un po' dalla classifica.
  L'errore tipico (RMSE) è mostrato sotto ogni stima: se la differenza è più piccola dell'errore, il prezzo è <em>in linea</em>.</p>
  <div class="conclusione"><p>Le stime valgono per i filtri usati nello scraping (prezzo, anni, km) e per il comune di residenza scelto.</p></div>
</section>
<section class="capitolo" id="c4" data-titolo="4. Aggiornare i dati" data-parte=""><h2 data-n="Capitolo 04">Aggiornare i dati</h2>
  <p>Dalla cartella del progetto:</p>
  <ul><li><code>python -m vehicle_price_monitor run Opel_Corsa</code>: scarica, pulisce, addestra e rigenera questa pagina.</li>
  <li><code>python -m vehicle_price_monitor top Opel_Corsa --prezzo-max 12000 --dist-max 150</code>: classifica nel terminale con i tuoi filtri.</li>
  <li><code>python -m vehicle_price_monitor -h</code>: tutti i comandi. Nuove auto: aggiungi <code>data/config/Marca_Modello.toml</code>.</li></ul>
</section>
<script type="application/json" id="dati">{dati}</script>
<script>{_JS}</script>
'''


_JS = r'''
(() => {
  const D = Object.fromEntries(JSON.parse(document.getElementById("dati").textContent).map(m => [m.nome, m]));
  const $$ = id => document.getElementById(id);
  const AREE = {"Nord-est": null, "Nord-ovest": "is NO vs NE", "Centro": "is Centro vs NE", "Sud": "is Sud_Isole vs NE", "Isole": "is Sud_Isole vs NE"};
  const eur = n => Math.round(n).toLocaleString("it-IT") + " €";
  const riempi = (sel, valori) => sel.replaceChildren(...valori.map(v => Object.assign(document.createElement("option"), {textContent: v})));

  function cambiaModello() {
    const m = D[$$("f-modello").value];
    riempi($$("f-allest"), Object.keys(m.allestimenti));
    riempi($$("f-carb"), m.carburanti);
    $$("esito").hidden = true;
  }
  $$("f-modello").addEventListener("change", cambiaModello);
  cambiaModello();

  $$("calcola").addEventListener("click", () => {
    const m = D[$$("f-modello").value], v = id => $$(id).value;
    const f = {Anni: +v("f-anni"), Chilometraggio: +v("f-km"), CV: +v("f-cv"), Cambio: +v("f-cambio"),
      [`is_${v("f-carb")} vs Benzina`]: 1, [`is_${m.allestimenti[v("f-allest")]} vs base`]: 1, [AREE[v("f-area")]]: 1};
    const previsto = m.cols.reduce((s, c, i) => s + m.coef[i] * (f[c] || 0), m.intercept);
    const prezzo = +v("f-prezzo"), delta = previsto - prezzo;
    const [classe, testo] = delta > m.rmse_lin ? ["buono", "Sotto prezzata: buon affare"]
      : delta < -m.rmse_lin ? ["cattivo", "Sovra prezzata"] : ["", "Prezzo in linea con il mercato"];
    const box = $$("esito");
    box.className = "esito " + classe;
    const s = Object.assign(document.createElement("strong"), {className: "verdetto", textContent: testo});
    const r = Object.assign(document.createElement("div"), {
      textContent: `Prezzo richiesto ${eur(prezzo)} · prezzo stimato ${eur(previsto)} · differenza ${delta >= 0 ? "+" : ""}${eur(delta)}`});
    const e = Object.assign(document.createElement("small"), {
      textContent: `Errore tipico del modello: ±${eur(m.rmse_lin)} (regressione lineare, R² ${m.r2_lin.toFixed(2)}).`});
    box.replaceChildren(s, r, e);
    box.hidden = false;
  });

  function tabella() {
    const m = D[$$("o-modello").value], corpo = $$("top-corpo");
    corpo.replaceChildren();
    if (!m.top.length) {
      const td = Object.assign(document.createElement("td"), {colSpan: 10, textContent: "Nessuna offerta (modello non ancora addestrato?)"});
      corpo.append(document.createElement("tr")); corpo.lastChild.append(td);
      return;
    }
    for (const o of m.top) {
      const tr = document.createElement("tr");
      const celle = [o.indice.toFixed(2), eur(o.prezzo), eur(o.previsto), "+" + eur(o.previsto - o.prezzo), o.anni, o.km.toLocaleString("it-IT"), o.dist, o.allest, o.carb];
      celle.forEach((t, i) => {
        const td = Object.assign(document.createElement("td"), {textContent: t});
        if (i < 7) td.className = "num" + (i === 3 ? " pos" : "");
        tr.append(td);
      });
      const a = Object.assign(document.createElement("a"), {href: o.link, target: "_blank", rel: "noopener", textContent: "Apri"});
      const td = document.createElement("td"); td.append(a); tr.append(td);
      corpo.append(tr);
    }
  }
  $$("o-modello").addEventListener("change", tabella);
  tabella();
})();
'''


def build(nomi=None, out=APP / "dashboard.html"):
    nomi = nomi or [n for n in modelli() if (PROCESSED / n / f"data_dummy_{n}.csv").exists()]
    if not nomi:
        raise SystemExit("Nessun modello con dati processati: esegui prima 'run <modello>'")
    ms = [_dati_modello(n) for n in nomi]
    cover = (APP / "copertina.svg").read_text(encoding="utf8").replace(
        "<svg ", '<svg class="bauhaus" preserveAspectRatio="xMidYMax slice" aria-hidden="true" ', 1)
    voci = [("c0", "Sintesi", "gruppo-grigio", ""), ("c1", "1. Calcola", "", ""), ("c2", "2. Migliori offerte", "", "link-b"),
            ("c3", "3. Come funziona", "gruppo-grigio", ""), ("c4", "4. Aggiornare i dati", "gruppo-grigio", "")]
    indice = "".join(f'<li class="{li}"><a class="{a}" href="#{i}">{t}</a></li>' for i, t, li, a in voci)
    tag = "".join(f"<span>{t}</span>" for t in ("Web scraping", "Machine Learning", "Prezzi auto usate"))
    pagina = (APP / "template.html").read_text(encoding="utf8")
    for k, v in {
        "LINGUA": "it", "TITOLO": "Vehicle Price Monitor", "TITOLO_HTML": "Vehicle <em>Price</em> Monitor",
        "DESCRIZIONE": "Quanto vale davvero un'auto usata? Confronto dei prezzi e stima sovra/sotto prezzo.",
        "SOTTOTITOLO": "Quanto vale davvero un'auto usata? Scopri se un annuncio è <strong>sovra o sotto prezzato</strong>.",
        "TAG": tag, "COVER_SVG": cover, "INDICE_VOCI": indice, "CAPITOLI": _capitoli(ms), "FAVICON_URI": FAVICON,
        "FOOTER": f"<p>Dati aggiornati al {ms[0]['aggiornato']} · Autoscout24, Automobile.it, Autosupermarket, Subito</p>",
    }.items():
        pagina = pagina.replace("{{" + k + "}}", v)
    out.write_text(pagina, encoding="utf8")
    print(f"🌐 Dashboard: {out} ({', '.join(nomi)})")
    return out
