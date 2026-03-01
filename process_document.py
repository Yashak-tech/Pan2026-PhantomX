import os
from pathlib import Path
from typing import Dict, List
import pdfplumber
import PyPDF2
from datetime import datetime
import re
import yaml
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# Install zstd dependency

# Download and install Ollama server binary

# Start Ollama server in the background

# %%writefile /content/streamlit_app/document_loader.py
class DocumentLoader:
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md', '.docx']

    def load_document(self, file_path: str) -> Dict:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        extension = file_path.suffix.lower()
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")

        if extension == '.pdf':
            return self._load_pdf(file_path)
        elif extension in ['.txt', '.md']:
            return self._load_text(file_path)
        elif extension == '.docx':
            return self._load_docx(file_path)

    def _load_pdf(self, file_path: Path) -> Dict:
        pages, full_text = [], []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    char_start = len(''.join(full_text))
                    pages.append({
                        'page_number': page_num,
                        'content': text,
                        'char_start': char_start,
                        'char_end': char_start + len(text)
                    })
                    full_text.append(text)
        except Exception:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    char_start = len(''.join(full_text))
                    pages.append({
                        'page_number': page_num,
                        'content': text,
                        'char_start': char_start,
                        'char_end': char_start + len(text)
                    })
                    full_text.append(text)

        content = '\n\n'.join(full_text)
        return {
            'content': content,
            'pages': pages,
            'metadata': {
                'filename': file_path.name,
                'filepath': str(file_path),
                'format': 'pdf',
                'total_pages': len(pages),
                'total_chars': len(content),
                'total_words': len(content.split()),
                'created_at': datetime.now().isoformat()
            }
        }

    def _load_text(self, file_path: Path) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pages, char_pos = [], 0
        for i, section in enumerate(content.split('\n\n'), start=1):
            if section.strip():
                pages.append({
                    'page_number': i,
                    'content': section,
                    'char_start': char_pos,
                    'char_end': char_pos + len(section)
                })
            char_pos += len(section) + 2

        return {
            'content': content,
            'pages': pages,
            'metadata': {
                'filename': file_path.name,
                'filepath': str(file_path),
                'format': 'text',
                'total_pages': len(pages),
                'total_chars': len(content),
                'total_words': len(content.split()),
                'created_at': datetime.now().isoformat()
            }
        }

    def _load_docx(self, file_path: Path) -> Dict:
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)

        pages, full_text, char_pos = [], [], 0
        for i, para in enumerate(doc.paragraphs, start=1):
            text = para.text
            if text.strip():
                pages.append({
                    'page_number': i,
                    'content': text,
                    'char_start': char_pos,
                    'char_end': char_pos + len(text)
                })
                full_text.append(text)
                char_pos += len(text) + 1

        content = '\n'.join(full_text)
        return {
            'content': content,
            'pages': pages,
            'metadata': {
                'filename': file_path.name,
                'filepath': str(file_path),
                'format': 'docx',
                'total_pages': len(pages),
                'total_chars': len(content),
                'total_words': len(content.split()),
                'created_at': datetime.now().isoformat()
            }
        }


