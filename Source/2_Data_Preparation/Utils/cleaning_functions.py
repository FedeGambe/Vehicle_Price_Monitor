import re, unicodedata, pandas as pd
from datetime import datetime

#NORM TESTO
def normalizza_testo(testo): # Funzione per rimuovere gli accenti e convertire in minuscolo
    if pd.isnull(testo):
        return testo
    # Rimuove accenti
    testo = unicodedata.normalize('NFKD', testo)
    testo = ''.join([c for c in testo if not unicodedata.combining(c)])
    # Gestione apostrofi
    testo = re.sub(r"(?<! )'(?! )", ' ', testo)
    # Minuscolo
    testo = testo.lower()
    # Rimuove articoli e preposizioni comuni
    testo = re.sub(r'\b(di|del|della|dell|nella|nell|nei|degli|dei|in|alla|alle|ai|al)\b', '', testo)
    # Rimuove punteggiatura
    testo = re.sub(r'[^\w\s]', '', testo)
    # Rimuove spazi multipli
    testo = re.sub(r'\s+', ' ', testo).strip()
    return testo

#PULIZIA DATI
def pulisci_prezzo(valore):
    if pd.isna(valore): # Se è NaN o None
        return None
    if isinstance(valore, (int, float)):     # Se è già un numero, convertilo in int
        return int(valore)
    if not isinstance(valore, str):     # Se non è stringa, convertilo
        valore = str(valore)
    matches = re.findall(r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+', valore)     # Regex per trovare numeri nel formato europeo
    if not matches:
        return None
    ultimo_prezzo = matches[-1]
    numero = ultimo_prezzo.replace('.', '').replace(',', '.')
    try:
        return int(float(numero))
    except Exception:
        return None

def pulisci_km(valore):
    if valore is None:
        return None
    valore = re.sub(r'[^\d.,]', '', str(valore))  # Rimuovo tutto ciò che non è numero, punto o virgola
    if '.' in valore and ',' in valore:     # Se contiene sia punto che virgola, assumo che il punto sia separatore migliaia e la virgola decimale
        valore = valore.replace('.', '').replace(',', '.')
    elif '.' in valore:     # Se contiene solo punti, assumo punto come separatore migliaia
        valore = valore.replace('.', '')
    elif ',' in valore:     # Se contiene solo virgola, la sostituisco con punto
        valore = valore.replace(',', '.')
    try:
        return int(float(valore))
    except ValueError:
        return None

def pulisci_cambio(valore, valore2):
    if pd.notna(valore):
        valore = str(valore).strip().lower()
        if 'aut' in valore:
            return 'automatico'
        if 'man' in valore:
            return 'manuale'
    if pd.notna(valore2):
        valore2 = str(valore2).strip().lower()
        if 'aut' in valore2:
            return 'automatico'
        if 'man' in valore2:
            return 'manuale'
    return 'automatico'

def pulisci_cambio_dt_merged(valore, valore2, valore3):
    if next((v for v in [valore, valore2, valore3] if 'autom' in str(v).strip().lower()), None):
        return 'automatico'
    return 'manuale'

# Carburanti riconosciuti
carburanti_validi = ['Diesel', 'Benzina', 'Ibrido', 'Elettrico', 'GPL', 'Metano']
def pulisci_carburante(valore, valore2, valore3):
    def normalize(val):
        return '' if pd.isna(val) else str(val).strip().lower()
    carburante_raw = normalize(valore)
    annuncio = normalize(valore2)
    modello = normalize(valore3)
    if 'elettric' in carburante_raw and 'benzina' in carburante_raw:
        return 'Ibrido'
    if 'elettric' in carburante_raw and 'diesel' in carburante_raw:
        return 'Ibrido'
    if 'hybrid'in carburante_raw or 'mild' in carburante_raw or 'plug-in' in carburante_raw or 'mhv' in carburante_raw:
        return 'Ibrido'
    for c in carburanti_validi:
        if c.lower() in carburante_raw:
            return c
    if any(k in annuncio for k in ['mild', 'plug', 'eq', 'mhv', 'hybrid', 'fhv', 'full hybrid', 'fhev', 'hev']):
        return 'Ibrido'
    if 'd' in modello:
        return 'Diesel'
    if 'e' in modello:
        return 'Elettrico'
    return 'Benzina'

def pulisci_indirizzo_AT(indirizzo):
    indirizzo = str(indirizzo).replace('IT-', '').strip()
    # Caso ben formattato tipo: "Roma - RM, 00123"
    match = re.match(r'([A-Za-z\s]+)\s-\s([A-Za-z]+),\s*(\d{5})', indirizzo)
    if match:
        citta = match[1].strip()
        provincia = match[2].strip()
        cap = match[3].strip()
        return cap, citta, provincia
    # Caso con "•" o formati meno regolari
    parti = indirizzo.split("•")
    if len(parti) > 1:
        indirizzo = parti[1].strip()
    cap_match = re.search(r'\b\d{5}\b', indirizzo)
    if cap_match:
        cap = cap_match[0]
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
