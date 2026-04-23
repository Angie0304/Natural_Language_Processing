# Mailbox Feedback Preprocessing
This project implements a preprocessing pipeline for feedback data collected from a mailbox of complaints and suggestions. It includes data cleaning, normalization, and analysis using Python-based tools to prepare the text for further processing and insights extraction.

## Module Structure

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
│   └── funciones_estandar_V2_2.py # Utility functions
└── README.md                       # Documentation and execution guide
