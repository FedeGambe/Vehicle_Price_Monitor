import pandas as pd
from Utils.cleaning import normalizza_testo
import sys
import os

#### CAP 
# - Creazione only_cap per comune
# - Creazione only_comune per cap
cap_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Dataset_grezzi', 'Località', 'gi_comuni_cap.csv'))
if cap_path not in sys.path:
    sys.path.append(cap_path)

cap= pd.read_csv(cap_path, delimiter=';')
only_cap = cap[['cap', 'denominazione_ita', 'sigla_provincia','denominazione_regione', 'ripartizione_geografica']]
only_cap = only_cap.rename(columns={'denominazione_ita': 'Comune', 'cap': 'CAP', 'sigla_provincia': 'Provincia', 'ripartizione_geografica': 'Area', 'denominazione_regione': 'Regione'})
only_cap['Comune'] = only_cap['Comune'].apply(normalizza_testo)
only_cap['Provincia'] = only_cap['Provincia'].apply(normalizza_testo)
print("Cap di tutta italia",only_cap.info(), "\n")
only_cap_per_comune = only_cap.sort_values('CAP').drop_duplicates(subset='Comune', keep='first')
only_comune_per_cap = only_cap.sort_values('Comune').drop_duplicates(subset='CAP', keep='first')
print("Cap duplicati eliminati delle grandi città\n",only_comune_per_cap.info(), "\n")
print("Comune duplicati eliminati dai cap\n",only_cap_per_comune.info())
print()

#### DISTANZA
distanza_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Dataset_grezzi', 'Località', 'italy_geo.json'))
if distanza_path not in sys.path:
    sys.path.append(distanza_path)
distanza = pd.read_json(distanza_path)
distanza = distanza.rename(columns={'comune': 'Comune', 'lng': 'Longitudine', 'lat': 'Latitudine'})
print(distanza.info())
distanza['Comune'] = distanza['Comune'].apply(normalizza_testo)
distanza.drop(columns=['istat'], inplace=True)
distanza = distanza.drop([7978, 7979])
print(distanza.head(5))

####OUTPUT
only_cap_per_comune.to_csv(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Data', 'Località', 'only_cap_per_comune.csv'), index=False)
only_comune_per_cap.to_csv(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Data', 'Località', 'only_comune_per_cap.csv'), index=False)
distanza.to_csv(os.path.join(os.path.dirname(__file__), '..', 'Materiali', 'Data', 'Località', 'distanza.csv'), index=False)
