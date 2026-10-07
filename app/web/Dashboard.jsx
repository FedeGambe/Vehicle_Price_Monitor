// Dashboard standalone: nessun modello ML da caricare, usa i coefficienti di models.json (regressione lineare).
const { useState, useEffect } = React;
const AREE = { "Nord-est": null, "Nord-ovest": "is NO vs NE", "Centro": "is Centro vs NE", "Sud": "is Sud_Isole vs NE", "Isole": "is Sud_Isole vs NE" };
const eur = (n) => n.toLocaleString("it-IT", { maximumFractionDigits: 0 }) + " €";

function predici(m, v) {
  const f = {
    Anni: v.anni, Chilometraggio: v.km, Cambio: v.cambio === "automatico" ? 1 : 0, CV: v.cv,
    [`is_${v.carburante} vs Benzina`]: 1,
    [`is_${m.allestimenti[v.allestimento]} vs base`]: 1,
    [AREE[v.area]]: 1,
  };
  return m.cols.reduce((s, c, i) => s + m.coef[i] * (f[c] || 0), m.intercept);
}

function Campo({ label, children }) {
  return <label style={{ display: "block", margin: "8px 0" }}>{label}<br />{children}</label>;
}

function Dashboard() {
  const [models, setModels] = useState(null);
  const [nome, setNome] = useState("");
  const [v, setV] = useState({ prezzo: 10000, anni: 3, km: 50000, cambio: "manuale", cv: 100, allestimento: "", carburante: "", area: "Nord-est" });
  const [res, setRes] = useState(null);

  useEffect(() => { fetch("models.json").then((r) => r.json()).then((d) => { setModels(d); setNome(Object.keys(d)[0]); }); }, []);
  const m = models && models[nome];
  useEffect(() => {
    if (m) { setV((x) => ({ ...x, allestimento: Object.keys(m.allestimenti)[0], carburante: m.carburanti[0] })); setRes(null); }
  }, [nome, models]);

  if (!m) return <p>Caricamento…</p>;
  const set = (k) => (e) => setV({ ...v, [k]: e.target.type === "number" ? +e.target.value : e.target.value });
  const num = (k) => <input type="number" value={v[k]} onChange={set(k)} />;
  const sel = (k, opts) => <select value={v[k]} onChange={set(k)}>{opts.map((o) => <option key={o}>{o}</option>)}</select>;
  const calcola = () => { const p = predici(m, v); setRes({ p, d: p - v.prezzo }); };

  return (
    <div style={{ maxWidth: 480, margin: "24px auto", fontFamily: "sans-serif" }}>
      <h2>Predizione prezzo</h2>
      <Campo label="Modello"><select value={nome} onChange={(e) => setNome(e.target.value)}>{Object.keys(models).map((o) => <option key={o}>{o}</option>)}</select></Campo>
      <Campo label="Prezzo annuncio (€)">{num("prezzo")}</Campo>
      <Campo label="Anni">{num("anni")}</Campo>
      <Campo label="Chilometraggio">{num("km")}</Campo>
      <Campo label="CV">{num("cv")}</Campo>
      <Campo label="Cambio">{sel("cambio", ["manuale", "automatico"])}</Campo>
      <Campo label="Allestimento">{sel("allestimento", Object.keys(m.allestimenti))}</Campo>
      <Campo label="Carburante">{sel("carburante", m.carburanti)}</Campo>
      <Campo label="Macro regione">{sel("area", Object.keys(AREE))}</Campo>
      <button onClick={calcola}>Genera predizione</button>
      {res && (
        <p>
          <b>{res.d > 100 ? "✅ Conveniente" : "❌ Non conveniente"}</b><br />
          Prezzo previsto: {eur(res.p)}<br />Differenza: {eur(res.d)}<br />
          <small>Regressione lineare — R² {m.r2.toFixed(2)}, RMSE {eur(m.rmse)}</small>
        </p>
      )}
    </div>
  );
}
ReactDOM.createRoot(document.getElementById("root")).render(<Dashboard />);
