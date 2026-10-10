import re
import pandas as pd
from datetime import datetime

def estrai_modello(annuncio, modelli_ord, motorizzazioni):
    if not isinstance(annuncio, str):
        return None
    norm = re.sub(r"[^\w]", "", annuncio.lower())
    for chiave in modelli_ord:
        if chiave in norm:
            return motorizzazioni[chiave]
    return None

def estrai_allestimento(annuncio, mappa_allestimenti):
    ann = f" {annuncio.lower()} "  # spazi ai bordi: chiavi come " fr " valgono anche a inizio/fine titolo
    for chiave in sorted(mappa_allestimenti.keys(), key=lambda x: -len(x)):
        if chiave in ann:
            return mappa_allestimenti[chiave]
    return None

def unifica_allestimento(value, allestimento_performance, allestimento_sport, allestimento_middle, allestimento_base):
    if value in allestimento_performance:
        return "Performance"
    elif value in allestimento_sport:
        return "Sport"
    elif value in allestimento_middle:
        return "Middle"
    elif value in allestimento_base:
        return "Base"
    else:
        return "Altro"

def estrai_cv(modello, mappa_cv):
    return mappa_cv.get(modello)

def estrai_cv_annuncio(annuncio):
    """CV scritti nel titolo dell'annuncio (es. '150cv', '150 CV' o '110KW'); None se assenti o non plausibili."""
    if not isinstance(annuncio, str):
        return None
    cv = re.search(r"(\d{2,3})\s?cv\b", annuncio, re.IGNORECASE)
    kw = re.search(r"(\d{2,3})\s?kw\b", annuncio, re.IGNORECASE)
    valore = int(cv[1]) if cv else round(int(kw[1]) * 1.36) if kw else None
    return valore if valore and 50 <= valore <= 700 else None

def estrai_anni(valore, valore2, valore3):
    try:
        valore3 = float(str(valore3).replace("€", "").replace(",", "").strip())
    except (ValueError, TypeError):
        valore3 = None
        
    if pd.isna(valore):
        if pd.notna(valore2) and valore2 == 0:
            return 0
        elif pd.isna(valore2) and pd.notna(valore3) and valore3 > 31000:
            return 0
        elif pd.notna(valore) and valore == 0 and pd.notna(valore2) and valore2 == 0:
            return 0
        else:
            return None
    else:
        return datetime.now().year - valore