# %%writefile /content/streamlit_app/chunker.py
class HierarchicalChunker:
    def __init__(self, config_path="config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)['compression']['chunking']
        self.paragraph_max_tokens = cfg['paragraph_max_tokens']
        self.section_max_paragraphs = cfg['section_max_paragraphs']
        self.chapter_max_sections = cfg['chapter_max_sections']

    def chunk_document(self, document: Dict) -> Dict:
        paragraphs = self._split_into_paragraphs(document['content'], document['pages'])
        
        # Limit to the first 20 paragraphs for a quick demonstration 
        paragraphs = paragraphs[:20]
        
        sections = self._group_into_sections(paragraphs)
        chapters = self._group_into_chapters(sections)

        return {
            'level_0': {'content': document['content'], 'metadata': document['metadata']},
            'level_1': paragraphs,
            'level_2': sections,
            'level_3': chapters,
            'metadata': {
                'total_paragraphs': len(paragraphs),
                'total_sections': len(sections),
                'total_chapters': len(chapters)
            }
        }

    def _split_into_paragraphs(self, content, pages):
        raw = re.split(r'\n\n+', content)
        paragraphs, char_pos = [], 0

        for i, text in enumerate(raw):
            text = text.strip()
            if not text or len(text) < 20:
                char_pos += len(text) + 2
                continue

            paragraphs.append({
                'id': f'para_{i}',
                'level': 1,
                'content': text,
                'metadata': {
                    'page_number': self._find_page(char_pos, pages),
                    'char_start': char_pos,
                    'char_end': char_pos + len(text),
                    'line_start': content[:char_pos].count('\n'),
                    'line_end': content[:char_pos].count('\n') + text.count('\n')
                }
            })
            char_pos += len(text) + 2
        return paragraphs

    def _group_into_sections(self, paragraphs):
        sections, buf = [], []
        for p in paragraphs:
            buf.append(p)
            if len(buf) >= self.section_max_paragraphs:
                sections.append(self._create_section(buf, len(sections)))
                buf = []
        if buf:
            sections.append(self._create_section(buf, len(sections)))
        return sections

    def _group_into_chapters(self, sections):
        chapters, buf = [], []
        for s in sections:
            buf.append(s)
            if len(buf) >= self.chapter_max_sections:
                chapters.append(self._create_chapter(buf, len(chapters)))
                buf = []
        if buf:
            chapters.append(self._create_chapter(buf, len(chapters)))
        return chapters

    def _create_section(self, paras, idx):
        return {
            'id': f'section_{idx}',
            'level': 2,
            'content': '\n\n'.join(p['content'] for p in paras),
            'child_ids': [p['id'] for p in paras]
        }

    def _create_chapter(self, sections, idx):
        return {
            'id': f'chapter_{idx}',
            'level': 3,
            'content': '\n\n---\n\n'.join(s['content'] for s in sections),
            'child_ids': [s['id'] for s in sections]
        }

    def _find_page(self, pos, pages):
        for p in pages:
            if p['char_start'] <= pos <= p['char_end']:
                return p['page_number']
        return 1


class CriticalContentExtractor:
    def __init__(self, config_path="config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        self.patterns = cfg['critical_content']['patterns']
        self.enabled = cfg['critical_content']['extract']

    def extract_from_chunks(self, chunks):
        items = []
        for c in chunks:
            items.extend(self.extract_from_chunk(c))
        return items

    def extract_from_chunk(self, chunk):
        content = chunk['content']
        results = []

        for key, patterns in self.patterns.items():
            if not self.enabled.get(key, False):
                continue
            for p in patterns:
                for m in re.finditer(p, content, re.IGNORECASE):
                    results.append({
                        'type': key,
                        'value': m.group(0),
                        'source': {
                            'chunk_id': chunk['id'],
                            'level': chunk['level'],
                            'page_number': chunk['metadata'].get('page_number', 1)
                        }
                    })
        return results


"""
Hierarchical Compressor
Compresses documents level by level using LLM
"""

import ollama
from typing import Dict, List
import yaml
from datetime import datetime


class HierarchicalCompressor:
    """
    Compress documents hierarchically using Ollama
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.llm_config = self.config['llm']
        self.model = self.llm_config['model']
        self.temperature = self.llm_config['temperature']
        self.max_tokens = self.llm_config['max_tokens']

    def compress_all_levels(self, chunks: Dict, critical_items: List[Dict]) -> Dict:
        """
        Compress all levels hierarchically

        Returns:
            Dict with compressed chunks at each level
        """
        print("\n🗜️  Starting hierarchical compression...")

        # Level 1: Compress paragraphs
        print("   Level 1: Compressing paragraphs...")
        compressed_l1 = self.compress_level_1(chunks['level_1'], critical_items)

        # Level 2: Compress sections
        print("   Level 2: Compressing sections...")
        compressed_l2 = self.compress_level_2(chunks['level_2'], compressed_l1)

        # Level 3: Compress chapters
        print("   Level 3: Compressing chapters...")
        compressed_l3 = self.compress_level_3(chunks['level_3'], compressed_l2)

        # Level 4: Executive summary
        print("   Level 4: Creating executive summary...")
        compressed_l4 = self.compress_level_4(chunks['level_0'], compressed_l3)

        return {
            'level_1': compressed_l1,
            'level_2': compressed_l2,
            'level_3': compressed_l3,
            'level_4': compressed_l4
        }

    def compress_level_1(self, paragraphs: List[Dict], critical_items: List[Dict]) -> List[Dict]:
        """Compress individual paragraphs"""
        compressed = []

        critical_by_chunk = {}
        for item in critical_items:
            chunk_id = item['source']['chunk_id']
            if chunk_id not in critical_by_chunk:
                critical_by_chunk[chunk_id] = []
            critical_by_chunk[chunk_id].append(item)

        for i, para in enumerate(paragraphs):
            print(f"      Paragraph {i+1}/{len(paragraphs)}", end='\r')

            para_critical = critical_by_chunk.get(para['id'], [])
            compressed_para = self._compress_paragraph(para, para_critical)
            compressed.append(compressed_para)

        print(f"      ✅ Compressed {len(compressed)} paragraphs")
        return compressed

    def compress_level_2(self, sections: List[Dict], compressed_l1: List[Dict]) -> List[Dict]:
        """Compress sections from paragraph summaries"""
        compressed = []
        para_index = {p['original_id']: p for p in compressed_l1}

        for i, section in enumerate(sections):
            print(f"      Section {i+1}/{len(sections)}", end='\r')

            child_paras = [para_index[cid] for cid in section['child_ids'] if cid in para_index]
            compressed_section = self._compress_section(section, child_paras)
            compressed.append(compressed_section)

        print(f"      ✅ Compressed {len(compressed)} sections")
        return compressed

    def compress_level_3(self, chapters: List[Dict], compressed_l2: List[Dict]) -> List[Dict]:
        """Compress chapters from section summaries"""
        compressed = []
        section_index = {s['original_id']: s for s in compressed_l2}

        for i, chapter in enumerate(chapters):
            print(f"      Chapter {i+1}/{len(chapters)}", end='\r')

            child_sections = [section_index[cid] for cid in chapter['child_ids'] if cid in section_index]
            compressed_chapter = self._compress_chapter(chapter, child_sections)
            compressed.append(compressed_chapter)

        print(f"      ✅ Compressed {len(compressed)} chapters")
        return compressed

    def compress_level_4(self, document: Dict, compressed_l3: List[Dict]) -> Dict:
        """Create executive summary"""
        print(f"      Creating executive summary...")
        exec_summary = self._compress_executive(document, compressed_l3)
        print(f"      ✅ Executive summary created")
        return exec_summary

    def _compress_paragraph(self, para: Dict, critical_items: List[Dict]) -> Dict:
        """Compress single paragraph"""
        critical_summary = self._format_critical_items(critical_items)

        prompt = f"""Compress this paragraph while preserving ALL critical information.

CRITICAL CONTENT TO PRESERVE:
{critical_summary}

RULES:
- Keep ALL numbers, dates, exceptions, obligations, and risks EXACTLY as written
- Remove filler words, redundant explanations, and examples
- Keep the meaning precise and exact
- Be concise but complete

ORIGINAL PARAGRAPH:
{para['content']}

COMPRESSED VERSION (respond with compressed text only, no explanations):"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            compressed_text = response['message']['content'].strip()
        except Exception as e:
            print(f"\n⚠️  LLM error: {e}")
            compressed_text = para['content'][:len(para['content'])//2]

        return {
            'id': para['id'] + '_compressed',
            'original_id': para['id'],
            'level': 1,
            'content': compressed_text,
            'original_content': para['content'],
            'compression_stats': {
                'original_chars': len(para['content']),
                'compressed_chars': len(compressed_text),
                'compression_ratio': len(compressed_text) / len(para['content']) if len(para['content']) > 0 else 1,
                'reduction_percent': (
                    (1 - len(compressed_text) / len(para['content'])) * 100
                    if len(para['content']) > 0 else 0
                )
            },
            'critical_content': critical_items,
            'source_traceability': {
                'chunk_id': para['id'],
                'page_number': para['metadata'].get('page_number', 1),
                'char_start': para['metadata']['char_start'],
                'char_end': para['metadata']['char_end'],
                'line_start': para['metadata']['line_start'],
                'line_end': para['metadata']['line_end']
            },
            'created_at': datetime.now().isoformat()
        }

    def _compress_section(self, section: Dict, child_paras: List[Dict]) -> Dict:
        """Compress section from paragraph summaries"""
        combined = '\n\n'.join([p['content'] for p in child_paras])

        all_critical = []
        for para in child_paras:
            all_critical.extend(para.get('critical_content', []))

        critical_summary = self._format_critical_items(all_critical)

        prompt = f"""Create a section summary from these compressed paragraphs.

CRITICAL FACTS TO INCLUDE:
{critical_summary}

COMPRESSED PARAGRAPHS:
{combined}

SECTION SUMMARY (synthesize, don't just concatenate):"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            compressed_text = response['message']['content'].strip()
        except Exception as e:
            print(f"\n⚠️  LLM error: {e}")
            compressed_text = combined[:len(combined)//2]

        return {
            'id': section['id'] + '_compressed',
            'original_id': section['id'],
            'level': 2,
            'content': compressed_text,
            'original_content': section['content'],
            'child_ids': [p['id'] for p in child_paras],
            'compression_stats': {
                'original_chars': len(section['content']),
                'compressed_chars': len(compressed_text),
                'compression_ratio': len(compressed_text) / len(section['content']) if len(section['content']) > 0 else 1
            },
            'critical_content': all_critical,
            'created_at': datetime.now().isoformat()
        }

    def _compress_chapter(self, chapter: Dict, child_sections: List[Dict]) -> Dict:
        """Compress chapter from section summaries"""
        combined = '\n\n---\n\n'.join([s['content'] for s in child_sections])

        prompt = f"""Create a chapter summary from these section summaries.

Focus on:
- Top 10 most critical facts
- Key themes and patterns
- Major risks and constraints

SECTION SUMMARIES:
{combined}

CHAPTER SUMMARY:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            compressed_text = response['message']['content'].strip()
        except Exception as e:
            print(f"\n⚠️  LLM error: {e}")
            compressed_text = combined[:len(combined)//3]

        return {
            'id': chapter['id'] + '_compressed',
            'original_id': chapter['id'],
            'level': 3,
            'content': compressed_text,
            'original_content': chapter['content'],
            'child_ids': [s['id'] for s in child_sections],
            'compression_stats': {
                'original_chars': len(chapter['content']),
                'compressed_chars': len(compressed_text),
                'compression_ratio': len(compressed_text) / len(chapter['content']) if len(chapter['content']) > 0 else 1
            },
            'created_at': datetime.now().isoformat()
        }

    def _compress_executive(self, document: Dict, child_chapters: List[Dict]) -> Dict:
        """Create executive summary"""
        combined = '\n\n═══════════════\n\n'.join([c['content'] for c in child_chapters])

        prompt = f"""Create an executive summary of this document.

Include:
- Document purpose and scope
- Top 20 most critical facts
- Major themes across all chapters
- Highest priority risks
- Key decision points

CHAPTER SUMMARIES:
{combined}

EXECUTIVE SUMMARY:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            compressed_text = response['message']['content'].strip()
        except Exception as e:
            print(f"\n⚠️  LLM error: {e}")
            compressed_text = combined[:2000]

        return {
            'id': 'executive_summary',
            'original_id': 'document',
            'level': 4,
            'content': compressed_text,
            'original_content': document['content'],
            'child_ids': [c['id'] for c in child_chapters],
            'compression_stats': {
                'original_chars': len(document['content']),
                'compressed_chars': len(compressed_text),
                'compression_ratio': len(compressed_text) / len(document['content']) if len(document['content']) > 0 else 1
            },
            'created_at': datetime.now().isoformat()
        }

    def _format_critical_items(self, items: List[Dict]) -> str:
        """Format critical items for prompt"""
        if not items:
            return "None found"

        formatted = []
        by_type = {}

        for item in items:
            item_type = item['type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item['value'])

        for item_type, values in by_type.items():
            unique_values = list(set(values))[:5]
            formatted.append(f"- {item_type}: {', '.join(unique_values)}")

        return '\n'.join(formatted)


class ContradictionDetector:
    def __init__(self, config_path="config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)['contradictions']
        self.enabled = cfg['enabled']
        self.threshold = cfg['similarity_threshold']
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def detect(self, paragraphs):
        if not self.enabled or len(paragraphs) < 2:
            return []

        texts = [p['content'] for p in paragraphs]
        emb = self.model.encode(texts)
        sim = cosine_similarity(emb)

        conflicts = []
        for i in range(len(paragraphs)):
            for j in range(i + 1, len(paragraphs)):
                if sim[i][j] > self.threshold:
                    conflicts.append({
                        'severity': 'high',
                        'statement_a': paragraphs[i],
                        'statement_b': paragraphs[j],
                        'confidence': float(sim[i][j])
                    })
        return conflicts


class TraceabilityManager:
    def __init__(self):
        self.forward_index = {}
        self.reverse_index = {}

    def build_links(self, compressed, chunks, document):
        for level, data in compressed.items():
            if isinstance(data, list):
                for c in data:
                    self.forward_index[c['id']] = c['original_id']
            else:
                self.forward_index[data['id']] = data['original_id']
        return {
            'forward_index': self.forward_index,
            'reverse_index': self.reverse_index,
            'citations': {}
        }


class ExplainabilityEngine:
    def generate_report(self, document, compressed, critical_items, contradictions, traceability):
        return {
            'generated_at': datetime.now().isoformat(),
            'compression_statistics': {
                'original_chars': len(document['content']),
                'compressed_chars': len(compressed['level_4']['content'])
            },
            'content_preservation': {
                'total_critical_items': len(critical_items)
            },
            'contradictions': len(contradictions)
        }

    def format_report_text(self, report: dict) -> str:
        """Formats the report dictionary into a human-readable string."""
        report_str = f"""--- Compression Report ---
Generated At: {report['generated_at']}

Compression Statistics:
  Original Characters: {report['compression_statistics']['original_chars']}
  Compressed Characters: {report['compression_statistics']['compressed_chars']}
  Reduction Percentage: {((report['compression_statistics']['original_chars'] - report['compression_statistics']['compressed_chars']) / report['compression_statistics']['original_chars']) * 100:.2f}%

Content Preservation:
  Total Critical Items Identified: {report['content_preservation']['total_critical_items']}

Contradiction Detection:
  Total Contradictions Found: {report['contradictions']}
--------------------------"""
        return report_str

class CompressionStorage:
    def __init__(self, output_dir="data/output"):
        self.dir = Path(output_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, name, data):
        with open(self.dir / f"{name}.json", "w") as f:
            json.dump(data, f, indent=2)


CONFIG_PATH = "config.yaml"
DOCUMENT_PATH = "Quantum-Computing-for-Computer-Scientists (1).pdf"

loader = DocumentLoader()
chunker = HierarchicalChunker(CONFIG_PATH)
extractor = CriticalContentExtractor(CONFIG_PATH)
compressor = HierarchicalCompressor(CONFIG_PATH)
detector = ContradictionDetector(CONFIG_PATH)
tracer = TraceabilityManager()
explainer = ExplainabilityEngine()

doc = loader.load_document(DOCUMENT_PATH)

chunks = chunker.chunk_document(doc)

critical = extractor.extract_from_chunks(chunks['level_1'])
compressed = compressor.compress_all_levels(chunks, critical)
contradictions = detector.detect(compressed['level_1'])
trace = tracer.build_links(compressed, chunks, doc)

report = explainer.generate_report(
    doc, compressed, critical, contradictions, trace
)

report

print(explainer.format_report_text(report))

print("\n" + "="*80)
print("  COMPRESSED DOCUMENT – FULL OUTPUT")
print("="*80 + "\n")

# =====================================================
# LEVEL 4 – EXECUTIVE SUMMARY
# =====================================================
print("\n" + "#"*60)
print("LEVEL 4: EXECUTIVE SUMMARY")
print("#"*60 + "\n")
print(compressed['level_4']['content'].encode('utf-8', errors='replace').decode('utf-8'))

# =====================================================
# LEVEL 3 – CHAPTER SUMMARIES
# =====================================================
print("\n" + "#"*60)
print("LEVEL 3: CHAPTER SUMMARIES")
print("#"*60)

for i, chapter in enumerate(compressed['level_3'], 1):
    print(f"\n--- CHAPTER {i} ---\n")
    print(chapter['content'].encode('utf-8', errors='replace').decode('utf-8'))

# =====================================================
# LEVEL 2 – SECTION SUMMARIES
# =====================================================
print("\n" + "#"*60)
print("LEVEL 2: SECTION SUMMARIES")
print("#"*60)

for i, section in enumerate(compressed['level_2'], 1):
    print(f"\n--- SECTION {i} ---\n")
    print(section['content'].encode('utf-8', errors='replace').decode('utf-8'))

# =====================================================
# LEVEL 1 – PARAGRAPH COMPRESSION (WITH ORIGINAL)
# =====================================================
print("\n" + "#"*60)
print("LEVEL 1: PARAGRAPH COMPRESSION")
print("#"*60)

for i, para in enumerate(compressed['level_1'], 1):
    print(f"\n--- PARAGRAPH {i} ---")

    print("\n[COMPRESSED]")
    print(para['content'].encode('utf-8', errors='replace').decode('utf-8'))

    print("\n[ORIGINAL]")
    print(para['original_content'].encode('utf-8', errors='replace').decode('utf-8'))

    # Critical content if exists
    if para.get('critical_content'):
        print("\n[CRITICAL CONTENT]")
        for item in para['critical_content']:
            print(f"- {item['type']}: {item['value'].encode('utf-8', errors='replace').decode('utf-8')}")

# =====================================================
# CONTRADICTIONS
# =====================================================
print("\n" + "#"*60)
print("CONTRADICTIONS DETECTED")
print("#"*60)

if not contradictions:
    print("\nNo contradictions found.")
else:
    for i, c in enumerate(contradictions, 1):
        print(f"\n--- CONTRADICTION {i} ---")
        # print(c['description']) # This key does not exist
        print(f"Severity: {c['severity']}")
        print(f"Confidence: {c['confidence']:.2f}")
        print("Statement A:", c['statement_a']['content'].encode('utf-8', errors='replace').decode('utf-8'))
        print("Statement B:", c['statement_b']['content'].encode('utf-8', errors='replace').decode('utf-8'))
        # print("Recommendation:", c['recommendation']) # This key does not exist
        print("Recommendation: Investigate these highly similar statements for potential redundancy or contradiction.")

# =====================================================
# EXPLAINABILITY REPORT (SUMMARY)
# =====================================================
print("\n" + "#"*60)
print("EXPLAINABILITY REPORT")
print("#"*60 + "\n")

print(explainer.format_report_text(report).encode('utf-8', errors='replace').decode('utf-8'))

print("\n" + "="*80)
print("END OF OUTPUT")
print("="*80)

# =====================================================
# LOCAL EXPORT FOR STREAMLIT
# =====================================================

import json
from pathlib import Path

# -------- BASIC PATHS --------
EXPORT_DIR = Path("./")
DATA_DIR = EXPORT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# -------- SAVE RUNTIME OUTPUTS --------
def save_json(name, obj):
    with open(DATA_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

save_json("compressed", compressed)
save_json("critical_items", critical)
save_json("contradictions", contradictions)
save_json("traceability", trace)
save_json("explainability_report", report)
save_json("chunks", chunks)
save_json("document_metadata", doc["metadata"])

print("✅ Saved pipeline outputs locally to ./data/")
print("\n🎉 EXPORT COMPLETE")
print("👉 Run: streamlit run app.py")
