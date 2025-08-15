# Configurazione specifica per Opel Corsa F (dal 2020)
import re

# Lista allestimenti ordinata in base alla lunghezza decrescente per matching più preciso
allestimenti = sorted([
    "GS Line", "GS", "GSLine", "GS-Line" ,"Elegance", "Ultimate", "Edition", "Yes Color Edition", "Yes color", "yescolor", "yes-color"
    "Desing & Tech", "D & T", "Desing&Tech", "D&T", "40 Years", "40Years", "40 anniversario", "40 anni"
], key=lambda x: -len(x))

# Mappatura nomi allestimenti a nomi standardizzati
mappa_allestimenti = {
    "GS-Line": "GS Line", "GSLine": "GS Line",
    "gs": "GS",
    "elegance": "Elegance",
    "ultimate": "Ultimate",
    "edition": "Edition",
    "design & tech": "Desing & Tech", "design&tech": "Desing & Tech", "d & th": "Desing & Tech", "d&": "Desing & Tech",
    "40 anniversario": "40 Anniversario", "40anniversario": "40 Anniversario", "40 anni": "40 Anniversario", "40anni": "40 Anniversario", "40 years": "40 Anniversario", "40years": "40 Anniversario",
    "Yes Color Edition": "Yes Color", "Yes color": "Yes Color", "yescolor": "Yes Color", "yes-color": "Yes Color"
    
}

# Classificazione degli allestimenti per segmento
allestimento_performance = []  # Non ci sono versioni OPC nella F di serie
allestimento_sport = ["GS Line", "GS"]
allestimento_middle = ["Elegance", "Ultimate","Desing & Tech", "Yes Color"]
allestimento_base = ["Edition"]

# Mappatura motorizzazioni (benzina, diesel, elettrico)
motorizzazioni = {
    "1.2 75": "1.2 75cv", "1.2 100": "1.2 100cv", "1.2 130": "1.2 130cv", "1.2": "1.2 75cv",
    "1.5": "1.5 Diesel", "1.5 100": "1.5 Diesel", "1.5 d": "1.5 Diesel"
}

def normalizza(s):
    return re.sub(r"[^\w]", "", s.lower())
# Ricrea il mapping con chiavi normalizzate
motorizzazioni_norm = {normalizza(k): v for k, v in motorizzazioni.items()}
# Ordina chiavi per lunghezza decrescente
modelli_ord = sorted(motorizzazioni_norm.keys(), key=len, reverse=True)

# Mappatura cavalli per ogni motorizzazione
mappa_cv = {
    "1.2 75cv": 75,
    "1.2 100cv": 100,
    "1.2 130cv": 130,
    "1.5 Diesel": 100}