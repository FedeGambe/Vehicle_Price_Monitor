import pandas as pd
import os

def load_csv_from_relative_path(relative_path_parts, delimiter=','):
    """
    Carica un file CSV a partire da un percorso relativo (lista di cartelle + nome file).
    
    Args:
        relative_path_parts (list): Lista di stringhe che rappresentano il percorso relativo (es. ['Materiali', 'Data', 'Località', 'distanza.csv']).
        delimiter (str): Delimitatore del file CSV (default: ',').
    
    Returns:
        pd.DataFrame: Il dataframe caricato, o DataFrame vuoto se il file non esiste o non è leggibile.
    """
    import pandas as pd
    import os

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..'))
    full_path = os.path.join(base_path, *relative_path_parts)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ File non trovato: {full_path}")
    
    try:
        df = pd.read_csv(full_path, delimiter=delimiter)
        print(f"✅ File caricato: {full_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")
        return df
    except Exception as e:
        print(f"❌ Errore durante la lettura del file {full_path}: {e}")
        return pd.DataFrame()
    
def load_csv_for_nb(relative_path_parts, delimiter=','):
    """
    Versione per notebook che parte da una directory superiore rispetto alla cwd.
    """
    # Salgo di una cartella (es. da Data_Analysis/ a Vehicle_Price_Monitor/)
    base_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
    full_path = os.path.join(base_path, *relative_path_parts)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ File non trovato: {full_path}")

    try:
        df = pd.read_csv(full_path, delimiter=delimiter)
        print(f"✅ File caricato: {full_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")
        return df
    except Exception as e:
        print(f"❌ Errore durante la lettura del file {full_path}: {e}")
        return pd.DataFrame()
    
def load_csv_for_notebook(base_path, relative_path_parts, delimiter=','):
    """
    Versione per notebook che parte da una directory superiore rispetto alla cwd.
    """
    full_path = os.path.join(base_path, *relative_path_parts)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ File non trovato: {full_path}")

    try:
        df = pd.read_csv(full_path, delimiter=delimiter)
        print(f"✅ File caricato: {full_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")
        return df
    except Exception as e:
        print(f"❌ Errore durante la lettura del file {full_path}: {e}")
        return pd.DataFrame()