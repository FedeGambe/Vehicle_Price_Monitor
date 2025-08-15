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

> 🟢 **L'utente deve utilizzare esclusivamente i notebook presenti nella cartella `Application/`.**  
> Non è necessario modificare o eseguire manualmente altri file all'interno del progetto.

### Passaggi da seguire:

1. **Personalizza le configurazioni dei modelli auto nei file presenti in `Data/config/`** creando un file .py

2. **Vai nella cartella `Application/`**

3. **Esegui i notebook nell'ordine indicato:**
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
├── Scraping/                  # Estrazione automatica dei dati online
├── Data_Preparation/         # Pulizia, unificazione e preparazione dei dataset
├── Data_Analysis/            # Analisi esplorativa, geolocalizzazione, ML
├── Materiali/                # Dataset grezzi, dati puliti e file di configurazione
├── Progetti/                 # Analisi dedicate a modelli auto specifici
├── Programma/                # Notebook guida per l’esecuzione completa
└── README.md                 # Questo file
