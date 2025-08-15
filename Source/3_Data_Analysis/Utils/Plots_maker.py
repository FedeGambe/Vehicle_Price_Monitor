import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import requests
from scipy.stats import norm

### PER UNDERSTANDING PRICE
def plot_feature_correlation_with_price(data: pd.DataFrame, target_col: str = 'Prezzo'):
    """
    Genera un grafico a barre orizzontali che mostra la correlazione tra le variabili indipendenti
    e una variabile target (default: 'Prezzo').

    Args:
        data (pd.DataFrame): DataFrame che contiene la variabile target e le feature.
        target_col (str): Nome della variabile target. Default è 'Prezzo'.

    Returns:
        None. Mostra il grafico interattivo.
    """
    # Calcolo matrice di correlazione
    corr_matrix = data.corr()

    # Estrazione correlazioni con la variabile target, escludendo se stessa
    target_corr = corr_matrix[target_col].drop(target_col)

    # Ordinamento per valore assoluto della correlazione
    target_corr_sorted = target_corr.reindex(target_corr.abs().sort_values(ascending=False).index)

    # Creazione DataFrame per il grafico
    corr_df = pd.DataFrame({
        'Variabile': target_corr_sorted.index,
        'Correlazione': target_corr_sorted.values
    })

    # Creazione del grafico a barre
    fig = px.bar(
        corr_df,
        x='Correlazione',
        y='Variabile',
        orientation='h',
        color='Correlazione',
        color_continuous_scale='RdBu'
    )

    fig.update_traces(hovertemplate='<b>%{y}</b><br>Correlazione: %{x:.2f}')
    fig.update_layout(
        title={
            'text': f"Correlazione delle feature con {target_col}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial', 'weight': 'bold'},
        },
        yaxis=dict(autorange="reversed"),
        #height=600,
        #width=800,
    )

    fig.show()

def plot_feature_correlation_matrix(data: pd.DataFrame):
    """
    Visualizza una heatmap annotata della matrice di correlazione tra le variabili indipendenti.

    Args:
        data (pd.DataFrame): DataFrame contenente solo le feature indipendenti numeriche.

    Returns:
        None. Mostra il grafico interattivo.
    """
    # Calcolo matrice di correlazione
    correlation_matrix = data.corr()
    original_columns = list(correlation_matrix.columns)

    # Creazione heatmap annotata
    fig = ff.create_annotated_heatmap(
        z=correlation_matrix.values,
        x=original_columns,
        y=original_columns,
        annotation_text=np.around(correlation_matrix.values, decimals=2),
        showscale=True,
        colorscale='RdBu',
        reversescale=True,
        hoverinfo='text'
    )

    # Layout del grafico
    fig.update_layout(
        title={
            'text': "Correlation Matrix tra le features",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial', 'weight': 'bold'}
        },
        margin=dict(t=200, b=25, l=0, r=0),
        #height=600,
        #width=1000
    )

    fig.show()
    
