file_path = "process_document.py"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

imports = "import os\nfrom pathlib import Path\nfrom typing import Dict, List\nimport pdfplumber\nimport PyPDF2\nfrom datetime import datetime\nimport re\nimport yaml\nimport json\nfrom sentence_transformers import SentenceTransformer\nfrom sklearn.metrics.pairwise import cosine_similarity\n"

text = imports + text

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Added missing imports to process_document.py")
