# Configurazione

- `<Marca_Modello>.toml`: una per auto (il nome del file è il nome usato nei comandi, es. `Opel_Corsa`).
  Sezioni: `[siti]` (percorso `marca/modello` su ogni sito, come nell'URL), `[ricerca]` (filtri di default, 0 = nessun limite),
  `[allestimenti]` (performance/sport/middle/base), `[mappa_allestimenti]`, `[motorizzazioni]`, `[mappa_cv]`.
  - Si configura solo l'ultima generazione del modello (prima e dopo il restyling): `anno_min` taglia le immatricolazioni della serie precedente.
  - Le chiavi di `[mappa_allestimenti]` si cercano nel titolo in minuscolo, la più lunga per prima; gli spazi contano (`" fr "` trova "FR" anche a fine titolo ma non "freni").
  - Le chiavi di `[motorizzazioni]` si cercano nel titolo senza spazi né punteggiatura, la più lunga per prima. I CV scritti nel titolo ("150cv", "110 kW") hanno la precedenza: `[mappa_cv]` serve quando mancano, quindi indica la potenza più diffusa.
  - Se Subito non ha la pagina del modello, `subito_it` può essere una ricerca nel titolo dentro la marca: `"seat/?q=leon&qso=true"`.
- `utente.toml`: comune di residenza, pesi dell'indice di appetibilità, soglia di prezzo.
- `geo/`: dati dei comuni italiani (CAP, coordinate, distanze).