def plot_polynomial_regression_comparison(X: pd.DataFrame, y: pd.Series, degree: int = 3, n_cols: int = 3):
    """
    Crea sottotrame per confrontare l'effetto di ogni feature sulla variabile target
    utilizzando regressione polinomiale.

    Args:
        X (pd.DataFrame): DataFrame con le feature indipendenti.
        y (pd.Series): Variabile target (es. Prezzo).
        degree (int): Grado della regressione polinomiale. Default = 3.
        n_cols (int): Numero di colonne per il layout dei subplot. Default = 3.

    Returns:
        None. Mostra il grafico interattivo.
    """
    titoli = list(X.columns)
    n_rows = (len(titoli) + n_cols - 1) // n_cols

    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=titoli)

    for i, feature in enumerate(titoli):
        x = X.iloc[:, i].values.reshape(-1, 1)
        x = np.array(x)
        y_vals = y.values

        # Regressione polinomiale
        poly = PolynomialFeatures(degree=degree)
        x_poly = poly.fit_transform(x)
        model = LinearRegression().fit(x_poly, y_vals)

        x_range = np.linspace(x.min(), x.max(), 300).reshape(-1, 1)
        x_range_poly = poly.transform(x_range)
        y_pred_poly = model.predict(x_range_poly)

        # Posizione subplot
        row = i // n_cols + 1
        col = i % n_cols + 1

        # Traccia dati
        fig.add_trace(
            go.Scatter(
                x=x.flatten(), y=y_vals,
                mode='markers',
                marker=dict(size=3, color='deepskyblue', opacity=0.3),
                name='Dati',
                showlegend=False
            ),
            row=row, col=col
        )

        # Traccia polinomiale
        fig.add_trace(
            go.Scatter(
                x=x_range.flatten(), y=y_pred_poly,
                mode='lines',
                line=dict(color='orange', width=2),
                name=f'Polinomiale grado {degree}',
                showlegend=False
            ),
            row=row, col=col
        )

        fig.update_yaxes(
            title_text="Prezzo",
            row=row, col=col,
            title_font=dict(size=10),
            tickfont=dict(size=9)
        )

    fig.update_layout(
        title={
            'text': f"Confronto: Regressione Polinomiale (grado {degree})",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial', 'weight': 'bold'}
        },
        template='plotly_dark',
        height=400 * n_rows,
        #width=1000
    )

    fig.update_annotations(font_size=10)
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    fig.show()

url_reg_json = 'https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson'
geojson = requests.get(url_reg_json).json()
def plot_price_by_region_and_fuel(data, geojson, allestimento, cambio, max_km):
    data_filt_reg = data[(data['Allestimento_unificato'] == allestimento) & (data['Cambio'].str.lower() == cambio) & (data['Chilometraggio'] <= max_km)]

    # suddivisione per carburante
    carburante1 = data_filt_reg[data_filt_reg['Carburante'] =='Diesel']
    carburante2 = data_filt_reg[data_filt_reg['Carburante'] =='Benzina']
    carburante3 = data_filt_reg[data_filt_reg['Carburante'] =='Ibrido']

    # funzione per calcolo media per regione
    def get_map_trace(df, geojson, title, color_scale):
        if df.empty:
            return go.Choropleth(locations=[], z=[], geojson=geojson) #se non c'è lauto in una det. regione verrà resituto un valore vuoto
        media = df.groupby("Regione")["Prezzo"].mean().reset_index()
        return go.Choropleth(geojson=geojson,featureidkey="properties.reg_name",locations=media["Regione"],
            z=media["Prezzo"],colorscale=color_scale,colorbar_title="Prezzo (€)",
            zmin=data_filt_reg['Prezzo'].min(),zmax=data_filt_reg['Prezzo'].max(),hovertemplate='<b>%{location}</b><br>Prezzo medio: %{z:,.0f} €<extra></extra>')
        
    fig_reg = make_subplots(rows=1, cols=3,subplot_titles=["Diesel", "Benzina", "Ibrida"], specs=[[{"type": "choropleth"}] * 3], column_widths=[0.33, 0.33, 0.33])
    fig_reg.add_trace(get_map_trace(carburante1, geojson, "Diesel", "YlGn"), row=1, col=1)
    fig_reg.add_trace(get_map_trace(carburante2, geojson, "Benzina", "YlOrBr"), row=1, col=2)
    fig_reg.add_trace(get_map_trace(carburante3, geojson, "Ibrida", "OrRd"), row=1, col=3)

    fig_reg.update_geos(fitbounds="locations", visible=True)
    fig_reg.update_layout(title_text=f"Prezzo Medio per Regione ({allestimento}, {cambio}, ≤ {max_km} Km)",)

    fig_reg.show()

