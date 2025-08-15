import pandas as pd
from model_utils import estrai_modello, estrai_allestimento, estrai_cv, estrai_anni, unifica_allestimento
from cleaning_functions import normalizza_testo, pulisci_cambio, pulisci_prezzo, pulisci_km, pulisci_cambio_dt_merged, pulisci_carburante, pulisci_indirizzo_AT
import requests
from geopy.distance import geodesic
import os


def clean_data_AS(data_AS, only_comune_per_cap, motorizzazioni, modelli_ord, mappa_cv):
    # Riempie valori mancanti in 'Annuncio'
    data_AS['Annuncio'] = data_AS.apply(
        lambda row: row['Annuncio'] if pd.notnull(row['Annuncio']) else (
            f"{row['Marca']} {row['Modello_plus_info']}" if pd.notnull(row.get('Modello_plus_info')) else f"{row['Marca']} {row['Modello']}"
        ), axis=1
    )
    data_AS['Annuncio'] = data_AS['Annuncio'].str.replace(r'\s*\n\s*', ' ', regex=True).str.strip()
    if 'Marca' in data_AS.columns:
        data_AS = data_AS.drop(columns=['Marca'])
    if 'Modello_plus_info' in data_AS.columns:
        data_AS = data_AS.drop(columns=['Modello_plus_info'])        
    data_AS['Modello'] = data_AS.apply(lambda row: estrai_modello(row['Annuncio'], modelli_ord, motorizzazioni) or estrai_modello(row['Link'], modelli_ord, motorizzazioni), axis=1)
    #data_AS['Modello'] = data_AS.apply(lambda row: estrai_modello(row['Annuncio']) or estrai_modello(row['Link']), axis=1)
    data_AS['Prezzo'] = data_AS['Prezzo'].apply(pulisci_prezzo)
    #data_AS = data_AS.drop(data_AS[data_AS['Prezzo'] == 0].index)
    if 'Prezzo_scont' in data_AS.columns:
        data_AS['Prezzo_scont'] = data_AS['Prezzo_scont'].apply(pulisci_prezzo).astype('Int64')
        data_AS['Prezzo'] = data_AS['Prezzo_scont'].combine_first(data_AS['Prezzo'])
        data_AS = data_AS.drop(columns=['Prezzo_scont'])
    data_AS['Chilometraggio'] = data_AS['Chilometraggio'].apply(pulisci_km).astype('Int64')
    data_AS['Immatricolazione'] = pd.to_numeric(data_AS['Immatricolazione'].str.split('/').str[1], errors='coerce').astype('Int64')
    if 'CV' in data_AS.columns:
        estratti = data_AS['CV'].str.extract(r'(?:\(?(\d+)\s?CV\)?)', expand=False)
        data_AS['CV'] = pd.to_numeric(estratti[0], errors='coerce')
        mask_cv_na = data_AS['CV'].isna()
        data_AS.loc[mask_cv_na, 'CV'] = data_AS.loc[mask_cv_na, 'Modello'].map(mappa_cv)
    else:
        data_AS['CV'] = data_AS['Modello'].map(mappa_cv)
    data_AS['Cambio'] = data_AS.apply(lambda row: pulisci_cambio(row['Cambio'], row['Annuncio']), axis=1)
    data_AS['Carburante'] = data_AS.apply(lambda row: pulisci_carburante(row['Carburante'], row['Annuncio'], row['Modello']), axis=1)
    data_AS['Venditore'] = data_AS['Località'].str.contains('privato', case=False, na=False).apply(lambda x: "Privato" if x else "Rivenditore")
    data_AS[['CAP', 'Città', 'Provincia']] = data_AS['Località'].apply(lambda x: pd.Series(pulisci_indirizzo_AT(x)))
    data_AS['CAP'] = data_AS['CAP'].astype('Int64')
    data_AS = data_AS.merge(only_comune_per_cap[['CAP', 'Comune']], on='CAP', how='left')
    data_AS = data_AS.drop(columns=['Provincia', 'Città', 'Località'])
    return data_AS

