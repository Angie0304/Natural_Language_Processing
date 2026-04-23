# Mailbox Feedback Preprocessing
This project implements a preprocessing pipeline for feedback data collected from a mailbox of complaints and suggestions. It includes data cleaning, normalization, and analysis using Python-based tools to prepare the text for further processing and insights extraction.

## Project Structure

```text
mailbox_preprocessing/
├── data/
│   ├── raw/                     # Raw input data
│   └── processed/               # Cleaned and processed data
├── notebooks/
│   ├── Limpieza_datos.ipynb             # Data cleaning notebook
│   └── 2_documentacion_hallazgos.ipynb  # Findings and analysis
├── source/
│   ├── datos.py                # Data handling functions
│   ├── preprocesamiento.py     # Preprocessing pipeline
│   ├── Limpieza_datos.py       # Data cleaning script
│   ├── constantes.py           # Constants and configurations
│   └── stopwords.py            # Stopwords definitions
├── utils/
│   └── funciones_estandar_V2_2.py  # Utility functions
├── README.md                       # Documentation and execution guide
└── requirements.txt               # Dependencies
```

## How it works

The system works as follows:

- Load raw feedback data  
- Clean the text (remove noise and irrelevant characters)  
- Normalize the text (lowercasing and standardization)  
- Remove stopwords  
- Apply preprocessing techniques  
- Store the processed data  
- Analyze the results 