### PER PRICE PREDICTION    
def plot_price_prediction_distributions(data: pd.DataFrame):
    """
    Crea subplot con le distribuzioni di 'prezzo_previsto' e 'delta_prezzo',
    includendo istogrammi e curve di distribuzione normale sovrapposte.

    Args:
        data (pd.DataFrame): DataFrame che deve contenere le colonne 'prezzo_previsto' e 'delta_prezzo'.

    Returns:
        None. Mostra il grafico Plotly.
    """

    # Verifica che le colonne esistano
    if 'prezzo_previsto' not in data.columns or 'delta_prezzo' not in data.columns:
        raise ValueError("Il DataFrame deve contenere le colonne 'prezzo_previsto' e 'delta_prezzo'.")

    # Parametri per prezzo_previsto
    mu_p = data['prezzo_previsto'].mean()
    sigma_p = data['prezzo_previsto'].std()
    x_p = np.linspace(data['prezzo_previsto'].min(), data['prezzo_previsto'].max(), 300)
    y_p = norm.pdf(x_p, mu_p, sigma_p)

    # Parametri per delta_prezzo
    mu_d = data['delta_prezzo'].mean()
    sigma_d = data['delta_prezzo'].std()
    x_d = np.linspace(data['delta_prezzo'].min(), data['delta_prezzo'].max(), 300)
    y_d = norm.pdf(x_d, mu_d, sigma_d)

    # Scaliamo le densità per adattarle all'istogramma
    bin_width_p = (data['prezzo_previsto'].max() - data['prezzo_previsto'].min()) / 120
    bin_width_d = (data['delta_prezzo'].max() - data['delta_prezzo'].min()) / 120

    y_p_scaled = y_p * len(data['prezzo_previsto']) * bin_width_p
    y_d_scaled = y_d * len(data['delta_prezzo']) * bin_width_d

    # Creo subplot
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Distribuzione di Prezzo Previsto', 'Distribuzione di Delta Prezzo']
    )

    # Istogrammi
    fig.add_trace(go.Histogram(
        x=data['prezzo_previsto'], nbinsx=120,
        name='Prezzo Previsto', marker_color='steelblue'
    ), row=1, col=1)

    fig.add_trace(go.Histogram(
        x=data['delta_prezzo'], nbinsx=120,
        name='Delta Prezzo', marker_color='darkorange'
    ), row=1, col=2)

    # Curve normali
    fig.add_trace(go.Scatter(
        x=x_p, y=y_p_scaled,
        mode='lines',
        name='Curva Normale Prezzo Previsto',
        line=dict(color='black', dash='dash')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x_d, y=y_d_scaled,
        mode='lines',
        name='Curva Normale Delta Prezzo',
        line=dict(color='black', dash='dash')
    ), row=1, col=2)

    # Layout finale
    fig.update_layout(
        title={
            'text': "Distribuzione delle variabili Prezzo Previsto e Delta Prezzo",
            'x': 0.5, 'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial', 'weight': 'bold'}
        },
        showlegend=True,
        bargap=0.05,
        #height=500,
        #width=1300
    )

    fig.show()

def plot_is_conveniente_distribution(data: pd.DataFrame, column: str = 'is_conveniente'):
    """
    Visualizza un pie chart della distribuzione della variabile binaria 'is_conveniente'
    e stampa la distribuzione relativa in console.

    Args:
        data (pd.DataFrame): DataFrame che contiene la variabile target.
        column (str): Nome della colonna binaria da analizzare (default: 'is_conveniente').

    Returns:
        None. Mostra il grafico interattivo e stampa le percentuali.
    """
    if column not in data.columns:
        raise ValueError(f"La colonna '{column}' non è presente nel DataFrame.")

    # Calcolo conteggi
    conv_counts = data[column].value_counts()
    labels = conv_counts.index
    sizes = conv_counts.values

    # Pie chart
    fig = px.pie(
        names=labels,
        values=sizes,
        color=labels,
        color_discrete_map={0: 'lightgreen', 1: 'lightcoral'},
        template='plotly',
        hole=0.2
    )

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        title={
            'text': f"Distribuzione della variabile {column}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial', 'weight': 'bold'}
        },
        #height=600,
        #width=600
    )

    fig.show()

    # Stampa in console
    distrib_relativa = data[column].value_counts(normalize=True).rename_axis(column).reset_index(name='Frequenza Relativa')
    print(f"\nDistribuzione relativa della variabile '{column}':\n")
    print(distrib_relativa.to_string(index=False))
