"""Genera docs/index.html: dashboard in un solo file (dati incorporati, nessun server, nessun modello ML da caricare)."""
import html
import json
from datetime import datetime
from urllib.parse import quote

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .paths import DOCS, MODELS, PROCESSED, load_config, modelli

WEB = __import__("pathlib").Path(__file__).parent / "web"  # template.html e logica.js
ESCLUSE = ["Prezzo", "Distanza", "Venditore"]  # colonne escluse da X, come in train()
FAVICON = "data:image/svg+xml," + quote((DOCS / "favicon.svg").read_text(encoding="utf8"))  # incorporata: la pagina resta un file solo


def _dati_modello(nome):
    """Coefficienti della regressione lineare (il calcolo avviene nel browser), medie, intervalli osservati, metriche e migliori offerte."""
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
        "medie": {c: float(dummy[c].mean()) for c in cols},
        "r2_lin": r2_score(yte, pred), "rmse_lin": mean_squared_error(yte, pred) ** 0.5,
        "allestimenti": tier, "carburanti": sorted(data["Carburante"].unique()),
        "tipico": {"anni": int(data["Anni"].median()), "km": int(round(data["Chilometraggio"].median(), -3)),
                   "cv": int(data["CV"].median()), "prezzo": int(round(data["Prezzo"].median(), -2))},
        "oss": {c: [int(data[k].quantile(.01)), int(data[k].quantile(.99))]  # 1°-99° percentile: ignora gli annunci anomali
                for c, k in (("anni", "Anni"), ("km", "Chilometraggio"), ("cv", "CV"), ("prezzo", "Prezzo"))},
        "top": [], "r2_rf": None, "rmse_rf": None,
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
    r2_rf = "–" if m["r2_rf"] is None else f"{m['r2_rf']:.2f}"
    rmse_rf = "–" if m["rmse_rf"] is None else f"±{round(m['rmse_rf']):,} €".replace(",", ".")
    prezzo = f"{m['prezzo_medio']:,}".replace(",", ".")
    rmse_lin = f"±{round(m['rmse_lin']):,} €".replace(",", ".")
    return (f"<tr><td>{html.escape(m['titolo'])}</td><td class='n'>{m['n']}</td><td class='n'>{prezzo} €</td>"
            f"<td class='n'>{r2_rf}</td><td class='n'>{rmse_rf}</td><td class='n'>{m['r2_lin']:.2f}</td><td class='n'>{rmse_lin}</td>"
            f"<td>{m['aggiornato']}</td></tr>")


SEZIONI = '''
      <fieldset class="scheda sezione">
        <legend><span class="passo">1</span>L'auto</legend>
        <div class="campi">
          <div class="campo largo"><label class="etichetta" for="modello">Modello</label><select id="modello"></select></div>
          <div class="campo"><label class="etichetta" for="allest">Allestimento</label><select id="allest"></select></div>
          <fieldset class="campo"><legend>Cambio</legend><div class="segmenti" id="seg-cambio"></div></fieldset>
          <fieldset class="campo largo"><legend>Carburante</legend><div class="segmenti colonne" id="seg-carb"></div></fieldset>
        </div>
      </fieldset>

      <fieldset class="scheda sezione">
        <legend><span class="passo">2</span>I numeri dell'annuncio</legend>
        <div class="campi">
          <div class="campo" data-contatore="anni"><label class="etichetta" for="anni">Anni dall'immatricolazione</label></div>
          <div class="campo" data-numero="cv" data-unita="CV"><label class="etichetta" for="cv">Potenza</label></div>
          <div class="campo" data-numero="km" data-unita="km"><label class="etichetta" for="km">Chilometraggio</label></div>
          <div class="campo" data-numero="prezzo" data-unita="€"><label class="etichetta" for="prezzo">Prezzo richiesto</label></div>
        </div>
      </fieldset>

      <fieldset class="scheda sezione">
        <legend><span class="passo">3</span>Dove si trova</legend>
        <div class="campi">
          <fieldset class="campo largo"><legend>Zona</legend><div class="segmenti colonne" id="seg-area"></div></fieldset>
        </div>
      </fieldset>
'''

KPI = '''
          <svg class="indicatore" viewBox="0 0 240 152" role="img" aria-labelledby="ind-desc">
            <desc id="ind-desc">Differenza tra prezzo stimato e prezzo richiesto</desc>
            <path class="traccia" d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke-width="20" stroke-linecap="round"/>
            <path class="valore" id="arco" d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke-width="20" stroke-linecap="round" pathLength="100" stroke-dasharray="0 100"/>
            <line class="media" x1="120" y1="8" x2="120" y2="40"/>
            <text class="grande" id="valore-grande" x="120" y="112" text-anchor="middle">–</text>
            <text class="estremi" x="20" y="148" text-anchor="middle">sovra</text>
            <text class="estremi" x="220" y="148" text-anchor="middle">sotto</text>
          </svg>
          <p class="delta" id="delta" aria-live="polite"></p>
          <div class="verdetto" id="verdetto"></div>
          <p class="confronto" id="confronto"></p>
'''

