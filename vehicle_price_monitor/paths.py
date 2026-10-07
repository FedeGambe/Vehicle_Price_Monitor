"""Percorsi del progetto e caricamento config: unica fonte di verità, niente sys.path nei notebook."""
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
MODELS = DATA / "models"
GEO = Path(__file__).parent / "config" / "geo"


def load_config(modello):
    """Carica vehicle_price_monitor.config.config_<modello>.py"""
    try:
        return importlib.import_module(f"vehicle_price_monitor.config.config_{modello}")
    except ModuleNotFoundError as e:
        raise FileNotFoundError(f"Config per '{modello}' non trovata in vehicle_price_monitor/config/") from e
