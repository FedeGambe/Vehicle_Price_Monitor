"""Uso: python -m vehicle_price_monitor <comando> [modello] [opzioni]   (python -m vehicle_price_monitor -h)"""
import argparse

from . import pipeline
from .paths import modelli


def _elenco(valori):
    """'tutti' -> tutti i modelli configurati."""
    return modelli() if valori == ["tutti"] else valori


def main():
    ap = argparse.ArgumentParser(prog="vehicle_price_monitor", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = dict(nargs="+", metavar="MODELLO", help="es. Opel_Corsa (più modelli, oppure 'tutti')")

    sub.add_parser("modelli", help="elenca i modelli configurati in data/config/")

    filtri = argparse.ArgumentParser(add_help=False)
    for f in ("prezzo-min", "prezzo-max", "km-min", "km-max", "anno-min", "anno-max"):
        filtri.add_argument(f"--{f}", type=int, help="default: sezione [ricerca] del TOML del modello")
    filtri.add_argument("--siti", nargs="+", choices=pipeline.SITI, default=list(pipeline.SITI))
    filtri.add_argument("--max-pages", type=int, help="pagine massime per sito (default: tutte)")

    p = sub.add_parser("scrape", parents=[filtri], help="scarica gli annunci in data/raw/<modello>/")
    p.add_argument("modello", **m)
    p = sub.add_parser("prepare", help="pulisce i dati grezzi -> data/processed/<modello>/")
    p.add_argument("modello", **m)
    p.add_argument("--comune", help="comune di residenza (default: data/config/utente.toml)")
    p = sub.add_parser("train", help="addestra la Random Forest -> data/models/<modello>/")
    p.add_argument("modello", **m)
    p = sub.add_parser("top", help="classifica delle migliori offerte (indice di appetibilità)")
    p.add_argument("modello", metavar="MODELLO")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--prezzo-min", type=int, default=0)
    p.add_argument("--prezzo-max", type=int, default=10**9)
    p.add_argument("--km-max", type=int, default=10**9)
    p.add_argument("--dist-max", type=int, default=10**9, help="distanza massima in km")
    p.add_argument("--carburante")
    p = sub.add_parser("dashboard", help="genera app/dashboard.html (pagina unica, si apre con doppio clic)")
    p.add_argument("modello", nargs="*", metavar="MODELLO", help="default: tutti quelli con dati")
    p = sub.add_parser("run", parents=[filtri], help="scrape + prepare + train + dashboard")
    p.add_argument("modello", **m)
    p.add_argument("--comune")
    p.add_argument("--senza-scraping", action="store_true", help="riusa i dati grezzi già scaricati")

    a = ap.parse_args()
    f = {k: getattr(a, k.replace("-", "_"), None) for k in ("prezzo-min", "prezzo-max", "km-min", "km-max", "anno-min", "anno-max")}
    f = {k.replace("-", "_"): v for k, v in f.items()}

    if a.cmd == "modelli":
        print("\n".join(modelli()))
    elif a.cmd == "top":
        pipeline.top(a.modello, a.n, a.prezzo_min, a.prezzo_max, a.km_max, a.dist_max, a.carburante)
    elif a.cmd == "dashboard":
        from .dashboard import build
        build(a.modello or None)
    else:
        for nome in _elenco(a.modello):
            print(f"\n===== {nome} =====")
            if a.cmd in ("scrape", "run") and not getattr(a, "senza_scraping", False):
                pipeline.scrape(nome, a.siti, a.max_pages, **f)
            if a.cmd in ("prepare", "run"):
                pipeline.prepare(nome, getattr(a, "comune", None))
            if a.cmd in ("train", "run"):
                pipeline.train(nome)
        if a.cmd == "run":
            from .dashboard import build
            build()


if __name__ == "__main__":
    main()
