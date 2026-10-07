"""Le fasi del programma: scrape -> prepare -> train -> top. Richiamate dalla riga di comando (python -m vehicle_price_monitor)."""
import numpy as np
import pandas as pd

from .paths import GEO, MODELS, PROCESSED, RAW, load_config, load_utente

SITI = ("autoscout", "automobile_it", "autosupermarket", "subito_it")
FILE_SITO = {"autoscout": "data_autoscout.csv", "automobile_it": "data_automobile_it.csv",
             "autosupermarket": "data_autosupermarket.csv", "subito_it": "data_subito_it.csv"}


def _ricerca(cfg, **override):
    """Filtri di default dal TOML del modello, sovrascritti dai valori passati (se non None)."""
    r = dict(cfg.ricerca)
    r.update({k: v for k, v in override.items() if v is not None})
    return r


def scrape(nome, siti=SITI, max_pages=None, **filtri):
    from .scraping.scraping_functions import (autoscout_scraper, automobile_it_scraper,
                                              autosupermarket_scraper, subito_scraper)
    from .scraping.url_builders import (bild_autoscout_urls, build_automobile_url,
                                        build_autosupermarket_url, build_subito_url)
    cfg = load_config(nome)
    r = _ricerca(cfg, **filtri)
    args = (r["prezzo_min"], r["prezzo_max"], r["km_min"], r["km_max"], r["anno_min"], r["anno_max"])
    slug = {s: cfg.siti[s].split("/") for s in cfg.siti}
    out = RAW / nome
    out.mkdir(parents=True, exist_ok=True)

    def autoscout():
        dfs = [autoscout_scraper(u + "&page={}", max_pages=max_pages or 20) for u in bild_autoscout_urls(*slug["autoscout"], *args)]
        return pd.concat([d for d in dfs if len(d)], ignore_index=True)

    def autosupermarket():
        df = autosupermarket_scraper(build_autosupermarket_url(*slug["autosupermarket"], *args), max_pages=max_pages)
        if df.empty:
            return df
        df["Prezzo"] = df["Prezzo"].apply(lambda x: x.split("\n")[-1] if "%" in x else x)
        return df.replace({"": np.nan, "Prezzo riservato": np.nan}).dropna()

    job = {
        "autoscout": autoscout,
        "automobile_it": lambda: automobile_it_scraper(build_automobile_url(*slug["automobile_it"], *args), max_pages=max_pages),
        "autosupermarket": autosupermarket,
        "subito_it": lambda: subito_scraper(build_subito_url(*slug["subito_it"], *args), max_pages=max_pages),
    }
    for sito in siti:
        try:
            df = job[sito]()
        except Exception as e:  # un sito che si rompe non deve fermare gli altri
            print(f"❌ {nome} / {sito}: {type(e).__name__}: {e}")
            continue
        if df is None or df.empty:
            print(f"⚠️ {nome} / {sito}: nessun dato, file non modificato")
            continue
        df.to_csv(out / FILE_SITO[sito], index=False)
        print(f"💾 {nome} / {sito}: {len(df)} annunci -> {out / FILE_SITO[sito]}")


