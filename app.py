import streamlit as st
import json
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Contextual Compression Engine",
    page_icon="🗜️",
    layout="wide"
)

st.title("🗜️ Contextual Compression Engine")
st.markdown("""
**Track 4 – Contextual Compression for Extreme Long Inputs**

> A hierarchical, traceable compression system that preserves  
> decision-critical information and supports drill-down.
""")

# =========================================================
# LOAD DATA
# =========================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

def load_json(name):
    with open(DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)

compressed = load_json("compressed")
critical_items = load_json("critical_items")
contradictions = load_json("contradictions")
traceability = load_json("traceability")
report = load_json("explainability_report")
chunks = load_json("chunks")
metadata = load_json("document_metadata")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("📄 Document Overview")
st.sidebar.write(f"**File:** {metadata['filename']}")
st.sidebar.write(f"**Pages:** {metadata['total_pages']}")
st.sidebar.write(f"**Words:** {metadata['total_words']}")
st.sidebar.write(f"**Characters:** {metadata['total_chars']}")

view = st.sidebar.radio(
    "Navigate",
    [
        "Executive Summary",
        "Chapter → Section Summaries",
        "Paragraph Drill-Down",
        "Key Facts / Exceptions / Risks",
        "Contradictions",
        "Explainability & Information Loss",
        "Raw Structured Output (JSON)"
    ]
)

# =========================================================
# 1️⃣ EXECUTIVE SUMMARY (TOP LEVEL)
# =========================================================
if view == "Executive Summary":
    st.header("📌 Executive Summary (Highest Compression Level)")

    st.write(compressed["level_4"]["content"])

    st.subheader("📍 Traceability")
    st.caption("This executive summary was synthesized from the following chapters:")
    for cid in compressed["level_4"]["child_ids"]:
        st.code(cid)

# =========================================================
# 2️⃣ CHAPTER → SECTION SUMMARIES
# =========================================================
elif view == "Chapter → Section Summaries":
    st.header("📚 Hierarchical Summaries")

    for c_idx, chapter in enumerate(compressed["level_3"], 1):
        with st.expander(f"Chapter {c_idx} Summary"):
            st.write(chapter["content"])

            st.markdown("**Derived from Sections:**")
            for sid in chapter["child_ids"]:
                st.code(sid)

            # SECTION DRILL-DOWN
            # Build section index ONCE (outside loops ideally)
            section_index = {s["id"]: s for s in compressed["level_2"]}

            # Inside chapter loop
            related_sections = [
                section_index[sid]
                for sid in chapter["child_ids"]
                if sid in section_index
            ]


            for s_idx, section in enumerate(related_sections, 1):
                with st.expander(f"Section {c_idx}.{s_idx}"):
                    st.write(section["content"])
                    st.caption(f"Source paragraphs: {', '.join(section['child_ids'])}")

# =========================================================
# 3️⃣ PARAGRAPH-LEVEL DRILL-DOWN
# =========================================================
elif view == "Paragraph Drill-Down":
    st.header("🔍 Paragraph-Level Drill-Down")

    st.markdown("""
    This is the **lowest compression level**.  
    Every compressed paragraph is shown **alongside its original text**
    with full traceability.
    """)

    for i, para in enumerate(compressed["level_1"], 1):
        with st.expander(f"Paragraph {i}"):
            st.subheader("Compressed Version")
            st.write(para["content"])

            st.subheader("Original Text")
            st.write(para["original_content"])

            st.subheader("Traceability")
            st.json(para["source_traceability"])

# =========================================================
# 4️⃣ KEY FACTS / EXCEPTIONS / RISKS
# =========================================================
elif view == "Key Facts / Exceptions / Risks":
    st.header("⚠️ Decision-Critical Information")

    st.markdown("""
    These items were **explicitly preserved** during compression:
    - Numbers, thresholds, limits
    - Exceptions (`unless`, `only if`)
    - Risks and constraints
    """)

    if not critical_items:
        st.info("No critical items detected.")
    else:
        for i, item in enumerate(critical_items, 1):
            with st.expander(f"{i}. {item['type'].upper()} → {item['value']}"):
                st.markdown("**Source Reference**")
                st.json(item["source"])

# =========================================================
# 5️⃣ CONTRADICTIONS
# =========================================================
elif view == "Contradictions":
    st.header("🚨 Potential Contradictions & Redundancies")

    st.markdown("""
    These are **high-similarity statements** detected using semantic embeddings.
    They may indicate:
    - Conflicting policies
    - Redundant rules
    - Ambiguous requirements
    """)

    if not contradictions:
        st.success("No contradictions detected.")
    else:
        for i, c in enumerate(contradictions, 1):
            with st.expander(f"Contradiction {i} (confidence {c['confidence']:.2f})"):
                st.subheader("Statement A")
                st.write(c["statement_a"]["content"])

                st.subheader("Statement B")
                st.write(c["statement_b"]["content"])

                st.caption("⚠️ Review recommended for policy clarity.")

# =========================================================
# 6️⃣ EXPLAINABILITY & INFORMATION LOSS
# =========================================================
elif view == "Explainability & Information Loss":
    st.header("🧠 Explainability Report")

    st.json(report)

    original_chars = report["compression_statistics"]["original_chars"]
    compressed_chars = report["compression_statistics"]["compressed_chars"]

    reduction = (1 - compressed_chars / original_chars) * 100

    st.subheader("📉 Compression Impact")
    st.write(f"**Original characters:** {original_chars}")
    st.write(f"**Compressed characters:** {compressed_chars}")
    st.write(f"**Reduction:** {reduction:.2f}%")

    st.markdown("""
    **Why this compression is trustworthy:**
    - Hierarchical (not one-shot summarization)
    - Decision-critical facts explicitly extracted
    - Every statement traceable to source
    - Contradictions surfaced instead of hidden
    """)

# =========================================================
# 7️⃣ RAW STRUCTURED OUTPUT
# =========================================================
elif view == "Raw Structured Output (JSON)":
    st.header("🧾 Structured Outputs (Machine-Readable)")

    tab1, tab2, tab3 = st.tabs(["Compressed", "Traceability", "Chunks"])

    with tab1:
        st.json(compressed)

    with tab2:
        st.json(traceability)

    with tab3:
        st.json(chunks)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("""
**Contextual Compression Engine – Track 4 Submission**

Focus:  
✔ Structure  
✔ Traceability  
✔ Decision-Preserving Compression  
✔ Explainability
""")
