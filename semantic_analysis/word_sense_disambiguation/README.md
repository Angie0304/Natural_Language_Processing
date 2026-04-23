# Word Sense Disambiguation

This module implements Word Sense Disambiguation (WSD) to determine the correct meaning of a word based on its context. It uses WordNet to analyze possible senses and select the most appropriate one.


## Module Structure 

``` text
sentence_semantic_disambiguation/
├── README.md
├── requirements.txt
└── WSD_Word_Sense_Disambiguation.ipynb
```

## How it works

The module follows these steps:

1. Load a sentence containing an ambiguous word  
2. Preprocess the text using spaCy  
3. Retrieve possible meanings (synsets) from WordNet  
4. Generate contextual representations using transformers  
5. Compare each meaning with the sentence context  
6. Select the most appropriate sense based on similarity  
7. Return the disambiguated meaning  

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