def prepare(nome, comune=None):
    from .preparation.dataset_cleaning import clean_data_AS, clean_data_ASM, clean_data_AT, clean_data_SU
    from .preparation.dataset_formatting import data_formatting, get_data_dummy
    cfg = load_config(nome)
    comune = comune or load_utente()["comune"]
    distanza = pd.read_csv(GEO / "distanza.csv")
    only_cap_per_comune = pd.read_csv(GEO / "only_cap_per_comune.csv")
    only_comune_per_cap = pd.read_csv(GEO / "only_comune_per_cap.csv")
    m, ordine = cfg.motorizzazioni_norm, cfg.modelli_ord

    pulizia = {
        "autoscout": lambda d: clean_data_AS(d, only_comune_per_cap, m, ordine, cfg.mappa_cv),
        "automobile_it": lambda d: clean_data_AT(d, only_cap_per_comune, m, ordine, cfg.mappa_cv),
        "autosupermarket": lambda d: clean_data_ASM(d, m, ordine),
        "subito_it": lambda d: clean_data_SU(d, only_cap_per_comune, m, ordine, cfg.mappa_cv),
    }
    parti = []
    for sito, pulisci in pulizia.items():
        f = RAW / nome / FILE_SITO[sito]
        if f.exists():
            parti.append(pulisci(pd.read_csv(f)))
            print(f"✅ {sito}: {len(parti[-1])} annunci puliti")
        else:
            print(f"⚠️ {sito}: {f.name} mancante, salto")
    if not parti:
        raise SystemExit(f"Nessun dato grezzo in {RAW / nome}: esegui prima 'scrape {nome}'")

    data = pd.concat(parti, ignore_index=True)
    data["Venditore"] = data["Venditore"].fillna("Rivenditore")
    formattato = data_formatting(data, only_cap_per_comune, distanza, comune, cfg.mappa_allestimenti,
                                 cfg.allestimento_performance, cfg.allestimento_sport,
                                 cfg.allestimento_middle, cfg.allestimento_base)
    dummy = get_data_dummy(formattato, cfg.allestimento_performance, cfg.allestimento_sport, cfg.allestimento_middle)
    out = PROCESSED / nome
    out.mkdir(parents=True, exist_ok=True)
    data.to_csv(out / f"data_NF_{nome}NF.csv", index=False)
    formattato.to_csv(out / f"data_{nome}.csv", index=False)
    dummy.to_csv(out / f"data_dummy_{nome}.csv", index=False)
    print(f"💾 {nome}: {len(formattato)} annunci pronti in {out}")


def _carica(nome):
    return (pd.read_csv(PROCESSED / nome / f"data_{nome}.csv"),
            pd.read_csv(PROCESSED / nome / f"data_dummy_{nome}.csv"))


def train(nome):
    from .analysis.price_analysis import modello_ml
    _, dummy = _carica(nome)
    modello_ml(dummy.drop(columns=["Prezzo", "Distanza", "Venditore"]), dummy["Prezzo"], MODELS / nome)


def valuta(nome):
    """Ritorna il DataFrame di tutti gli annunci con prezzo previsto (Random Forest), delta e indice di appetibilità."""
    from .analysis.price_analysis import indice_appetibilita, predizione_prezzo
    cfg, u = load_config(nome), load_utente()
    data, dummy = _carica(nome)
    X = dummy.drop(columns=["Prezzo", "Distanza", "Venditore"])
    _, y_pred = predizione_prezzo(dummy.copy(), X, MODELS / nome)
    p = u["pesi"]
    return indice_appetibilita(data, y_pred, u["prezzo_soglia"], p["anni"], p["prezzo"], p["km"], p["distanza"],
                               p["allestimento"], p["cv"], p["cambio"], cfg.allestimento_performance,
                               cfg.allestimento_sport, cfg.allestimento_middle, cfg.allestimento_base)


def top(nome, n=20, prezzo_min=0, prezzo_max=10**9, km_max=10**9, dist_max=10**9, carburante=None):
    df = valuta(nome)
    f = (df["Prezzo"].between(prezzo_min, prezzo_max) & (df["Chilometraggio"] <= km_max) & (df["Distanza"] <= dist_max))
    if carburante:
        f &= df["Carburante"] == carburante
    best = df[f].nlargest(n, "Indice_Appetibilità")
    cols = ["Indice_Appetibilità", "Prezzo", "prezzo_previsto", "delta_prezzo", "Anni", "Chilometraggio", "Distanza", "Allestimento", "Link"]
    with pd.option_context("display.width", 250, "display.max_colwidth", 90, "display.max_columns", None):
        print(f"Le migliori {len(best)} auto di {nome} per indice di appetibilità:\n")
        print(best[cols].to_string(index=False))
    return best
