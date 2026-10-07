# Configurazione specifica per Audi A3 8Y

# Lista allestimenti ordinata in base alla lunghezza decrescente per matching più preciso
allestimenti = sorted([
    "S line", "Sline", "S-line", "Business", "Business Advanced", "Business Plus",
    "Advanced", "Identity Black", "Identity Contrast", "Identity Plus", "Identity",
    "Sport", "Design", 'S', 'RS'
], key=lambda x: -len(x))

# Mappatura nomi allestimenti a nomi standardizzati
mappa_allestimenti = {
    "s line": "S line",
    "s-line": "S line",
    "sline": "S line",
    "business advanced": "Business Advanced",
    "business plus": "Business Plus",
    "business": "Business",
    "advanced": "Advanced",
    "identity black": "Identity",
    "identity contrast": "Identity",
    "identity plus": "Identity",
    "identity": "Identity",
    "sport": "Sport",
    "design": "Design",
    "s":"S",
    "rs": "RS"
}

# Classificazione degli allestimenti per segmento
allestimento_performance = ["S", "RS"]
allestimento_sport = ["S line"]
allestimento_middle = ["Advanced", "Business Advanced", "Identity", "Sport", "Design"]
allestimento_base = ["Business", "Business Plus"]

# Mappatura motorizzazioni (benzina, diesel, ibride)
motorizzazioni = {
    "30tfsi": "30 TFSI", "35tfsi": "35 TFSI", "40tfsi": "40 TFSI",
    "35tfsi mhev": "35 TFSI MHEV", "40tfsi mhev": "40 TFSI MHEV",
    "30tdi": "30 TDI", "35tdi": "35 TDI", "40tdi": "40 TDI",
    "45tfsi": "45 TFSI", "s3": "S3", "rs3": "RS3",
    "40tfsi e": "40 TFSI e", "45tfsi e": "45 TFSI e"
}

# Ordine per ricerca ottimale (più lungo prima)
modelli_ord = sorted(motorizzazioni.keys(), key=len, reverse=True)

# Mappatura cavalli per ogni motorizzazione
mappa_cv = {
    "30 TFSI": 110,
    "35 TFSI": 150,
    "40 TFSI": 190,
    "35 TFSI MHEV": 150,
    "40 TFSI MHEV": 190,
    "30 TDI": 116,
    "35 TDI": 150,
    "40 TDI": 190,
    "40 TFSI e": 204,
    "45 TFSI e": 245,
    "45 TFSI": 245,
    "S3": 310,
    "RS3": 400
}