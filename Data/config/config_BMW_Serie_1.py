# Configurazione specifica per BMW Serie 1 F40

allestimenti = sorted([
    "Advantage", "Business", "Sport", "Sport Line", "Sport-Line", "MSport", "M Sport","M-Sport", "M", 
    "Luxury", "Executive", "Edition"
], key=lambda x: -len(x))

mappa_allestimenti = {
    "m sport": "M Sport",
    "msport": "M Sport",
    "m-sport": "M Sport",
    "sport line": "Sport Line",
    "sport-line": "Sport Line",
    "advantage": "Advantage",
    "business": "Business",
    "sport": "Sport Line",
    "luxury": "Luxury",
    "executive": "Executive",
    "edition": "Edition",
    "m": "M"  # eventualmente da rimuovere se ti dà falsi positivi
}

allestimento_performance = ["M"]
allestimento_sport = ["M Sport"]
allestimento_middle = ["Executive", "Luxury", "Sport Line"]
allestimento_base = ["Edition","Advantage", "Business"]

motorizzazioni = {
    "116i": "116i", "118i": "118i", "120i": "120i", "128ti": "128ti",
    "m135i": "M135i xDrive", "116d": "116d", "118d": "118d", "120d": "120d",
    "120dx": "120d xDrive", "m135ix": "M135i xDrive"
}
modelli_ord = sorted(motorizzazioni.keys(), key=len, reverse=True)

mappa_cv = {
    "116i": 109, "118i": 136, "120i": 178, "128ti": 265,
    "M135i xDrive": 306, "116d": 116, "118d": 150, "120d": 190,
    "120d xDrive": 190
}