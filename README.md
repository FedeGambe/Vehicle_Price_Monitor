# 🚗 Vehicle Price Monitor

**Vehicle Price Monitor** è un'applicazione Python per il monitoraggio dei prezzi delle auto usate, con l’obiettivo di identificare le offerte più interessanti tramite analisi oggettive e personalizzabili.

Utilizza tecniche di **web scraping** (AutoScout24) e dataset provenienti da più portali (es. Automobile.it, AutoSupermarket, AutoTorino) usando software di scraping - come Octoparse - per valutare i veicoli secondo parametri come **prezzo, chilometraggio, potenza, allestimento e distanza**.

---

## 📌 Caratteristiche principali

- Estrazione automatica degli annunci (scraping, solo in `VehiclePriceMonitor_AutoscoutScraper.ipynb`)
- Calcolo distanza chilometrica tra annuncio e luogo di residenza
- Valutazione "conveniente / non conveniente"
- Calcolo di un **Indice di Appetibilità personalizzabile**
- Classifica delle **10 migliori offerte**
- Analisi regionale dei prezzi (solo in `Vehicle_Price_Monitor.ipynb`)

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

```
---
Link Colab
-  Vehicle_Price_Monitor: [![Apri su Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1c_pZhJ38KxPhe0YUictMe4ysiB-6GBo3?usp=sharing)
-  VehiclePriceMonitor_AutoscoutScraper: [![Apri su Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VSYNB0qraaoZPC1ZIS_AbRln1viPwnp1?usp=sharing)


---

## 🧠 Come funziona l’Indice di Appetibilità

L’indice è un valore compreso tra 0 e 1 che rappresenta quanto un’auto risulta interessante rispetto alle altre dell’elenco. Per esmpio viene calcolato combinando i seguenti fattori:

| Fattore             | Peso  | Descrizione                                        |
|---------------------|-------|---------------------------------------------------|
| Anno dell'auto      | 0.15  | Auto più recenti sono preferite                   |
| Prezzo              | 0.25  | Prezzo più basso è considerato più appetibile     |
| Chilometraggio      | 0.20  | Meno chilometri percorsi = migliore condizione    |
| Distanza da te      | 0.10  | Più vicina = più comoda e meno costosa da ritirare|
| Allestimento        | 0.30  | Più alto è il livello, maggiore è il punteggio    |
| Potenza (CV)        | 0.10  | Veicoli più potenti ricevono un leggero vantaggio |
| Cambio automatico   | 0.50  | Le auto automatiche ottengono un bonus aggiuntivo |

Tutti i valori sono **normalizzati** per garantire confronti equi tra veicoli con caratteristiche diverse.

---
