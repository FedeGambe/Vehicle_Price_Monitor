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