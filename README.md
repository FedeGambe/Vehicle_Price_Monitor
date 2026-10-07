# Vehicle Price Monitor

**Auto Price Monitor** è un programma completo per la **raccolta**, **preparazione**, **analisi** e **predizione** dei prezzi delle auto usate in Italia.  
L'obiettivo è supportare gli utenti nella valutazione delle offerte disponibili online, stimando il prezzo corretto e fornendo un'analisi personalizzata delle migliori opportunità sul mercato.

---

## Funzionalità principali

- **Web Scraping automatizzato** da siti italiani di annunci auto:
  - [x] autoscout24.it
  - [x] automobile.it
  - [x] subito.it
  - [x] autosupermarket.it
- **Pulizia e preparazione dati** multi-sorgente
- **Analisi geografica e di convenienza**:
  - Calcolo della **distanza chilometrica** tra l'annuncio e il luogo di residenza dell'utente
  - **Valutazione del prezzo** come *conveniente* o *non conveniente* rispetto al mercato
- **Indice di Appetibilità** configurabile:
  - Ponderazione delle caratteristiche preferite (es. chilometraggio, potenza, anno, prezzo)
- **Classifica delle migliori offerte** in base alle preferenze dell’utente
- **Predizione del prezzo di mercato** con modelli di machine learning
- **Dashboard HTML** (`docs/index.html`): pagina unica che si apre con doppio clic. Calcolatore sovra/sotto prezzo e classifica delle migliori offerte, senza server né modelli da caricare

---

## Come si usa il programma

```bash
pip install -e .                                   # una volta sola (Python >= 3.11)

python -m vehicle_price_monitor modelli            # auto configurate
python -m vehicle_price_monitor run Opel_Corsa     # scrape + prepare + train + dashboard
python -m vehicle_price_monitor run tutti          # tutte le auto configurate
```

Poi apri **`docs/index.html`** nel browser.

Ogni fase si può lanciare da sola (`python -m vehicle_price_monitor -h` per le opzioni):

| Comando | Cosa fa | Output |
|---|---|---|
| `scrape MODELLO` | scarica gli annunci dai 4 siti (`--siti`, `--max-pages`, `--prezzo-max 20000`, `--anno-min 2022`, ...) | `data/raw/<Modello>/` |
| `prepare MODELLO` | pulisce, unisce, calcola distanze e variabili dummy (`--comune`) | `data/processed/<Modello>/` |
| `train MODELLO` | addestra la Random Forest | `data/models/<Modello>/` |
| `top MODELLO` | classifica nel terminale (`--prezzo-max`, `--km-max`, `--dist-max`, `-n`) | stampa |
| `dashboard` | rigenera la pagina HTML | `docs/index.html` |
| `run MODELLO` | scrape + prepare + train + dashboard (`--senza-scraping` riusa i grezzi) | tutto |

Lo scraping apre Chrome (Subito e Autosupermarket lo richiedono): è normale che compaiano delle finestre.

### Pubblicare con GitHub Pages

La dashboard è in `docs/index.html`. Dopo il push: **Settings → Pages → Source: Deploy from a branch → branch `main`, cartella `/docs`**.
Il sito sarà su `https://<utente>.github.io/Vehicle_Price_Monitor/`. Per aggiornarlo: `python -m vehicle_price_monitor run tutti`, poi commit e push.

### Configurazione (`data/config/`)

- **`<Marca_Modello>.toml`**: una per auto. Contiene lo slug di ogni sito, i filtri di ricerca di default, gli allestimenti per segmento, le motorizzazioni e i CV. Per aggiungere un'auto copia un file esistente e cambia i valori (il nome del file è il nome del modello).
- **`utente.toml`**: il tuo comune di residenza, i pesi dell'indice di appetibilità e la soglia di prezzo.
- **`geo/`**: comuni, CAP e distanze.

## Struttura del progetto

```plaintext
Vehicle_Price_Monitor/
├── vehicle_price_monitor/        # Pacchetto Python (si lancia con python -m vehicle_price_monitor)
│   ├── __main__.py               # Riga di comando
│   ├── pipeline.py               # scrape / prepare / train / top
│   ├── dashboard.py              # Genera docs/index.html
│   ├── paths.py                  # Percorsi e lettura dei TOML
│   ├── scraping/                 # url_builders, scraping_functions
│   ├── preparation/              # pulizia e formattazione dataset
│   └── analysis/                 # price_analysis (OLS, RF, appetibilità), plots
├── docs/
│   ├── index.html                # La dashboard (generata, servita da GitHub Pages)
│   ├── template.html             # Struttura e stile della pagina
│   └── copertina.svg             # Copertina
├── data/
│   ├── config/                   # <Modello>.toml, utente.toml, geo/
│   ├── raw/<Modello>/            # output grezzo dello scraping
│   ├── processed/<Modello>/      # dataset puliti
│   └── models/<Modello>/         # modelli ML salvati (.pkl)
├── archive/                      # Vecchi notebook, Projects/, main deprecato
├── pyproject.toml
└── requirements.txt
```
