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
  - [ ] autotorino.it *(in fase di sviluppo)*
- **Pulizia e preparazione dati** multi-sorgente
- **Analisi geografica e di convenienza**:
  - Calcolo della **distanza chilometrica** tra l'annuncio e il luogo di residenza dell'utente
  - **Valutazione del prezzo** come *conveniente* o *non conveniente* rispetto al mercato
- **Indice di Appetibilità** configurabile:
  - Ponderazione delle caratteristiche preferite (es. chilometraggio, potenza, anno, prezzo)
- **Classifica delle migliori offerte** in base alle preferenze dell’utente
- **Predizione del prezzo di mercato** con modelli di machine learning
- **Dashboard predittiva** utilizza un modello di machine learning per prevedere il prezzo di una vettura, in base ai dati inseriti dall’utente, e valutare se rappresenta un buon affare

---

## Come si usa il programma?

> 🟢 **Si usano solo i notebook in `notebooks/`.**

### Setup (una volta)

```bash
pip install -e .        # installa il pacchetto vehicle_price_monitor + dipendenze
```

### Passaggi

1. **Crea la config del modello** in `vehicle_price_monitor/models_config/config_<Marca_Modello>.py` (vedi il README in quella cartella).
2. **Esegui i notebook in `notebooks/` nell'ordine:**
   - `1_Scraping_and_Data_preparation.ipynb`  
     ↳ Scarica i dati dal web e li prepara per l'analisi
   - `2_Understanding_Pricing.ipynb`  
     ↳ Analizza i dati, valuta la distanza, convenienza e appetibilità
   - `3_Price_Prediction.ipynb`  
     ↳ Applica un modello predittivo per stimare il prezzo delle auto
   - `4_Dashboard.ipynb`  
     ↳ Se hai trovato una nuova auto o ti hanno proposto un nuovo prezzo, con la dashboard predittiva: potrai inserire tutti nuovi i parametri per capire se l’offerta è conveniente o meno.

---


## Struttura del progetto

```plaintext
Vehicle_Price_Monitor/
├── notebooks/                    # Unico entry point utente (1→4)
├── vehicle_price_monitor/        # Codice riutilizzabile (pacchetto Python)
│   ├── paths.py                  # Percorsi (ROOT, RAW, PROCESSED, MODELS, GEO) + load_config()
│   ├── models_config/            # config_<Modello>.py: allestimenti, motorizzazioni, CV
│   ├── scraping/                 # url_builders, scraping_functions
│   ├── preparation/              # pulizia e formattazione dataset
│   ├── analysis/                 # price_analysis (OLS, RF, appetibilità), plots
│   └── dashboard.py              # dashboard Dash
├── data/
│   ├── raw/<Modello>/            # output grezzo dello scraping (+ raw/geo)
│   ├── processed/<Modello>/      # dataset puliti (+ processed/geo)
│   └── models/<Modello>/         # modelli ML salvati (.pkl)
├── archive/                      # Materiale storico: vecchi notebook, Projects/, main deprecato
├── pyproject.toml
└── requirements.txt
```
