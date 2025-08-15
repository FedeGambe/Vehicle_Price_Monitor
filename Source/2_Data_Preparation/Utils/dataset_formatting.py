import pandas as pd
from model_utils import estrai_modello, estrai_allestimento, estrai_cv, estrai_anni, unifica_allestimento
from cleaning_functions import normalizza_testo, pulisci_cambio, pulisci_prezzo, pulisci_km, pulisci_cambio_dt_merged, pulisci_carburante, pulisci_indirizzo_AT
from geopy.distance import geodesic
import os

from data_loader import load_csv_from_relative_path
distanza = load_csv_from_relative_path(['Data', 'Processed_data', '0_Località', 'distanza.csv'])
only_cap_per_comune = load_csv_from_relative_path(['Data', 'Processed_data', '0_Località', 'only_cap_per_comune.csv'])
only_comune_per_cap = load_csv_from_relative_path(['Data', 'Processed_data', '0_Località', 'only_comune_per_cap.csv'])

def data_formatting (data, only_cap_per_comune, distanza, comune_per_analisi, mappa_allestimenti, allestimento_performance, allestimento_sport, allestimento_middle, allestimento_base):
    data = data.merge(only_cap_per_comune[['Regione', 'Comune']], on='Comune', how='left')
    data = data.merge(only_cap_per_comune[['Area', 'Comune']], on='Comune', how='left')
    val_doppi = data['Link'].duplicated()
    print(f"\nCi sono dei valori doppi? {val_doppi.any()}")
    if val_doppi.any() == True:
        print(f"Se si quanti ce ne sono? {val_doppi.sum()}, su un totale di {len(data)}")
        data = data.drop_duplicates(subset='Link', keep='first')
        print("Valori doppi rimossi")
    else:
        print("Non ci sono valori doppi")
    #comune_riferimento = str(input("Inserisci il tuo comune di residenza")) # Filtra il comune di riferimento
    
    comune_riferimento = comune_per_analisi #"Sant'Agata Bolognese" # Filtra il comune di riferimento
    comune_riferimento = normalizza_testo(comune_riferimento)
    comune_rif = distanza[distanza['Comune'] == comune_riferimento]

    # Estrazione latitudine e longitudine per il comune di riferimento
    lat_rif = comune_rif['Latitudine'].values[0]
    lon_rif = comune_rif['Longitudine'].values[0]

    # Funzione per calcolare la distanza tra il comune di riferimento e gli altri comuni
    def calcola_distanza(lat1, lon1, lat2, lon2):
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    # Calcolare la distanza per tutti gli altri comuni
    distanza['Distanza'] = distanza.apply(
        lambda row: calcola_distanza(
            lat_rif,
            lon_rif,
            row['Latitudine'],
            row['Longitudine'])
        , axis=1)
    data = data.merge(distanza[['Comune', 'Distanza']], on='Comune', how='left')
    data['Distanza'] = data['Distanza'].round(2)
    if 'Località' in data.columns:
        data = data.drop(columns=['Località'])
    data['Venditore'] = data['Venditore'].fillna('Rivenditore') #riempire i valori vuoti con Rivenditori, in quanto non sono provati
    #data['Cambio'] = data.apply(lambda row: pulisci_cambio_dt_merged(row['Cambio'], row['Annuncio'], row['Link']), axis=1) #nel caso non rilevi dei cambi
    data ['Anni'] = data.apply(lambda row: estrai_anni(row['Immatricolazione'], row['Chilometraggio'], row['Prezzo']), axis=1) #calcolo Anni
    data = data.dropna(subset=['Annuncio']) #Per ricavare l'allestimento
    data['Allestimento'] = data['Annuncio'].apply(lambda x: estrai_allestimento(x, mappa_allestimenti))
    data["Allestimento_unificato"] = data["Allestimento"].apply(
        lambda x: unifica_allestimento(x, allestimento_performance, allestimento_sport, allestimento_middle, allestimento_base))
    cols = [c for c in data.columns if c != 'Modello']
    data = data.dropna(subset=cols)
    #print('*****   DEBUG', data.shape,'   ******')
    for col in ['Prezzo', 'Immatricolazione', 'Chilometraggio', 'CV', 'Distanza', 'CAP', 'Anni']:
        data[col] = data[col].astype(int)
    #Nuovo Ordine
    data = data[['Annuncio', 'Link', 'Prezzo', 'Anni' ,'Immatricolazione', 'Chilometraggio', 'Cambio',
                'Carburante', 'CV', 'Allestimento','Allestimento_unificato','Modello','Venditore', 'Distanza','Comune', 'CAP', 'Regione', 'Area']]
    return data


def get_data_dummy (data, allestimento_performance, allestimento_sport, allestimento_middle):
    data_dummy = data.copy()
    data_dummy= data_dummy.drop(columns=['Annuncio', 'Link', 'Comune','Immatricolazione', 'CAP', 'Modello', 'Regione' ,'Allestimento_unificato'],errors='ignore')
    data_dummy['Cambio'] = data_dummy['Cambio'].map({'automatico': 1, 'manuale': 0})
    data_dummy['Venditore'] = data_dummy['Venditore'].map({'Privato': 0, 'Rivenditore': 1})
    carburanti = pd.unique(data_dummy['Carburante'])
    for carburante in carburanti:
        if carburante != 'Benzina': # Benzina = baseline
            data_dummy[f'is_{carburante} vs Benzina'] = data_dummy['Carburante'].apply(lambda x: 1 if x == carburante else 0)
    data_dummy.drop(columns=['Carburante'], inplace=True)
    data_dummy['is_sport vs base'] = data_dummy['Allestimento'].isin(allestimento_sport).astype(int)
    data_dummy['is_performance vs base'] = data_dummy['Allestimento'].isin(allestimento_performance).astype(int)
    data_dummy['is_middle vs base'] = data_dummy['Allestimento'].isin(allestimento_middle).astype(int)
    data_dummy.drop(columns=['Allestimento'], inplace=True)
    #for allestimento in allestimenti:
    nord_e = ['Nord-est'] # baseline
    nord_o = ['Nord-ovest']
    centro = ['Centro']
    sud_isole = ['Sud', 'Isole']

    data_dummy['is NO vs NE']= data_dummy['Area'].isin(nord_o).astype(int)
    data_dummy['is Centro vs NE']= data_dummy['Area'].isin(centro).astype(int)
    data_dummy['is Sud_Isole vs NE']= data_dummy['Area'].isin(sud_isole).astype(int)
    data_dummy.drop(columns=['Area'], inplace=True)
    return data_dummy
    