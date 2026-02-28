
import re
import yaml

class HierarchicalChunker:
    def __init__(self, config_path):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)["compression"]["chunking"]
        self.section_max_paragraphs = cfg["section_max_paragraphs"]
        self.chapter_max_sections = cfg["chapter_max_sections"]

    def chunk_document(self, document):
        paras = self._split(document["content"], document["pages"])
        sections = self._group(paras, self.section_max_paragraphs, "section")
        chapters = self._group(sections, self.chapter_max_sections, "chapter")

        return {
            "level_0": document,
            "level_1": paras,
            "level_2": sections,
            "level_3": chapters
        }

    def _split(self, text, pages):
        raw = re.split(r"\n\n+", text)
        out, pos = [], 0
        for i, p in enumerate(raw):
            if len(p.strip()) < 20:
                pos += len(p) + 2
                continue
            out.append({
                "id": f"para_{i}",
                "level": 1,
                "content": p,
                "metadata": {
                    "page_number": 1,
                    "char_start": pos,
                    "char_end": pos + len(p)
                }
            })
            pos += len(p) + 2
        return out

    def _group(self, items, size, prefix):
        groups, buf = [], []
        for i in items:
            buf.append(i)
            if len(buf) >= size:
                groups.append({
                    "id": f"{prefix}_{len(groups)}",
                    "level": 2 if prefix == "section" else 3,
                    "content": "\n\n".join(b["content"] for b in buf),
                    "child_ids": [b["id"] for b in buf]
                })
                buf = []
        if buf:
            groups.append({
                "id": f"{prefix}_{len(groups)}",
                "level": 2 if prefix == "section" else 3,
                "content": "\n\n".join(b["content"] for b in buf),
                "child_ids": [b["id"] for b in buf]
            })
        return groups
