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

- Load input text or dataset  
- Validate and normalize the input  
- Apply text cleaning (remove punctuation, symbols, and noise)  
- Normalize text (lowercasing and accent removal)  
- Tokenize the text using spaCy  
- Remove stopwords  
- Apply lemmatization  
- Clean empty tokens and normalize output  
- Return processed text as tokens or string

## Usage 

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

## Usage in python

### 1. Import the module
```bash
from source.preprocesamiento import PreprocesadorTextoAvanzado
```

## 2. Initialize the processor
```bash
procesador = PreprocesadorTextoAvanzado()
```
## 3. Process text 
```bash
resultado = procesador.procesar("Texto de ejemplo")
print(resultado)
```
