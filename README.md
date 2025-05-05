# Vehicle Price Monitor
## AutoScout Scraper & Indice di Appetibilità Auto

**AutoScout Scraper** è un'applicazione Python progettata per analizzare automaticamente gli annunci di auto usate pubblicati su [AutoScout24](https://www.autoscout24.it), con l'obiettivo di aiutarti a individuare i veicoli più interessanti in base a criteri oggettivi e personalizzabili.

Il programma si occupa di scaricare gli annunci da una pagina di ricerca AutoScout, elaborare i dati e restituire un elenco delle **10 auto più appetibili** secondo un indice basato su caratteristiche tecniche, distanza, prezzo e allestimento.

- Link Colab: [![Apri su Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VSYNB0qraaoZPC1ZIS_AbRln1viPwnp1?usp=sharing)
-  [Notebook ipynb](./Vehicle_Price_Monitor/VehiclePriceMonitor_Scaper%20(autoscout).ipynb)
  
---

## 🎯 Cosa fa il programma

- Raccoglie annunci direttamente da AutoScout24 tramite web scraping
- Organizza i dati in un DataFrame
- Calcola automaticamente la **distanza tra la tua residenza e la posizione del veicolo**
- Pulisce e normalizza le variabili numeriche (prezzo, chilometraggio, potenza, età del veicolo)
- Valuta la **qualità dell'allestimento** sulla base delle tue preferenze
- Calcola un **Indice di Appetibilità** personalizzato per ciascun veicolo
- Esegue un'**analisi statistica** per comprendere i fattori che influenzano il prezzo
- Restituisce le **10 migliori occasioni** secondo i tuoi criteri

---

## 🧠 Come funziona l’Indice di Appetibilità

L’indice è un valore compreso tra 0 e 1 che rappresenta quanto un’auto risulta interessante rispetto alle altre dell’elenco. Viene calcolato combinando i seguenti fattori:

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

## 🛠️ Come usare il programma
1.	URL di AutoScout24: incolla il link della pagina risultati che vuoi analizzare (può contenere filtri come marca, modello, fascia di prezzo, ecc.)
2.	Comune di residenza: usato per calcolare la distanza chilometrica da ogni annuncio.
3.	Lista di allestimenti di interesse: inserisci gli allestimenti dell'auto analizzata.
4.	Indice di Appetibilità: personalizza i pesi dell'indice per dare maggiore rilevanza ai fattori che contano di più per te (es. prezzo, chilometraggio, potenza, ecc.).
