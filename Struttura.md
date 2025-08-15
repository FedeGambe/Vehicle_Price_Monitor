```plaintext

Vehicle_Price_Monitor/
├── Application/                 # Esecuzione guidata del progetto (user entry point)
│   ├── 1_Scraping_and_Data_preparation.ipynb
│   ├── 2_Understanding_Pricing.ipynb
│   └── 3_Price_Prediction.ipynb
├── Projects/                  # Analisi dedicate a modelli auto specifici (facoltativo)
│   └── [Modelli_Auto]/
├── Data/                 # Dati e configurazioni
│   ├── config/                # Configurazioni da completare (es. modelli auto)
│   ├── Processed_data/                  # Dataset puliti e pronti all'uso
│   ├── Raw_data/        # Output grezzi dello scraping
│   │   ├── [Modelli_Auto]/    # Sottocartelle per ogni modello
│   │   ├── Località/          # Dati geografici italiani
│   │   │   ├── gi_comuni_cap.csv
│   │   │   ├── italy_geo.json
│   │   │   └── italy_geo.xlsx
│   └── Import_file_from_github.py
├── Source/
│   ├── 1_Scraping/                   # Codice per raccogliere dati dal web
│   │   ├── Utils/                  # Funzioni riutilizzabili per scraping
│   │   │   ├── Autoscout_scraping.ipynb
│   │   │   ├── Scraping_Functions.py
│   │   │   └── Url_builders.py
│   │   ├── Scraping.ipynb         # Notebook principale per lanciare scraping
│   │   └── README.md              # Istruzioni per scraping
│   ├── 2_Data_Preparation/          # Pulizia e costruzione dataset analizzabili
│   │   ├── Utils/                 # Funzioni riutilizzabili per pulizia/prep dati
│   │   │   ├── cleaning_funtions.py
│   │   │   ├── data_loader.py
│   │   │   ├── dataset_cleaning.py
│   │   │   ├── dataset_formatting.py
│   │   │   └── model_utils.py
│   │   ├── main.ipynb             # Notebook principale di preprocessing
│   │   └── main(deprecato).py     # Versione obsoleta
│   ├── 3_Data_Analysis/             # Notebook e funzioni di analisi dei dati
│   │   ├── Utils/
│   │   │   ├── Function_price_analysis.py
│   │   │   └── Plots_maker.py
│   │   ├── Price_Prediction.ipynb
│   │   └── Understanding_Pricing.ipynb
│   ├── 4_Dashboard/             # Notebook e funzioni permla dashboard predittiva
│   │   ├── Utils/
│   │   │   └── Functions_dashboard.py
│   │   └── main.ipynb
└── README.md                  # (Suggerito) Istruzioni generali per il progetto