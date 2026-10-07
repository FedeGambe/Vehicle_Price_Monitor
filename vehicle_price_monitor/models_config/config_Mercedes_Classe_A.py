# Configurazione specifica per Mercedes Classe A
allestimenti = sorted([
    "Sport", "Business", "AMG", "AMG line", "amg-line", "amgline","Elegance",
    "Premium", "Advanced", "Progressive", "Executive"
], key=lambda x: -len(x))

# Mappatura nomi allestimenti a nomi standardizzati (tutto in minuscolo per mappatura più robusta)
mappa_allestimenti = {
    "amg line": "AMG line",
    "amg-line": "AMG line",
    "ameline": "AMG line",
    "premium": "AMG line",
    "amg": "AMG",
    "sport": "Sport",
    "business": "Business",
    "elegance": "Elegance",
    "advanced": "Advanced",
    "progressive": "Progressive",
    "executive": "Executive"
}

allestimento_performance = ["AMG"]
allestimento_sport = ["AMG line"]
allestimento_middle = ["Progressive", "Advanced","Elegance", "Sport"]
allestimento_base = ["Business","Executive"]

motorizzazioni = {
    "a160": "A 160", "a180": "A 180", "a200": "A 200", "a220": "A 220", "a250": "A 250",
    "a35": "A 35", "a45": "A 45", "a45s": "A 45 S", "a160d": "A 160 d", "a180d": "A 180 d",
    "a200d": "A 200 d", "a220d": "A 220 d", "a250e": "A 250 e"
}
modelli_ord = sorted(motorizzazioni.keys(), key=len, reverse=True)

mappa_cv = {
    "A 160": 109, "A 180": 136, "A 200": 163, "A 220": 190, "A 250": 224,
    "A 35": 306, "A 45": 387, "A 45 S": 421,
    "A 160 d": 95, "A 180 d": 116, "A 200 d": 150, "A 220 d": 190, "A 250 e": 218
}