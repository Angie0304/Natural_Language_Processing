# Word Sense Disambiguation

This module implements Word Sense Disambiguation (WSD) to determine the correct meaning of a word based on its context. It uses WordNet to analyze possible senses and select the most appropriate one.


## Module Structure 

``` text
sentence_semantic_disambiguation/
├── README.md                             # Documentation and execution guide
├── requirements.txt                      # Dependencies
└── WSD_Word_Sense_Disambiguation.ipynb   # Semantic Disambiguation with WordNet
```

## How it works

The system works as follows:

- Load a sentence containing an ambiguous word  
- Preprocess the text using spaCy  
- Retrieve possible meanings (synsets) from WordNet  
- Generate contextual representations using transformers  
- Compare each meaning with the sentence context  
- Select the most appropriate sense based on similarity  
- Return the disambiguated meaning   

## Usage 

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the notebook:
   ```bash
    jupyter notebook WSD_Word_Sense_Disambiguation.ipynb
   ```
## Aditional Setup 

1. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

2. Download NLTK resources:
```bash
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
```

## Status 
Completed

