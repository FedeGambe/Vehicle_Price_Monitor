import pandas as pd
import sys
import os
import importlib
from Utils.data_loader import load_csv_from_relative_path
from Data_Preparation.Utils.dataset_cleaning import data_formatting,clean_data_AS,clean_data_AT,clean_data_AR,clean_data_ASM, clean_data_SU, get_data_dummy

# --- 1. IMPORTAZIONI INIZIALI per il modello e il comune da analizzare ---
comune_per_analisi = "Sant'Agata Bolognese" #Inserire il comune dal quale si vuole calcolare la distanza dell'annuncio dell'auto
modello_per_analisi = 'Opel_Corsa'  
# Opzioni possibili: Mercedes_Classe_A, BMW_Serie_1, Audi_A3, Fiat_Panda
print()
print("-" * 100)
print(f'\nNUOVO RUN per la creazione dei dataset: Data e Data_dummy, per il veicolo: {modello_per_analisi}\n')
print("-" * 100,"\n")


# --- IMPORT CONFIGURAZIONE DELL'AUTO ---
#Configurazione path per import dinamico del modulo di configurazione 
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'config'))
if config_path not in sys.path:
    sys.path.append(config_path)
print("\n - config_path:", config_path)
print(" - Contenuto della cartella:", os.listdir(config_path))
# --- Import dinamico del modulo di configurazione in base al modello ---
modulo_config = f"config_{modello_per_analisi}"  # esempio: config_Mercedes_Classe_A
try:
    config = importlib.import_module(modulo_config)
except ModuleNotFoundError:
    print(f"❌ Modulo di configurazione '{modulo_config}' non trovato.")
    sys.exit(1)
# --- Accesso ai parametri di configurazione ---
#allestimenti = config.allestimenti
allestimento_performance = config.allestimento_performance
allestimento_sport = config.allestimento_sport
allestimento_middle = config.allestimento_middle
allestimento_base = config.allestimento_base
mappa_allestimenti = config.mappa_allestimenti
motorizzazioni = config.motorizzazioni
modelli_ord = config.modelli_ord
mappa_cv = config.mappa_cv

# --- 2. CARICAMENTO DATAFRAME DA FILE CSV ---
# Dati località e distanza
distanza = load_csv_from_relative_path(['Materiali', 'Data', '0_Località', 'distanza.csv'])
only_cap_per_comune = load_csv_from_relative_path(['Materiali', 'Data', '0_Località', 'only_cap_per_comune.csv'])
only_comune_per_cap = load_csv_from_relative_path(['Materiali', 'Data', '0_Località', 'only_comune_per_cap.csv'])
# Dataset auto grezzi per il modello selezionato
data_AS = load_csv_from_relative_path(['Materiali', 'Dataset_grezzi', modello_per_analisi, 'data_autoscout.csv'])
data_AT = load_csv_from_relative_path(['Materiali', 'Dataset_grezzi', modello_per_analisi, 'data_automobile_it.csv'])
data_ASM = load_csv_from_relative_path(['Materiali', 'Dataset_grezzi', modello_per_analisi, 'data_autosupermarket.csv'])
data_SU = load_csv_from_relative_path(['Materiali', 'Dataset_grezzi', modello_per_analisi, 'data_subito_it.csv'])
#data_AR = load_csv_from_relative_path(['Materiali', 'Dataset_grezzi', modello_per_analisi, 'data_autotorino.csv'])

# --- 3. PULIZIA DEI DATAFRAME SINGOLI ---
# Utilizzo delle funzioni di pulizia importate per ogni dataset
data_AS = clean_data_AS(data_AS, only_comune_per_cap, motorizzazioni, modelli_ord, mappa_cv)
data_AT = clean_data_AT(data_AT, only_cap_per_comune, motorizzazioni, modelli_ord, mappa_cv)
data_ASM = clean_data_ASM(data_ASM, motorizzazioni, modelli_ord)
data_SU = clean_data_SU(data_SU, only_cap_per_comune, modelli_ord, motorizzazioni,mappa_cv)
#data_AR = clean_data_AR(data_AR, only_cap_per_comune, motorizzazioni, modelli_ord, mappa_cv)

# --- 4. UNIONE DEI DATAFRAME PULITI ---
data = pd.concat([data_AS, data_AT, data_ASM, data_SU
                  #data_AR
                  ], ignore_index=True)
# Output diagnostico per verificare l'unione
print("\n✅ Dataset unificato caricato correttamente.")
print(f"Numero di righe: {data.shape[0]}")
print(f"Numero di colonne: {data.shape[1]}")
print("\n📋 Informazioni dettagliate per il dataframe NON FORMATTATO:")
data.info()
print()

# --- 5. FORMATTAZIONE DEL DATAFRAME UNITO ---
data_formattato = data_formatting(data, only_cap_per_comune, distanza, comune_per_analisi, mappa_allestimenti, allestimento_performance, allestimento_sport, allestimento_middle, allestimento_base)
print("\n📋 Informazioni dettagliate per il dataframe FORMATTATO:")
data_formattato.info()
print()
# Visualizzazione dei valori unici delle colonne categoriali (escluse alcune colonne informative)
exclude_columns = ["località", "CAP", "Comune", "Annuncio", "Link", "Regione"]
object_columns = [
    col for col in data_formattato.select_dtypes(include='object').columns 
    if col not in exclude_columns]
for column in object_columns:
    print("\nValori unici delle variabili Categoriali, riferite ai veicoli:")
    print(f"Colonna: {column}: {data_formattato[column].unique()}")
    print("-" * 40)

# --- 6. CREAZIONE DF DUMMY X ANALISI ---
data_dummy = get_data_dummy(data_formattato, allestimento_performance, allestimento_sport, allestimento_middle)
print("\n📋 Informazioni per il dataframe DUMMY:")
data_dummy.info()

# --- 7. SALVATAGGIO DEI DATAFRAME ---
output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Data', modello_per_analisi))
os.makedirs(output_folder, exist_ok=True)  
# Salvataggio versione NON formattata (NF)
data.to_csv(os.path.join(output_folder, f"data_NF_{modello_per_analisi}NF.csv"), index=False)
# Salvataggio versione FORMATTATA
data_formattato.to_csv(os.path.join(output_folder, f"data_{modello_per_analisi}.csv"), index=False)
# Salvataggio versione DUMMY
data_dummy.to_csv(os.path.join(output_folder, f"data_dummy_{modello_per_analisi}.csv"), index=False)

# --- FINE PROGRAMMA ---
print("\n" + "="*100)
print("✅ Programma completato con successo! I dataset sono stati salvati nella cartella:")
print(output_folder)
print("="*100 + "\n")