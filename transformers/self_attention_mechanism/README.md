# Self-Attention Mechanism


## Module Structure

```text
self_attention_mechanism/
├── mecanismo_autoatencion.ipynb  # Implementation and experiments of the self-attention mechanism
├── README.md                     # Documentation and usage guide
└── requirements.txt              # Dependencies
```
## How it works

The system works as follows:

- Represent input tokens as vectors  
- Compute query (Q), key (K), and value (V) matrices  
- Calculate attention scores using dot-product similarity between queries and keys  
- Scale the scores to stabilize gradients  
- Apply softmax to obtain attention weights  
- Multiply attention weights by the value vectors  
- Aggregate the weighted values to produce context-aware representations

## Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the notebook 
```bash
jupyter notebook self_attention.ipynb
```

## Status 
Completed
