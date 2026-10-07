"""Percorsi del progetto e lettura delle configurazioni (data/config/*.toml)."""
import re
import tomllib
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
MODELS = DATA / "models"
CONFIG = DATA / "config"
GEO = CONFIG / "geo"
APP = ROOT / "app"


def modelli():
    """Nomi dei modelli configurati (un file <Marca_Modello>.toml per modello)."""
    return sorted(p.stem for p in CONFIG.glob("*.toml") if p.stem != "utente")


def _normalizza(s):
    return re.sub(r"[^\w]", "", s.lower())


def load_config(modello):
    """Legge data/config/<modello>.toml e aggiunge i campi derivati usati dalla preparazione dati."""
    f = CONFIG / f"{modello}.toml"
    if not f.exists():
        raise FileNotFoundError(f"Config non trovata: {f}. Modelli disponibili: {', '.join(modelli())}")
    d = tomllib.loads(f.read_text(encoding="utf8"))
    norm = {_normalizza(k): v for k, v in d["motorizzazioni"].items()}
    return SimpleNamespace(
        marca=d["marca"], modello=d["modello"], siti=d["siti"], ricerca=d["ricerca"],
        allestimento_performance=d["allestimenti"]["performance"], allestimento_sport=d["allestimenti"]["sport"],
        allestimento_middle=d["allestimenti"]["middle"], allestimento_base=d["allestimenti"]["base"],
        mappa_allestimenti=d["mappa_allestimenti"], motorizzazioni=d["motorizzazioni"],
        motorizzazioni_norm=norm, modelli_ord=sorted(norm, key=len, reverse=True), mappa_cv=d["mappa_cv"],
    )


def load_utente():
    """Preferenze personali: comune di residenza, pesi dell'indice di appetibilità."""
    return tomllib.loads((CONFIG / "utente.toml").read_text(encoding="utf8"))
