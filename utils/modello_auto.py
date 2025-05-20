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