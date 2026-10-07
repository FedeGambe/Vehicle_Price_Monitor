import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


#########################################################################
#  Funzione per la creazione del df dummy, SOLO PER ANALISI DASHBOARD   #
#########################################################################
def get_data_dummy_for_dash (data, data_originale, allestimento_performance, allestimento_sport, allestimento_middle):
    data_dummy = data.copy()
    data_dummy= data_dummy.drop(columns=['Annuncio', 'Link', 'Comune','Immatricolazione', 'CAP', 'Modello', 'Regione' ,'Allestimento_unificato'],errors='ignore')
    data_dummy['Cambio'] = data_dummy['Cambio'].map({'automatico': 1, 'manuale': 0})
    data_dummy['Venditore'] = data_dummy['Venditore'].map({'Privato': 0, 'Rivenditore': 1})
    carburanti = pd.unique(data_originale['Carburante'])
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

################################################
#  Funzione per la creazione della DASHBOARD   #
################################################
def create_dashboard(modello_per_analisi, data_originale, allestimenti, carburanti, allestimento_performance,
                     allestimento_sport, allestimento_middle, model_ml, scaler_ml, val_metrics, cols_model, get_data_dummy_for_dash):
    def preprocess_data(data):
        scaled_data = scaler_ml.transform(data)
        return pd.DataFrame(scaled_data, columns=data.columns)

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container([
        html.H1(f"Dashboard di Predizione del prezzo di {modello_per_analisi}",
                className="text-center mt-4 mb-4"),

        # ----------------------------
        # Input: Prezzo, Anni, Chilometraggio
        # ----------------------------
        dbc.Row([
            dbc.Col([html.Label("Prezzo"),dcc.Input(id='prezzo', type='number', value=1.0, min=1000, max=500000, className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("Anni"),dcc.Input(id='anni', type='number', value=1.0, min=0, max=100, className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("Chilometraggio"),dcc.Input(id='km', type='number', value=1.0, min=0, max=500000, className='form-control')], width=6, className='mb-3'),
        ]),

        # ----------------------------
        # Input: Cambio, CV, Allestimento
        # ----------------------------
        dbc.Row([
            dbc.Col([html.Label("Cambio"),dcc.Dropdown(id='cambio',options=[{'label': 'Automatico', 'value': 'automatico'},{'label': 'Manuale', 'value': 'manuale'}],value='automatico', className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("CV"),dcc.Input(id='cv', type='number', value=1.0, min=0, max=1500, className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("Allestimento"),dcc.Dropdown(id='allestimento',options=[{'label': a, 'value': a} for a in allestimenti],value=allestimenti[0], className='form-control')], width=6, className='mb-3'),
        ]),

        # ----------------------------
        # Input: Carburante, Venditore, Area
        # ----------------------------
        dbc.Row([
            dbc.Col([html.Label("Carburante"),dcc.Dropdown(id='carburante',options=[{'label': c, 'value': c} for c in carburanti],value=carburanti[0], className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("Venditore"),dcc.Dropdown(id='venditore',options=[{'label': 'Rivenditore', 'value': 'Rivenditore'},{'label': 'Privato', 'value': 'Privato'}],value='Rivenditore', className='form-control')], width=6, className='mb-3'),
            dbc.Col([html.Label("Macro Regione"),dcc.Dropdown(id='area',options=[{'label': 'Nord-Est', 'value': 'Nord-est'},{'label': 'Nord-Ovest', 'value': 'Nord-ovest'},{'label': 'Centro', 'value': 'Centro'},{'label': 'Sud', 'value': 'Sud'},{'label': 'Isole', 'value': 'Isole'}],value='Nord-est', className='form-control')], width=6, className='mb-3'),
        ]),

        # ----------------------------
        # Pulsante e output
        # ----------------------------
        html.Div([
            dbc.Row([dbc.Col(dbc.Button('Genera Predizione', id='predict-button', n_clicks=0, color='primary', className='mt-4'),width={'size': 6, 'offset': 3},className="text-center")]),
            html.Div(id='prediction-output', className='mt-4 text-center', style={'margin-bottom': '50px'})
        ]),
    ], fluid=True)

    # ===============================
    # Callback di predizione
    # ===============================
    @app.callback(
        Output('prediction-output', 'children'),
        Input('predict-button', 'n_clicks'),
        State('prezzo', 'value'),
        State('anni', 'value'),
        State('km', 'value'),
        State('cambio', 'value'),
        State('cv', 'value'),
        State('allestimento', 'value'),
        State('carburante', 'value'),
        State('venditore', 'value'),
        State('area', 'value')
    )
    def update_prediction(n_clicks, prezzo, anni, km, cambio, cv, allestimento, carburante, venditore, area):
        if n_clicks > 0:
            try:
                # 1. Creo il DataFrame di input
                new_data = pd.DataFrame([{
                    'Prezzo': prezzo,
                    'Anni': anni,
                    'Chilometraggio': km,
                    'Cambio': cambio,
                    'CV': cv,
                    'Allestimento': allestimento,
                    'Carburante': carburante,
                    'Venditore': venditore,
                    'Area': area
                }])

                # 2. Preprocessing con la funzione dummy
                data_dummy = get_data_dummy_for_dash(
                    new_data, data_originale,
                    allestimento_performance, allestimento_sport, allestimento_middle
                )

                data_dummy_priced = data_dummy[cols_model]

                # 4. Normalizzazione
                data_dummy_processed = preprocess_data(data_dummy_priced)

                # 5. Predizione
                predicted_price = model_ml.predict(data_dummy_processed)[0]

                # 6. Calcolo delta e convenienza
                delta_prezzo = predicted_price - prezzo
                is_conveniente = delta_prezzo > 100

                # 7. Messaggio formattato
                msg = [
                    f"{'✅ Conveniente!' if is_conveniente else '❌ Non conveniente'}", html.Br(),
                    f"- Prezzo attuale: {prezzo:,.2f} €", html.Br(),
                    f"- Prezzo previsto: {predicted_price:,.2f} €", html.Br(),
                    f"- Differenza: {delta_prezzo:,.2f} €", html.Br(),
                    html.Br(),
                    f"Metriche di valutazione del modello -> MSE: {round(val_metrics['mse'], 2)}, RMSE: {round(val_metrics['rmse'], 2)}, R²: {round(val_metrics['r2'], 4)}"
                ]

                return msg

            except Exception as e:
                return f"Errore durante la predizione: {e}"

        return 'Inserisci i valori e premi il pulsante per stimare il prezzo.'

    return app