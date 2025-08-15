import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics.tsaplots import plot_acf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, classification_report
import joblib
import os

def vif_analysis(X,y, modello_analizzato):
    X = X.astype(float)
    y = y.astype(float)
    X_cons = sm.add_constant(X)
    vif_data = pd.DataFrame()
    vif_data['Variable'] = X_cons.columns
    vif_data['VIF'] = [variance_inflation_factor(X_cons.values, i) for i in range(X_cons.shape[1])]
    print(f"Valori VIF per l'analisi del veicolo: {modello_analizzato}")
    print(vif_data)
    
def model_OLS(X, y, modello_analizzato):
    print(f"Risultati della OLS reg. per l'analisi del veicolo: {modello_analizzato}")
    X_cons = sm.add_constant(X)
    model = sm.OLS(y, X_cons)
    results = model.fit()
    print(results.summary())

    residui = results.resid     # Plot dell'autocorrelazione dei residui
    plot_acf(residui)
    plt.title('Autocorrelazione dei residui')
    plt.show()

    coefficienti_b = round(results.params, 3)
    p_value = round(results.pvalues, 3)
    standard_errors = round(results.bse, 3)
    tabella_diz = {'Coefficienti': coefficienti_b,'P-value': p_value,'Standard Error': standard_errors}
    tabella_riass = pd.DataFrame(tabella_diz)
    tabella_sign = tabella_riass[tabella_riass['P-value'] < 0.05]
    tabella_sign['indice'] = range(len(tabella_sign))
    
    return tabella_sign, tabella_riass, results
        
        

def modello_ml(X, y, path_modello, test_size=0.2):
    os.makedirs(path_modello, exist_ok=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    sc = StandardScaler()
    X_train_scaled = pd.DataFrame(sc.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(sc.transform(X_test), columns=X_test.columns, index=X_test.index)
    # Modello
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train_scaled, y_train)
    # Salvataggio del modello e dello scaler
    joblib.dump(model, f'{path_modello}/modello_rf.pkl')
    joblib.dump(sc, f'{path_modello}/scaler_rf.pkl')
    # Valutazione sul test set
    y_pred_test = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred_test)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred_test)
    joblib.dump(mse, f'{path_modello}/mse_rf.pkl')
    joblib.dump(rmse, f'{path_modello}/rmse_rf.pkl') 
    joblib.dump(r2, f'{path_modello}/r2_rf.pkl') 
    cols_model = X.columns.tolist()
    cols_to_remove = ['prezzo_previsto', 'delta_prezzo', 'is_conveniente']
    cols_model = [col for col in cols_model if col not in cols_to_remove]
    joblib.dump(cols_model, f'{path_modello}/cols_model.pkl')
    print("Valutazione delle performance sul test set")
    print(f" - Mean Squared Error: {round(mse, 2)}")
    print(f" - Root Mean Squared Error: {round(rmse, 2)} euro")
    print(f" - R-squared:  {round(r2, 2)}")
    
def predizione_prezzo(data_ml, X, path_modello):
    model =joblib.load(f'{path_modello}/modello_rf.pkl')
    sc = joblib.load(f'{path_modello}/scaler_rf.pkl')
    X_scaled_all = pd.DataFrame(sc.transform(X), columns=X.columns, index=X.index)
    y_pred_all = model.predict(X_scaled_all)
    data_ml['prezzo_previsto'] = y_pred_all.round(2)
    data_ml['delta_prezzo'] = round(data_ml['prezzo_previsto'] - data_ml['Prezzo'],2)
    data_ml['is_conveniente'] = (data_ml['delta_prezzo'] > 100).astype(int)
    return data_ml, y_pred_all


def is_conveniente_class_report (data_ml):
    y_class = data_ml['is_conveniente']
    X = data_ml.drop(columns=['Prezzo'])
    sc = StandardScaler()
    X_scaled = sc.fit_transform(X)
    X = pd.DataFrame(X_scaled, columns=X.columns)
    X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)
    model_class = RandomForestClassifier(n_estimators=100, random_state=42)
    model_class.fit(X_train, y_train)
    y_pred_class = model_class.predict(X_test)
    print(classification_report(y_test, y_pred_class))