DETTAGLIO = '''
        <div class="cascata" id="cascata" role="list"></div>
        <div class="asse-x" aria-hidden="true"><span></span><div class="tacche" id="tacche"></div><span></span></div>
        <div class="legenda" aria-hidden="true"><span><i style="background:var(--teal)"></i>▲ alza il prezzo</span><span><i style="background:var(--arancio)"></i>▼ abbassa il prezzo</span></div>
'''

METODO = '''
          <p>Si parte dal prezzo stimato per l'<strong>auto media</strong> del modello e si aggiunge, una voce alla volta, l'effetto delle caratteristiche di questa auto rispetto alla media,
            dalla più influente alla meno influente. L'ultima riga è il prezzo stimato; il segno arancio è il prezzo richiesto.</p>
          <p>Gli effetti vengono da una regressione lineare sugli annunci raccolti: descrivono il modello, non una causa. La classifica in fondo alla pagina usa invece una Random Forest, più precisa:
            per questo le due stime possono differire.</p>
'''

RISULTATI = '''
  <section class="risultati" id="risultati" aria-label="Risultati">
    <div class="scheda">
      <h2>Risultati per modello</h2>
      <p>Qualità dei due modelli addestrati sugli annunci raccolti. R² più vicino a 1 e errore tipico (RMSE) più basso significano stime più affidabili.</p>
      <div class="tabella"><table><thead><tr><th>Modello</th><th>Annunci</th><th>Prezzo medio</th><th>R² Random Forest</th><th>Errore RF</th><th>R² lineare</th><th>Errore lineare</th><th>Dati del</th></tr></thead><tbody>__RIGHE__</tbody></table></div>
    </div>
    <div class="scheda">
      <h2>Le migliori offerte</h2>
      <p>Annunci sotto prezzati secondo la Random Forest, ordinati per <strong>indice di appetibilità</strong> (prezzo, km, anni, distanza, allestimento, cambio, CV: i pesi sono in <code>data/config/utente.toml</code>).</p>
      <div class="campo selettore"><label class="etichetta" for="o-modello">Modello</label><select id="o-modello"></select></div>
      <div class="tabella"><table><thead><tr><th>Indice</th><th>Prezzo</th><th>Previsto</th><th>Risparmio</th><th>Anni</th><th>Km</th><th>Dist. km</th><th>Allestimento</th><th>Alim.</th><th></th></tr></thead><tbody id="top-corpo"></tbody></table></div>
    </div>
  </section>
'''


def build(nomi=None, out=DOCS / "index.html"):
    nomi = nomi or [n for n in modelli() if (PROCESSED / n / f"data_dummy_{n}.csv").exists()]
    if not nomi:
        raise SystemExit("Nessun modello con dati processati: esegui prima 'run <modello>'")
    ms = [_dati_modello(n) for n in nomi]
    dati = json.dumps({"ordine": nomi, "modelli": {m["nome"]: m for m in ms}}, ensure_ascii=False).replace("</", "<\\/")
    pagina = (WEB / "template.html").read_text(encoding="utf8")
    for k, v in {
        "LINGUA": "it", "TITOLO": "Vehicle Price Monitor", "TITOLO_HTML": "Vehicle <em>Price</em> Monitor",
        "DESCRIZIONE": "Un'auto usata è sovra o sotto prezzata? Stima del prezzo di mercato e migliori offerte.",
        "INTRO": "Inserisci i dati di un annuncio e scopri se il prezzo è in linea con il mercato. "
                 "La stima si basa sugli annunci di Autoscout24, Automobile.it, Autosupermarket e Subito.",
        "LINK_BARRA": "", "FAVICON_URI": FAVICON, "SEZIONI_CONTROLLI": SEZIONI,
        "TITOLO_KPI": "Prezzo giusto?", "KPI": KPI, "ETICHETTA_KPI": "Stima − richiesto",
        "TITOLO_DETTAGLIO": "Cosa fa il prezzo", "DETTAGLIO": DETTAGLIO, "NOTE_METODO": METODO,
        "RISULTATI": RISULTATI.replace("__RIGHE__", "".join(_riga_modello(m) for m in ms)),
        "NOTA_FOOTER": ("<p>Stime indicative su annunci raccolti il " + ms[0]["aggiornato"] + ": i prezzi di vendita reali possono differire, "
                        "e il modello descrive correlazioni, non cause. Nessun dato inserito lascia il tuo browser.</p>"),
        "DATI": dati, "LOGICA": (WEB / "logica.js").read_text(encoding="utf8"),
    }.items():
        pagina = pagina.replace("{{" + k + "}}", v)
    out.write_text(pagina, encoding="utf8")
    print(f"🌐 Dashboard: {out} ({', '.join(nomi)})")
    return out
