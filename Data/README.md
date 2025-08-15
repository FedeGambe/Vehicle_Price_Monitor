# ⚙️ Configurazioni Modelli Auto

Questa cartella (`Materiali/config/`) contiene i **file .py di configurazione** specifici per ogni modello di auto da analizzare all'interno del progetto **Auto Price Monitor**.

---

## 📝 Scopo

Ogni file `.py` definisce le informazioni necessarie per:
- Riconoscere correttamente **allestimenti** e **motorizzazioni** presenti negli annunci online
- Standardizzare le sigle e i nomi
- Classificare gli allestimenti in base al livello o prestazioni
- Associare i **CV (cavalli)** alle motorizzazioni
- Permettere un’analisi coerente tra modelli simili

---

## 📄 Struttura di ogni file `.py`

Un file `.py` di configurazione **deve contenere** le seguenti voci:

| Variabile                 | Descrizione                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `allestimenti`           | Lista degli allestimenti (ordinata per lunghezza decrescente)              |
| `mappa_allestimenti`     | Mappa delle varianti testuali → forma standardizzata                       |
| `allestimento_performance` | Lista di allestimenti sportivi/ad alte prestazioni                       |
| `allestimento_sport`     | Allestimenti con look sportivo ma non prestazionali                        |
| `allestimento_middle`    | Allestimenti intermedi                                                      |
| `allestimento_base`      | Allestimenti base                                                           |
| `motorizzazioni`         | Mappa sigle tecniche → forma leggibile/standardizzata                      |
| `modelli_ord`            | Lista ordinata delle chiavi di `motorizzazioni`, utile per il parsing      |
| `mappa_cv`               | Mappa delle motorizzazioni → cavalli (CV)                                  |

---

## 📁 Esempio: `audi_a3_8y.py`

Questo file è un **esempio di configurazione** per il modello *Audi A3 8Y (inclusi S3 e RS3)*.  
Può essere usato come modello di partenza per altri file.

Contiene:
- Lista degli allestimenti reali (es. S line, Business, Advanced…)
- Mappature per correggere nomi scritti in modo errato o abbreviato
- Categorie di allestimenti per calcolo indice appetibilità
- Mappa delle motorizzazioni e relativi cavalli

---

## 📤 Dove viene usato?

Le configurazioni vengono importate automaticamente durante:
- la **preparazione dei dati**
- l'**analisi delle offerte**
- il calcolo dell'**indice di appetibilità**

---

## 💡 Suggerimenti

- Prendi d'esempio uno dei file già creati e aiutati con ChatGPT

---
