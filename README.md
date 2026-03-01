<div align="center">

<img src="https://img.shields.io/badge/Pan2026-PhantomX-3b82f6?style=for-the-badge&logo=lightning&logoColor=white" alt="PhantomX"/>
<img src="https://img.shields.io/badge/Track%204-Contextual%20Compression-8b5cf6?style=for-the-badge" alt="Track 4"/>
<img src="https://img.shields.io/badge/Model-llama3%3Alatest-10b981?style=for-the-badge&logo=ollama&logoColor=white" alt="Llama3"/>
<img src="https://img.shields.io/badge/UI-Streamlit-ef4444?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>

# ⚡ PhantomX — Contextual Compression Engine

### *Pan2026 Hackathon · Track 4: Contextual Compression for Extreme Long Inputs*

**A hierarchical, traceable document compression system that preserves decision-critical information, surfaces contradictions, and supports full drill-down — powered by a local LLM.**

[🚀 Live Demo](#-deployment) · [📖 Architecture](#-system-architecture) · [⚙️ Setup](#%EF%B8%8F-setup--installation) · [🎯 Features](#-key-features)

</div>

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 📄 **Multi-format Ingestion** | Supports PDF, DOCX, TXT, and Markdown files |
| 🏗️ **4-Level Hierarchy** | Paragraph → Section → Chapter → Executive Summary |
| 🔒 **Fact Preservation** | Extracts numbers, dates, exceptions, obligations, and risks explicitly |
| 🔗 **Full Traceability** | Every compressed statement maps back to a source paragraph, page, and character range |
| 🚨 **Contradiction Detection** | Semantic similarity embeddings surface conflicting or redundant statements |
| 🧠 **Explainability Report** | Quantified compression stats with a breakdown of critical content preservation |
| 🎨 **Premium Dashboard** | Glassmorphism dark-themed Streamlit UI with real-time drill-down |

---

## 🧠 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     DOCUMENT INPUT                               │
│              PDF / DOCX / TXT / Markdown                        │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                   1. DOCUMENT LOADER                             │
│  • pdfplumber + PyPDF2 fallback for PDFs                        │
│  • python-docx for Word documents                               │
│  • UTF-8 text / Markdown support                                │
│  • Outputs: content, pages[], metadata{}                        │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│               2. HIERARCHICAL CHUNKER                            │
│                                                                  │
│   Level 0 (Raw)  →  Full document text                          │
│   Level 1        →  Paragraphs   (max 500 tokens, 50 overlap)   │
│   Level 2        →  Sections     (max 15 paragraphs)            │
│   Level 3        →  Chapters     (max 8 sections)               │
│                                                                  │
│  Each chunk tagged: id, page_number, char_start, char_end       │
└───────────────────────┬──────────────────────────────────────────┘
                        │
            ┌───────────┴────────────┐
            ▼                        ▼
┌─────────────────────┐   ┌──────────────────────────┐
│  3. CRITICAL CONTENT│   │  4. HIERARCHICAL          │
│     EXTRACTOR       │   │     COMPRESSOR            │
│                     │   │                            │
│ Regex patterns for: │   │  LLM: llama3:latest        │
│  • Numbers/thresholds│  │  (via Ollama locally)      │
│  • Dates            │   │                            │
│  • Exceptions       │   │  L1: Compress paragraphs  │
│  • Obligations      │   │  L2: Compress sections    │
│  • Risks/penalties  │   │  L3: Compress chapters    │
│                     │   │  L4: Executive summary    │
└──────────┬──────────┘   └────────────┬───────────────┘
           │                           │
           └─────────────┬─────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│            5. CONTRADICTION DETECTOR                             │
│                                                                  │
│  Model: sentence-transformers/all-MiniLM-L6-v2                  │
│  • Encodes all compressed paragraphs                            │
│  • Cosine similarity matrix  (threshold: 0.70)                  │
│  • Flags high-similarity pairs as potential contradictions      │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│            6. TRACEABILITY MANAGER                               │
│                                                                  │
│  Builds forward_index:  compressed_id → original_id             │
│  Tracks: chunk_id, page_number, char_start, char_end,           │
│          line_start, line_end                                    │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│            7. EXPLAINABILITY ENGINE                              │
│                                                                  │
│  Generates report:                                               │
│  • original_chars vs compressed_chars → reduction %             │
│  • total_critical_items preserved                               │
│  • contradictions count                                         │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│        8. JSON EXPORT  →  ./data/*.json                         │
│                                                                  │
│  compressed.json       chunks.json        critical_items.json   │
│  contradictions.json   traceability.json  explainability_...    │
│  document_metadata.json                                          │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│           9. STREAMLIT DASHBOARD  (app.py)                      │
│                                                                  │
│  • Executive Summary     • Chapter/Section drill-down           │
│  • Paragraph comparison  • Critical facts explorer              │
│  • Contradiction viewer  • Explainability report                │
│  • Raw JSON viewer                                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Pan2026-PhantomX/
│
├── 📄 app.py                    # Streamlit dashboard (premium dark UI)
├── 📄 process_document.py       # Full pipeline script (run this first)
├── 📄 config.yaml               # All configuration (LLM, chunking, patterns)
├── 📄 requirements.txt          # Python dependencies
│
├── 📁 src/
│   ├── chunker.py               # HierarchicalChunker class
│   └── document_loader.py       # DocumentLoader class
│
├── 📁 data/                     # Pipeline output JSON files
│   ├── compressed.json          # 4-level compressed outputs
│   ├── chunks.json              # Structured chunks with metadata
│   ├── critical_items.json      # Extracted facts, numbers, risks
│   ├── contradictions.json      # Detected semantic conflicts
│   ├── traceability.json        # Forward/reverse index
│   ├── explainability_report.json
│   └── document_metadata.json
│
├── 📓 Full_source_code.ipynb    # Jupyter notebook walkthrough
└── 📄 README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed and running
- `llama3` model pulled

### 1. Clone the Repository

```bash
git clone https://github.com/Yashak-tech/Pan2026-PhantomX.git
cd Pan2026-PhantomX
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama & Pull Model

```bash
# Start the Ollama server (background)
ollama serve

# Pull the LLM
ollama pull llama3
```

### 5. Run the Pipeline

Place your document in the project root, then:

```bash
python process_document.py
```

This will:
- Load and parse the PDF/DOCX/TXT
- Chunk hierarchically (paragraphs → sections → chapters)
- Extract critical facts using regex patterns
- Compress each level using `llama3` via Ollama
- Detect contradictions using sentence embeddings
- Export all outputs to `./data/*.json`

### 6. Launch the Dashboard

```bash
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🔧 Configuration (`config.yaml`)

| Section | Key Setting | Default |
|---|---|---|
| `compression.chunking` | `paragraph_max_tokens` | `500` |
| `compression.chunking` | `section_max_paragraphs` | `15` |
| `compression.chunking` | `chapter_max_sections` | `8` |
| `compression.target_ratios` | Level 1 → Level 4 | `0.5 → 0.9` |
| `critical_content.extract` | numbers, dates, exceptions, obligations, risks | all `true` |
| `contradictions` | `similarity_threshold` | `0.70` |
| `llm` | `model` | `llama3:latest` |
| `llm` | `temperature` | `0.3` |
| `llm` | `max_tokens` | `2000` |

---

## 🖥️ Dashboard Views

| View | What It Shows |
|---|---|
| 🏠 **Executive Summary** | Document KPIs, compression bar, top-level LLM summary, traceability chain |
| 📚 **Chapter & Section View** | Nested accordion — Chapter summaries → Section summaries, each with source badges |
| 🔍 **Paragraph Drill-Down** | Side-by-side: Compressed vs Original text + traceability (page, char range, chunk ID) |
| ⚠️ **Critical Facts & Risks** | Grouped by type (numbers, dates, exceptions, obligations, risks) with source references |
| 🚨 **Contradictions** | Semantic similarity conflicts displayed as statement pairs with confidence scores |
| 🧠 **Explainability Report** | Compression level breakdown, reduction %, trustworthiness pillars |
| 🧾 **Raw JSON Output** | Full tabbed JSON view of all pipeline outputs |

---

## 📦 Dependencies

```txt
streamlit              # Dashboard UI
ollama                 # Local LLM interface
pyyaml                 # Config file parsing
pdfplumber             # Primary PDF text extraction
PyPDF2                 # PDF fallback extractor
sentence-transformers  # Semantic embeddings for contradiction detection
scikit-learn           # Cosine similarity matrix
numpy                  # Numerical operations
jupyter                # Notebook support
```

---

## 🔬 How the Compression Pipeline Works

### Step 1 — Document Ingestion
The `DocumentLoader` reads the input file and outputs a standardised JSON-like structure with a `content` string, a `pages` array (each with `page_number`, `char_start`, `char_end`), and a `metadata` dict.

### Step 2 — Hierarchical Chunking
`HierarchicalChunker` splits the document bottom-up:
- **Level 1:** Splits on double newlines, filters paragraphs under 20 characters
- **Level 2:** Groups paragraphs into sections (up to 15 per section)
- **Level 3:** Groups sections into chapters (up to 8 per chapter)

Every chunk carries a unique `id`, `level`, and full positional metadata.

### Step 3 — Critical Content Extraction
`CriticalContentExtractor` runs regex patterns across Level 1 chunks to flag:
- Numeric thresholds, monetary values, percentages
- Calendar dates
- Exception clauses (`unless`, `only if`, `provided that`)
- Obligation markers (`must`, `shall`, `required to`)
- Risk indicators (`may result in`, `penalty`, `non-compliance`)

### Step 4 — Hierarchical Compression (LLM)
`HierarchicalCompressor` calls `llama3` via Ollama for each compression level with carefully structured prompts:
- **L1 prompt:** Compress paragraph, preserve all critical items exactly
- **L2 prompt:** Synthesise section summary from paragraph summaries
- **L3 prompt:** Create chapter summary with top 10 critical facts
- **L4 prompt:** Executive summary with top 20 facts, major themes, key risks

Fallback: If the LLM fails, the original text is truncated (no silent data loss).

### Step 5 — Contradiction Detection
`ContradictionDetector` uses `sentence-transformers/all-MiniLM-L6-v2` to encode all compressed paragraph outputs into dense embeddings, then computes a pairwise cosine similarity matrix. Any pair exceeding the threshold (default: 0.70) is flagged as a potential contradiction.

### Step 6 — Traceability
`TraceabilityManager` builds a `forward_index` mapping every compressed chunk ID to its original chunk ID, creating a full lineage from executive summary all the way down to the raw source paragraph.

### Step 7 — Explainability
`ExplainabilityEngine` generates a human-readable compression report quantifying the overall character reduction, total critical items preserved, and number of contradictions detected.

---

## 📊 Sample Output (Quantum Computing PDF)

| Metric | Value |
|---|---|
| Document | Quantum Computing for Computer Scientists |
| Pages | 402 |
| Total Words | 75,031 |
| Total Characters (original) | 747,856 |
| Total Characters (compressed) | ~1,889 |
| **Compression Ratio** | **99.7%** |
| Critical Items Preserved | 9 |
| Paragraphs Compressed | 20 |
| Contradiction Pairs Detected | Multiple |

---

## 🚀 Deployment

### Option 1: Streamlit Community Cloud (Recommended — Free)

1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repo: `Yashak-tech/Pan2026-PhantomX` · Branch: `main` · File: `app.py`
4. Click **Deploy**

> ✅ Data JSON files are committed to the repo — no pipeline re-run needed for the dashboard.

### Option 2: Local Development

```bash
streamlit run app.py
# → http://localhost:8501
```

---

## 🏆 Hackathon Context

This project was built for the **Pan2026 Hackathon** targeting the challenge of handling **extreme long inputs** in real-world documents. The key insight: one-shot summarisation destroys traceability and drops critical facts. Our solution uses a **bottom-up hierarchical approach** where:

- ✔ Every compression level is **independently verifiable**
- ✔ Every fact is **traceable to its exact source location**
- ✔ Contradictions are **surfaced, not suppressed**
- ✔ The system is **explainable by design**, not post-hoc

---

## 👥 Team

**PhantomX** — Pan2026 Hackathon Team

---

<div align="center">

Made with ⚡ by PhantomX &nbsp;|&nbsp; Pan2026 Hackathon

[![GitHub](https://img.shields.io/badge/GitHub-Yashak--tech-181717?style=flat&logo=github)](https://github.com/Yashak-tech/Pan2026-PhantomX)

</div>
