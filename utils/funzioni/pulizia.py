import re
import pandas as pd

def pulisci_prezzo(valore):
    if not isinstance(valore, str):
        valore = str(valore)
    matches = re.findall(r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?', valore)
    if not matches:
        return None
    ultimo_prezzo = matches[-1]
    return ultimo_prezzo.replace('.', '').replace(',', '.')

def pulisci_km(valore):
    if valore is None:
        return None
    valore = str(valore).lower()
    valore = re.sub(r'[^\d]', '', valore)
    return int(valore) if valore.isdigit() else None

def pulisci_cambio(valore, valore2):
    if pd.notna(valore):
        valore = str(valore).strip().lower()
        if 'aut' in valore:
            return 'automatico'
        if 'man' in valore:
            return 'manuale'
    if pd.notna(valore2):
        valore2 = str(valore2).strip().lower()
        if 'aut' in valore2 or '':
            return 'automatico'
        if 'man' in valore2:
            return 'manuale'
    return 'automatico'

def pulisci_cambio_dt_merged(valore, valore2, valore3):
    for v in [valore, valore2, valore3]:
        if 'autom' in str(v).strip().lower():
            return 'automatico'
    return 'manuale'

# Carburanti riconosciuti
carburanti_validi = ['Diesel', 'Benzina', 'Ibrido']
def pulisci_carburante(valore, valore2, valore3):
    def normalize(val):
        return '' if pd.isna(val) else str(val).strip().lower()
    carburante_raw = normalize(valore)
    annuncio = normalize(valore2)
    modello = normalize(valore3)
    if 'elettric' in carburante_raw and 'benzina' in carburante_raw:
        return 'Ibrido'
    for c in carburanti_validi:
        if c.lower() in carburante_raw:
            return c
    if any(k in annuncio for k in ['mild', 'plug', 'eq', 'mhv']):
        return 'Ibrido'
    if 'd' in modello:
        return 'Diesel'
    if 'e' in modello:
        return 'Ibrido'
    return 'Benzina'

def pulisci_indirizzo_AT(indirizzo):
    indirizzo = str(indirizzo).replace('IT-', '').strip()
    # Caso ben formattato tipo: "Roma - RM, 00123"
    match = re.match(r'([A-Za-z\s]+)\s-\s([A-Za-z]+),\s*(\d{5})', indirizzo)
    if match:
        citta = match.group(1).strip()
        provincia = match.group(2).strip()
        cap = match.group(3).strip()
        return cap, citta, provincia
    # Caso con "•" o formati meno regolari
    parti = indirizzo.split("•")
    if len(parti) > 1:
        indirizzo = parti[1].strip()
    cap_match = re.search(r'\b\d{5}\b', indirizzo)
    if cap_match:
        cap = cap_match.group(0)
        indirizzo = indirizzo.replace(cap, "").strip()
        parti_indirizzo = indirizzo.split("-")
        if len(parti_indirizzo) == 2:
            citta = parti_indirizzo[0].strip()
            provincia = parti_indirizzo[1].strip()
        elif len(parti_indirizzo) == 1:
            citta = parti_indirizzo[0].strip()
            provincia = None
        else:
            citta = provincia = None
        return cap, citta, provincia
    else:
        return None, None, None