def indice_appetibilita (data, y_pred, prezzo_soglia, valore_idx_anni, valore_idx_prezzo, valore_idx_km,
                         valore_idx_dist, valore_idx_allestimento, valore_idx_cv, valore_idx_cambio,
                         allestimento_performance, allestimento_sport,allestimento_middle,allestimento_base ):
    #Funzioni utili per la creazione dell'indice
    def normalizzata_inv(value, min_value, max_value):
        return (max_value - value) / (max_value - min_value)
    def normalizzata(value, min_value, max_value):
        return (value - min_value) / (max_value - min_value)
    def allestimento_score(allestimento):
        if allestimento in allestimento_sport or allestimento in allestimento_performance:
            return 1
        elif allestimento in allestimento_middle:
            return 0.4
        elif allestimento in allestimento_base:
            return 0.1
        return 0
    def prezzo_score(x, prezzo_min, prezzo_max):
        soglia = prezzo_soglia
        if x <= soglia : # Normalizzazione inversa per i prezzi <= soglia
            return (prezzo_max - x) / (prezzo_max - prezzo_min)
        else:
            # Penalizzazione esponenziale severa per i prezzi > 35.000
            base_score = (prezzo_max - soglia) / (prezzo_max - prezzo_min)
            penalty = np.exp(-0.1 * (x - soglia))
            return base_score * penalty
        
    anni_norm = data['Anni'].apply(lambda x: normalizzata_inv(x, data['Anni'].min(), data['Anni'].max()))
    prezzo_norm = data['Prezzo'].apply(lambda x: prezzo_score(x, data['Prezzo'].min(), data['Prezzo'].max()))
    chilometraggio_norm = data['Chilometraggio'].apply(lambda x: normalizzata_inv(x, data['Chilometraggio'].min(), data['Chilometraggio'].max()))
    distanza_norm = data['Distanza'].apply(lambda x: normalizzata_inv(x, data['Distanza'].min(), data['Distanza'].max()))
    cv_norm = data['CV'].apply(lambda x: normalizzata(x, data['CV'].min(), data['CV'].max()))
    allestimento_score_col = data['Allestimento'].apply(allestimento_score)
    cambio_scorre = data['Cambio'].map({'automatico': 1, 'manuale': 0})
    
    # Calcolo dell'indice appetibilità
    data['Indice_Appetibilità'] = (
        valore_idx_anni * anni_norm +              #Anni bassi è migliore
        valore_idx_prezzo * prezzo_norm +            #Prezzo basso è migliore
        valore_idx_km * chilometraggio_norm +    #Chilometraggio basso è migliore
        valore_idx_dist * distanza_norm +          #Distanza bassa è migliore
        valore_idx_allestimento * allestimento_score_col + #Allestimento
        valore_idx_cv * cv_norm +                #CV alto è migliore
        valore_idx_cambio * cambio_scorre           #Cambio automatico è migliore
    )
    data['Indice_Appetibilità'] = data['Indice_Appetibilità'].round(2) 
    data['prezzo_previsto'] = y_pred.round(2)
    data['delta_prezzo'] = round(data['prezzo_previsto'] - data['Prezzo'],2)
    data['is_conveniente'] = (data['delta_prezzo'] > 100).astype(int)
    return data
    
from IPython.display import display, HTML
def display_top_auto(df,n_display, prezzo_max, prezzo_min, km_max, km_min, dist_max, carburante=None):
    # Filtro sia per prezzo che per km e distanza
    filtro = (
        (df['Prezzo'] <= prezzo_max) & (df['Prezzo'] > prezzo_min) &
        (df['Chilometraggio'] <= km_max) & (df['Chilometraggio'] > km_min) &
        (df['Distanza'] <= dist_max)
    )
    
    # Se è specificato il carburante, aggiungo anche questo filtro
    if carburante is not None:
        filtro = filtro & (df['Carburante'] == carburante)
    
    filtered_df = df[filtro]
    top_X = filtered_df.nlargest(n_display, 'Indice_Appetibilità')

    print(f"Le migliori {n_display} auto secondo l'indice di appetibilità sono:")
    for _, row in top_X.iterrows():
        link = row['Link']
        display(HTML(f"Indice {row['Indice_Appetibilità']:.2f} → <a href='{link}' target='_blank'>{link}</a>"))
    print()
    display(top_X)