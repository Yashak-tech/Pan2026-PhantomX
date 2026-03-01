# Pan2026-PhantomX Model

This repository contains the code and assets for the Pan2026-PhantomX document
processing and hierarchical chunking model. The goal of the project is to load
various document formats (PDF, DOCX, text), break them into meaningful chunks
(paragraphs, sections, chapters), and prepare the data for downstream
information retrieval or machine learning tasks.

## 🔍 Model Overview

- **Document Loader** – reads PDF, DOCX, and plain text files and converts
  them to a common JSON-like representation.
- **Hierarchical Chunker** – splits the loaded document into paragraphs, groups
  them into sections, and optionally chapters using configurable rules.
- **Notebook & Scripts** – `Full_source_code.ipynb` demonstrates how the
  pipeline works along with supporting scripts (`process_document.py`,
  `to_script.py`, etc.).

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yashak-tech/Pan2026-PhantomX.git
   cd Pan2026-PhantomX
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the notebook**
   Open `Full_source_code.ipynb` in Jupyter or VS Code to step through the model
   pipeline interactively.

## 🛠️ Usage

### Loading and chunking a document
```python
from process_document import DocumentLoader, HierarchicalChunker

loader = DocumentLoader()
doc = loader.load_document("sample.pdf")

chunker = HierarchicalChunker(config_path="config.yaml")
result = chunker.chunk_document(doc)
print(result.keys())  # e.g. ['paragraphs', 'sections']
```

### Converting paths in notebooks
Use `change_nb.py` to replace hardcoded Colab `/content/` paths with local
relative paths.

## 📁 Repository Structure

```
.
├── src/                      # Core Python modules
│   ├── chunker.py
│   └── document_loader.py
├── Full_source_code.ipynb     # Example notebook showing the full model
├── process_document.py        # Helper script for loading/chunking
├── to_script.py               # Utility script used by the notebook
├── change_nb.py               # Notebook path converter
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ✨ Contributing
Contributions are welcome! Please fork the repo and submit a pull request with
clear description of your changes. Make sure to update the notebook or include
new examples when adding features.

## 📄 License
Specify the license you want to use here (e.g. MIT, Apache 2.0). If no license
is chosen, the code is "All rights reserved" by default.
