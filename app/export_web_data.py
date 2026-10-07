"""Genera app/web/models.json: regressione lineare per modello, usabile dalla dashboard JSX senza i .pkl.
Uso: python -m app.export_web_data"""
import json
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from vehicle_price_monitor.paths import PROCESSED, load_config

ESCLUSE = ["Prezzo", "Distanza", "Venditore"]  # stesse colonne escluse da X nei notebook
out = {}
for d in sorted(p for p in PROCESSED.iterdir() if p.is_dir() and (p / f"data_dummy_{p.name}.csv").exists()):
    nome = d.name
    dummy = pd.read_csv(d / f"data_dummy_{nome}.csv")
    cols = [c for c in dummy.columns if c not in ESCLUSE]
    X, y = dummy[cols], dummy["Prezzo"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    lr = LinearRegression().fit(Xtr, ytr)
    pred = lr.predict(Xte)
    cfg = load_config(nome)
    tier = {a: t for t, lst in [("performance", cfg.allestimento_performance), ("sport", cfg.allestimento_sport),
                                ("middle", cfg.allestimento_middle), ("base", cfg.allestimento_base)] for a in lst}
    out[nome] = {
        "cols": cols, "coef": lr.coef_.tolist(), "intercept": float(lr.intercept_),
        "r2": r2_score(yte, pred), "rmse": mean_squared_error(yte, pred) ** 0.5,
        "allestimenti": tier,
        "carburanti": pd.read_csv(d / f"data_{nome}.csv")["Carburante"].unique().tolist(),
    }
dest = __file__.rsplit("export_web_data.py", 1)[0] + "web/models.json"
json.dump(out, open(dest, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("scritto", dest, list(out))
