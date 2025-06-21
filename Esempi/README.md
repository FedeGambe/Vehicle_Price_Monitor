# 🚗 Vehicle Price Monitor

**Vehicle Price Monitor** è un'applicazione Python per il monitoraggio dei prezzi delle auto usate, con l’obiettivo di identificare le offerte più interessanti tramite analisi oggettive e personalizzabili.

Utilizza tecniche di **web scraping** (AutoScout24) e dataset provenienti da più portali (es. Automobile.it, AutoSupermarket, AutoTorino) per valutare i veicoli secondo parametri come **prezzo, chilometraggio, potenza, allestimento e distanza**.

---

## 📌 Caratteristiche principali

- ✅ Estrazione automatica degli annunci (scraping)
- ✅ Calcolo distanza chilometrica tra annuncio e luogo di residenza
- ✅ Valutazione "conveniente / non conveniente"
- ✅ Calcolo di un **Indice di Appetibilità personalizzabile**
- ✅ Classifica delle **10 migliori offerte**
- ✅ Analisi regionale dei prezzi (solo in `Vehicle_Price_Monitor.ipynb`)

---

## 📂 Struttura del progetto

```bash
📁 Vehicle-Price-Monitor/
├── VehiclePriceMonitor_AutoscoutScraper.ipynb     # Scraping + analisi per Mercedes Classe A
├── Vehicle_Price_Monitor.ipynb                    # Analisi da CSV + confronto prezzi regionali
├── autoscout_scraper.py                           # Script puro di scraping AutoScout24
├── requirements.txt
├── LICENSE
└── 📁 Esempi/                                      # Notebook di esempio per altri modelli
    ├── Fiat_Panda_Analisi.ipynb
    ├── Audi_A3_Analisi.ipynb
    └── ...
