
from pathlib import Path
from datetime import datetime
import pdfplumber
import PyPDF2

class DocumentLoader:
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md']

    def load_document(self, file_path: str):
        file_path = Path(file_path)
        pages, full_text = [], []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                char_start = len(''.join(full_text))
                pages.append({
                    "page_number": i,
                    "content": text,
                    "char_start": char_start,
                    "char_end": char_start + len(text)
                })
                full_text.append(text)

        content = "\n\n".join(full_text)
        return {
            "content": content,
            "pages": pages,
            "metadata": {
                "filename": file_path.name,
                "total_pages": len(pages),
                "total_chars": len(content),
                "total_words": len(content.split()),
                "created_at": datetime.now().isoformat()
            }
        }
