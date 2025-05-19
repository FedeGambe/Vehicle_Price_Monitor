import re
import pandas as pd
from datetime import datetime

# Allestimenti noti
allestimenti = [
    "Sport", "Business", "AMG", "AMG line", "amg-line", "Elegance",
    "Premium", "Advanced", "Progressive", "Executive"
]

# Mappatura modelli e motorizzazioni
motorizzazioni = {
    "a160": "A 160", "a180": "A 180", "a200": "A 200", "a220": "A 220", "a250": "A 250",
    "a35": "A 35", "a45": "A 45", "a45s": "A 45 S",
    "a160d": "A 160 d", "a180d": "A 180 d", "a200d": "A 200 d", "a220d": "A 220 d",
    "a250e": "A 250 e",
    "160": "A 160", "180": "A 180", "180d": "A 180 d", "200": "A 200",
    "200d": "A 200 d", "220": "A 220", "220d": "A 220 d", "250": "A 250",
    "250e": "A 250 e", "35": "A 35", "45": "A 45", "45s": "A 45 S",
    "amg35": "A 35", "amg45": "A 45", "amg45s": "A 45 S"
}
modelli_ord = sorted(motorizzazioni.keys(), key=len, reverse=True)

# Cavalli per modello
mappa_cv = {
    "A 160": 109, "A 180": 136, "A 200": 163, "A 220": 190, "A 250": 224,
    "A 35": 306, "A 45": 387, "A 45 S": 421,
    "A 160 d": 95, "A 180 d": 116, "A 200 d": 150, "A 220 d": 190,
    "A 250 e": 218
}

def estrai_modello(annuncio):
    if not isinstance(annuncio, str):
        return None
    annuncio_norm = re.sub(r"[^\w]", "", annuncio.lower())
    for chiave in modelli_ord:
        if chiave in annuncio_norm:
            return motorizzazioni[chiave]
    return None

def estrai_anni(valore, valore2, valore3):
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

def estrai_allestimento(annuncio):
    annuncio = annuncio.lower()
    for allestimento in allestimenti:
        if allestimento.lower() in annuncio:
            if 'amg line' in annuncio or 'amg-line' in annuncio or 'premium' in annuncio or 'amgline' in annuncio:
                return 'Premium AMG line'
            return allestimento
    return None

def estrai_cv(modello):
    return mappa_cv.get(modello)