def clean_data_AT(data_AT, only_cap_per_comune, motorizzazioni, modelli_ord, mappa_cv):
    #data_AT['Modello'] = data_AT.apply(lambda row: estrai_modello(row['Annuncio']) or estrai_modello(row['Link']), axis=1)
    data_AT['Modello'] = data_AT.apply(lambda row: estrai_modello(row['Annuncio'], modelli_ord, motorizzazioni) or estrai_modello(row['Link'], modelli_ord, motorizzazioni), axis=1)
    data_AT['Prezzo'] = data_AT['Prezzo'].apply(pulisci_prezzo).astype('Int64')
    data_AT.loc[data_AT['Chilometraggio'].str.contains('CV', na=False), 'Chilometraggio'] = 0
    data_AT['Chilometraggio'] = data_AT['Chilometraggio'].apply(pulisci_km).astype('Int64')
    data_AT['Immatricolazione'] = data_AT['Immatricolazione'].str.extract(r'(\d{4})').astype('Int64')
    valori_cambio = ['Manuale', 'Automatico', 'Semiautomatico']
    mask_cambio = data_AT['Carburante'].isin(valori_cambio)
    data_AT.loc[mask_cambio, 'Cambio'] = data_AT.loc[mask_cambio, 'Carburante']
    data_AT.loc[mask_cambio, 'Carburante'] = pd.NA
    data_AT['Cambio'] = data_AT.apply(lambda row: pulisci_cambio(row['Cambio'], row['Annuncio']), axis=1)
    data_AT['Carburante'] = data_AT.apply(lambda row: pulisci_carburante(row['Carburante'], row['Annuncio'], row['Modello']), axis=1)
    data_AT = data_AT.rename(columns={'TIpologia': 'Tipologia'})
    data_AT = data_AT.drop(columns=['Unico_Proprietario', 'Tipologia'])
    if 'Unico_Proprietario' in data_AT.columns:
        data_AT = data_AT.drop(columns=['Unico_Proprietario'])
    #data_AT['CV'] = data_AT['Modello'].apply(estrai_cv)
    data_AT['CV'] = data_AT['Modello'].apply(lambda modello: estrai_cv(modello, mappa_cv))
    condizione = (
        data_AT['Immatricolazione'].isnull() &
        (data_AT['Prezzo'] > 29000) &
        (data_AT['Chilometraggio'].isnull() | (data_AT['Chilometraggio'] < 1000))
    )
    data_AT.loc[condizione, 'Immatricolazione'] = 2025
    data_AT[['Comune', 'Provincia']] = data_AT['Località'].str.extract(r'(.+)\s+\((\w{2})\)')
    data_AT['Comune'] = data_AT['Comune'].apply(normalizza_testo)
    data_AT = data_AT.drop(columns=['Località', 'Provincia'])
    data_AT = data_AT.merge(only_cap_per_comune[['CAP', 'Comune']], on='Comune', how='left')
    return data_AT

def clean_data_SU(data_SU, only_cap_per_comune, motorizzazioni, modelli_ord, mappa_cv):
    data_SU = data_SU.drop(columns =['Classe Euro', 'Tipologia'])
    data_SU['Modello'] = data_SU.apply(lambda row: estrai_modello(row['Annuncio'], modelli_ord, motorizzazioni) or estrai_modello(row['Link'], modelli_ord, motorizzazioni), axis=1)
    data_SU['Prezzo'] = data_SU['Prezzo'].apply(pulisci_prezzo)
    data_SU['Chilometraggio'] = data_SU['Chilometraggio'].apply(pulisci_km).astype('Int64')
    data_SU['Chilometraggio'] = data_SU['Chilometraggio'].fillna(0)
    data_SU['Cambio'] = data_SU.apply(lambda row: pulisci_cambio(row['Cambio'], row['Annuncio']), axis=1)
    data_SU['Carburante'] = data_SU.apply(lambda row: pulisci_carburante(row['Carburante'], row['Annuncio'], row['Modello']), axis=1)
    data_SU['Immatricolazione'] = pd.to_datetime(data_SU['Immatricolazione'], errors='coerce').dt.year
    data_SU['CV'] = data_SU['Modello'].apply(lambda modello: estrai_cv(modello, mappa_cv))
    data_SU['Comune'] = data_SU['Località'].apply(normalizza_testo)
    data_SU = data_SU.drop(columns=['Località', 'Provincia'])
    data_SU = data_SU.merge(only_cap_per_comune[['CAP', 'Comune']], on='Comune', how='left')
    return data_SU
    
