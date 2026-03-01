# Pan2026-PhantomX Model(working on itt to be more precise)

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