def clean_data_ASM(data_ASM,motorizzazioni, modelli_ord):
    data_ASM = data_ASM.drop(columns=['Tipologia']) 
    if 'Venditore' in data_ASM.columns:
        data_ASM = data_ASM.drop(columns=['Venditore'])
    if 'Link2' in data_ASM.columns:
        data_ASM = data_ASM.drop(columns=['Link2'])
    data_ASM = data_ASM.rename(columns={'Modello ': 'Annuncio'})
    data_ASM['Annuncio'] = data_ASM['Annuncio'].str.replace(r'\s*\n\s*', ' ', regex=True).str.strip()
    #data_ASM['Modello'] = data_ASM['Link'].apply(estrai_modello)
    data_ASM['Modello'] = data_ASM['Link'].apply(lambda x: estrai_modello(x, modelli_ord, motorizzazioni))
    data_ASM['Prezzo'] = data_ASM['Prezzo'].apply(pulisci_prezzo)
    data_ASM['Chilometraggio'] = data_ASM['Chilometraggio'].apply(pulisci_km).astype('Int64')
    data_ASM['Immatricolazione'] = data_ASM['Immatricolazione'].str.extract(r'(\d{4})').astype('Int64')
    data_ASM['Cambio'] = data_ASM.apply(lambda row: pulisci_cambio(row['Cambio'], row['Annuncio']), axis=1)
    data_ASM['Carburante'] = data_ASM.apply(lambda row: pulisci_carburante(row['Carburante'], row['Annuncio'], row['Modello']), axis=1)
    data_ASM['CV'] = data_ASM['CV'].str.extract(r'(?:\(?(\d+)\s?CV\)?)', expand=False).astype(float)
    if 'Località2' in data_ASM.columns:
        data_ASM['Località'] = data_ASM['Località2'].combine_first(data_ASM['Località'])
        data_ASM = data_ASM.drop(columns=['Località2'])
    data_ASM[['CAP', 'Comune', 'Provincia']] = data_ASM['Località'].str.extract(r'(\d{5})\s+(.+?)\s+\((\w{2})\)')
    data_ASM['Comune'] = data_ASM['Comune'].apply(normalizza_testo)
    data_ASM = data_ASM.drop(columns=['Località', 'Provincia'])
    return data_ASM

def clean_data_AR(data_AR, only_cap_per_comune, motorizzazioni, modelli_ord, mappa_cv):
    data_AR = data_AR.drop(columns=['Tipologia'])
    data_AR['Modello_motore'] = data_AR['Link'].apply(lambda x: estrai_modello(x, modelli_ord, motorizzazioni))
    data_AR['Annuncio'] = data_AR['Marca'] + ' ' + data_AR['Modello'] + ' - ' + data_AR['Modello_motore']
    data_AR = data_AR.drop(columns=['Marca', 'Modello'])
    data_AR = data_AR.rename(columns={'Modello_motore': 'Modello'})
    data_AR['Cambio'] = data_AR.apply(lambda row: pulisci_cambio(row['Cambio'], row['Annuncio']), axis=1)
    data_AR['Prezzo'] = data_AR['Prezzo'].apply(pulisci_prezzo).astype('Int64')
    data_AR['Carburante'] = data_AR.apply(lambda row: pulisci_carburante(row['Carburante'], row['Annuncio'], row['Modello']), axis=1)
    data_AR['Chilometraggio'] = data_AR['Chilometraggio'].apply(pulisci_km).astype('Int64')
    data_AR['CV'] = data_AR['Modello'].map(mappa_cv)
    #Immettere il concessionario AutoTorino più vicino
    data_AR['Comune'] = 'modena'
    data_AR['Comune'] = data_AR['Comune'].apply(normalizza_testo)
    data_AR = data_AR.merge(only_cap_per_comune[['CAP', 'Comune']], on='Comune', how='left')
    return data_AR

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
    data_dummy= data_dummy.drop (columns=['Annuncio', 'Link', 'Comune','Immatricolazione', 'CAP', 'Modello', 'Regione' ,'Allestimento_unificato'])
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
    