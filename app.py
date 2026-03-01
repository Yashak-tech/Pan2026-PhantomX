import streamlit as st
import json
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Contextual Compression Engine · PhantomX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM DARK UI CSS
# =========================================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* --- FIX EXPANDER ICON: kill broken Baseweb icon text completely --- */
    /* Baseweb renders a span with icon ligature text (arrow_down etc.) — we nuke it */
    [data-testid="stExpander"] details summary > div > span:first-child,
    [data-testid="stExpander"] details summary > div > div:first-child > span,
    [data-testid="stExpander"] details summary span[class*="arrow"],
    [data-testid="stExpander"] details summary span[class*="icon"] {
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        display: inline-block !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }
    /* Our clean custom arrow via ::before */
    [data-testid="stExpander"] details summary {
        position: relative !important;
        padding-left: 1.4rem !important;
    }
    [data-testid="stExpander"] details summary::before {
        content: '▶';
        position: absolute !important;
        left: 0.5rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        font-size: 0.55rem !important;
        color: #3b82f6 !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="stExpander"] details[open] summary::before {
        transform: translateY(-50%) rotate(90deg) !important;
    }
    /* Style the expander header text cleanly */
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] .streamlit-expanderHeader p {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        margin: 0 !important;
    }



    /* --- ROOT VARIABLES --- */
    :root {
        --bg-primary: #040d1a;
        --bg-secondary: #060f20;
        --bg-card: rgba(13, 28, 54, 0.80);
        --glass-border: rgba(99, 179, 237, 0.15);
        --accent-blue: #3b82f6;
        --accent-cyan: #22d3ee;
        --accent-purple: #a78bfa;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --gradient-1: linear-gradient(135deg, #1e3a5f 0%, #0a1628 100%);
        --gradient-accent: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    }

    /* --- GLOBAL RESET --- */
    .stApp {
        background: var(--bg-primary) !important;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(34,211,238,0.04) 0%, transparent 50%) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* --- REMOVE DEFAULT STREAMLIT PADDING --- */
    .block-container {
        padding: 2rem 3rem 3rem 3rem !important;
        max-width: 1400px !important;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background: rgba(4, 13, 26, 0.97) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; right: 0; bottom: 0;
        width: 1px;
        background: linear-gradient(to bottom, transparent, rgba(59,130,246,0.5), rgba(167,139,250,0.3), transparent);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* --- NATIVE HTML details/summary ACCORDION (replaces st.expander) --- */
    details.custom-acc {
        background: rgba(13,28,54,0.82) !important;
        border: 1px solid rgba(99,179,237,0.14) !important;
        border-radius: 14px !important;
        margin-bottom: 0.75rem !important;
        overflow: hidden !important;
        transition: border-color 0.2s !important;
    }
    details.custom-acc:hover { border-color: rgba(59,130,246,0.3) !important; }
    details.custom-acc summary {
        cursor: pointer !important;
        list-style: none !important;
        padding: 1rem 1.25rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #e2e8f0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        user-select: none !important;
    }
    details.custom-acc summary::-webkit-details-marker { display: none !important; }
    details.custom-acc summary::marker { display: none !important; }
    details.custom-acc summary .acc-arrow {
        font-size: 0.55rem !important;
        color: #3b82f6 !important;
        transition: transform 0.25s ease !important;
        display: inline-block !important;
        flex-shrink: 0 !important;
    }
    details.custom-acc[open] summary .acc-arrow {
        transform: rotate(90deg) !important;
    }
    details.custom-acc summary:hover { color: #93c5fd !important; }
    details.custom-acc .acc-body {
        padding: 0 1.25rem 1.25rem 1.25rem !important;
        border-top: 1px solid rgba(99,179,237,0.1) !important;
    }
    details.inner-acc {
        background: rgba(6,15,32,0.5) !important;
        border: 1px solid rgba(99,179,237,0.1) !important;
        border-radius: 10px !important;
        margin-bottom: 0.5rem !important;
        overflow: hidden !important;
    }
    details.inner-acc summary {
        cursor: pointer !important;
        list-style: none !important;
        padding: 0.7rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        color: #94a3b8 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    details.inner-acc summary::-webkit-details-marker { display: none !important; }
    details.inner-acc summary::marker { display: none !important; }
    details.inner-acc summary .acc-arrow { font-size:0.5rem; color:#22d3ee; transition:transform .2s; flex-shrink:0; }
    details.inner-acc[open] summary .acc-arrow { transform:rotate(90deg); }
    details.inner-acc:hover { border-color:rgba(34,211,238,0.25) !important; }
    details.inner-acc summary:hover { color:#67e8f9 !important; }
    details.inner-acc .acc-body { padding: 0.5rem 1rem 1rem 1rem !important; border-top:1px solid rgba(34,211,238,0.1) !important; }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 0.3rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(99,179,237,0.08) !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.85rem !important;
        margin: 2px 0 !important;
        transition: all 0.2s ease !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(59,130,246,0.12) !important;
        border-color: rgba(59,130,246,0.35) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(59,130,246,0.18) !important;
        border-color: rgba(59,130,246,0.5) !important;
    }

    /* --- HEADINGS --- */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
    h3 { font-size: 1.15rem !important; font-weight: 600 !important; }

    /* --- ALL TEXT --- */
    p, li, div, span {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    strong, b { color: var(--text-primary) !important; }

    /* --- METRICS / STAT CARDS --- */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        padding: 1.2rem 1.5rem !important;
        backdrop-filter: blur(20px) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(59,130,246,0.18) !important;
        border-color: rgba(59,130,246,0.35) !important;
    }
    [data-testid="stMetricLabel"] > div {
        color: var(--text-muted) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* --- EXPANDERS --- */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 14px !important;
        margin-bottom: 0.75rem !important;
        backdrop-filter: blur(16px) !important;
        transition: border-color 0.2s !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(59,130,246,0.3) !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: var(--text-primary) !important;
        padding: 1rem 1.25rem !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #63b3ed !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 0 1.25rem 1.25rem !important;
        border-top: 1px solid rgba(99,179,237,0.1) !important;
    }

    /* --- TABS --- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: rgba(13,28,54,0.6) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid var(--glass-border) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 9px !important;
        padding: 0.5rem 1.2rem !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(59,130,246,0.2) !important;
        color: #93c5fd !important;
        border: 1px solid rgba(59,130,246,0.35) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* --- CODE BLOCKS --- */
    [data-testid="stCode"], .stCode {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(99,179,237,0.15) !important;
        border-radius: 10px !important;
        font-size: 0.8rem !important;
    }
    code { color: #93c5fd !important; }

    /* --- INFO / SUCCESS / WARNING BOXES --- */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border-left-width: 4px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* --- DIVIDER --- */
    hr {
        border: none !important;
        border-top: 1px solid rgba(99,179,237,0.12) !important;
        margin: 2rem 0 !important;
    }

    /* --- SCROLLBAR --- */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.35); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.6); }

    /* --- JSON VIEW --- */
    [data-testid="stJson"] {
        background: rgba(0,0,0,0.35) !important;
        border: 1px solid rgba(99,179,237,0.12) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

def load_json(name):
    with open(DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)

compressed     = load_json("compressed")
critical_items = load_json("critical_items")
contradictions = load_json("contradictions")
traceability   = load_json("traceability")
report         = load_json("explainability_report")
chunks         = load_json("chunks")
metadata       = load_json("document_metadata")

# =========================================================
# HELPER: HTML CARD
# =========================================================
def card(content_html, accent="#3b82f6", padding="1.4rem 1.8rem"):
    st.markdown(f"""
    <div style="
        background: rgba(13,28,54,0.82);
        border: 1px solid rgba(99,179,237,0.14);
        border-left: 3px solid {accent};
        border-radius: 14px;
        padding: {padding};
        margin-bottom: 0.75rem;
        backdrop-filter: blur(16px);
        line-height: 1.7;
        color: #cbd5e1;
        font-size: 0.9rem;
    ">{content_html}</div>
    """, unsafe_allow_html=True)

def badge(label, color):
    return f'<span style="background:rgba({color},0.15);color:rgb({color});border:1px solid rgba({color},0.4);border-radius:99px;font-size:0.72rem;font-weight:600;padding:3px 10px;margin-right:6px;letter-spacing:0.05em">{label}</span>'

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 0 1.5rem 0; border-bottom: 1px solid rgba(99,179,237,0.15); margin-bottom: 1.5rem;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; color:#e2e8f0; letter-spacing:-0.02em;">
            ⚡ PhantomX
        </div>
        <div style="font-size:0.73rem; color:#64748b; font-weight:500; margin-top:4px; letter-spacing:0.06em; text-transform:uppercase;">
            Contextual Compression Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.72rem;color:#64748b;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.6rem;">📄 Document</div>', unsafe_allow_html=True)

    # Stats
    comp_stats  = report["compression_statistics"]
    orig_chars  = comp_stats["original_chars"]
    comp_chars  = comp_stats["compressed_chars"]
    reduction   = (1 - comp_chars / orig_chars) * 100 if orig_chars else 0

    st.markdown(f"""
    <div style="background:rgba(13,28,54,0.7);border:1px solid rgba(99,179,237,0.13);border-radius:13px;padding:1rem 1.2rem;margin-bottom:1.2rem;">
        <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.2rem;">📁 {metadata['filename']}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.8rem;">
            <div><div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Pages</div>
                 <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;font-family:'Space Grotesk',sans-serif">{metadata['total_pages']}</div></div>
            <div><div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Words</div>
                 <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;font-family:'Space Grotesk',sans-serif">{metadata['total_words']:,}</div></div>
            <div><div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Compression</div>
                 <div style="font-size:1.1rem;font-weight:700;color:#10b981;font-family:'Space Grotesk',sans-serif">{reduction:.1f}%</div></div>
            <div><div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Critical Facts</div>
                 <div style="font-size:1.1rem;font-weight:700;color:#f59e0b;font-family:'Space Grotesk',sans-serif">{report['content_preservation']['total_critical_items']}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.72rem;color:#64748b;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.6rem;">🧭 Navigate</div>', unsafe_allow_html=True)

    view = st.radio(
        "Navigate",
        [
            "🏠  Executive Summary",
            "📚  Chapter & Section View",
            "🔍  Paragraph Drill-Down",
            "⚠️  Critical Facts & Risks",
            "🚨  Contradictions",
            "🧠  Explainability Report",
            "🧾  Raw JSON Output"
        ],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="margin-top:auto;padding-top:2rem;border-top:1px solid rgba(99,179,237,0.1);margin-top:1.5rem;">
        <div style="font-size:0.7rem;color:#334155;text-align:center;line-height:1.6">
            Pan2026 · PhantomX Team<br>Contextual Compression
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGE HERO HEADER
# =========================================================
VIEW_ICONS = {
    "🏠  Executive Summary":    ("Executive Summary",          "🏠",  "#3b82f6"),
    "📚  Chapter & Section View": ("Hierarchical View",        "📚",  "#8b5cf6"),
    "🔍  Paragraph Drill-Down": ("Paragraph Drill-Down",       "🔍",  "#22d3ee"),
    "⚠️  Critical Facts & Risks": ("Critical Facts & Risks",   "⚠️",  "#f59e0b"),
    "🚨  Contradictions":       ("Contradiction Detector",     "🚨",  "#ef4444"),
    "🧠  Explainability Report": ("Explainability Report",     "🧠",  "#10b981"),
    "🧾  Raw JSON Output":      ("Raw Structured Output",      "🧾",  "#64748b"),
}
view_name, view_icon, view_color = VIEW_ICONS[view]

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(13,28,54,0.95) 0%, rgba(6,15,32,0.95) 100%);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute; top: 0; right: 0; width: 300px; height: 300px;
        background: radial-gradient(circle, {view_color}18 0%, transparent 65%);
        pointer-events: none;
    "></div>
    <div style="display:flex;align-items:center;gap:1rem;">
        <div style="
            font-size: 2.4rem;
            background: linear-gradient(135deg, {view_color} 0%, {view_color}aa 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        ">{view_icon}</div>
        <div>
            <div style="font-size:0.72rem;color:#64748b;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">Pan2026 · PhantomX</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.7rem;font-weight:700;color:#e2e8f0;letter-spacing:-0.02em;line-height:1.2">{view_name}</div>
        </div>
    </div>
    <div style="
        margin-top: 1rem;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, {view_color}80 0%, {view_color}20 60%, transparent 100%);
        border-radius: 2px;
    "></div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 1️⃣  EXECUTIVE SUMMARY
# =========================================================
if view == "🏠  Executive Summary":

    # Top KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Total Pages",    metadata['total_pages'])
    with col2:
        st.metric("📝 Total Words",    f"{metadata['total_words']:,}")
    with col3:
        st.metric("🗜️ Compression",   f"{reduction:.1f}%",  delta="chars saved")
    with col4:
        st.metric("⚡ Critical Items", report['content_preservation']['total_critical_items'])

    st.markdown("<br>", unsafe_allow_html=True)

    # Compression Bar
    st.markdown(f"""
    <div style="background:rgba(13,28,54,0.8);border:1px solid rgba(99,179,237,0.14);border-radius:14px;padding:1.4rem 1.8rem;margin-bottom:1.2rem">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
            <span style="font-size:0.8rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Information Reduction</span>
            <span style="font-size:1.1rem;font-weight:700;color:#10b981;font-family:'Space Grotesk',sans-serif">{reduction:.1f}% Reduced</span>
        </div>
        <div style="background:rgba(0,0,0,0.35);border-radius:99px;height:10px;overflow:hidden;">
            <div style="width:{reduction:.0f}%;height:100%;background:linear-gradient(90deg,#10b981,#3b82f6);border-radius:99px;transition:width 1s ease;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:0.5rem;">
            <span style="font-size:0.72rem;color:#64748b">Original: {orig_chars:,} chars</span>
            <span style="font-size:0.72rem;color:#64748b">Compressed: {comp_chars:,} chars</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📌 Executive Summary")
    card(f"""
    <div style='color:#cbd5e1;line-height:1.75;font-size:0.9rem;'>
        {compressed["level_4"]["content"].replace(chr(10), "<br>")}
    </div>
    """, accent="#3b82f6")

    st.markdown("### 📍 Traceability Chain")
    st.caption("This executive summary was synthesised from the following chapters:")
    cols = st.columns(min(len(compressed["level_4"]["child_ids"]), 4))
    for i, cid in enumerate(compressed["level_4"]["child_ids"]):
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:0.6rem 1rem;text-align:center;font-size:0.78rem;font-weight:600;color:#93c5fd;">
                🔗 {cid}
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# 2️⃣  CHAPTER → SECTION SUMMARIES
# =========================================================
elif view == "📚  Chapter & Section View":

    section_index = {s["id"]: s for s in compressed["level_2"]}

    for c_idx, chapter in enumerate(compressed["level_3"], 1):
        child_badges = ''.join([badge(sid, "139,92,246") for sid in chapter["child_ids"]])
        related_sections = [section_index[sid] for sid in chapter["child_ids"] if sid in section_index]

        section_html = ""
        for s_idx, section in enumerate(related_sections, 1):
            source_ids = ' &middot; '.join(section['child_ids'])
            content_html = section['content'].replace('\n', '<br>').replace('"', '&quot;')
            section_html += f"""
            <details class="inner-acc">
              <summary><span class="acc-arrow">&#9654;</span> Section {c_idx}.{s_idx}</summary>
              <div class="acc-body">
                <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(34,211,238,0.14);border-left:3px solid #22d3ee;border-radius:12px;padding:1rem 1.2rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem;margin-bottom:0.5rem;">
                  {content_html}
                </div>
                <div style="font-size:0.72rem;color:#64748b;margin-top:0.3rem;">&#128206; Source: {source_ids}</div>
              </div>
            </details>
            """

        chapter_content = chapter["content"].replace('\n', '<br>').replace('"', '&quot;')
        open_attr = 'open' if c_idx == 1 else ''
        st.markdown(f"""
        <details class="custom-acc" {open_attr}>
          <summary>
            <span class="acc-arrow">&#9654;</span>
            Chapter {c_idx} &nbsp;<span style="color:#64748b;font-weight:400;font-size:0.8rem;">&mdash; {len(chapter['child_ids'])} sections</span>
          </summary>
          <div class="acc-body">
            <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(139,92,246,0.2);border-left:3px solid #8b5cf6;border-radius:12px;padding:1.2rem 1.6rem;line-height:1.7;color:#cbd5e1;font-size:0.9rem;margin-bottom:1rem;">
              {chapter_content}
            </div>
            <div style="display:flex;gap:0.4rem;margin-bottom:1rem;flex-wrap:wrap;">{child_badges}</div>
            {section_html}
          </div>
        </details>
        """, unsafe_allow_html=True)



# =========================================================
# 3️⃣  PARAGRAPH-LEVEL DRILL-DOWN
# =========================================================
elif view == "🔍  Paragraph Drill-Down":

    total = len(compressed["level_1"])
    st.markdown(f"""
    <div style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem;">
        <span style="font-size:1.5rem;">&#128269;</span>
        <div>
            <div style="color:#67e8f9;font-weight:600;font-size:0.9rem;">Paragraph-Level Compression View</div>
            <div style="color:#64748b;font-size:0.8rem;margin-top:2px;">Showing <strong style='color:#22d3ee'>{total}</strong> compressed paragraphs alongside their original text with full traceability.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, para in enumerate(compressed["level_1"], 1):
        ratio = para.get("compression_stats", {}).get("reduction_percent", 0)
        ratio_color = "#10b981" if ratio > 40 else ("#f59e0b" if ratio > 20 else "#ef4444")
        orig_text = para['original_content'].replace('\n','<br>').replace('"', '&quot;')
        comp_text = para['content'].replace('\n','<br>').replace('"', '&quot;')
        trace = para.get("source_traceability", {})
        trace_html = ""
        if trace:
            trace_html = f"""<div style='display:flex;gap:0.5rem;margin-top:0.7rem;flex-wrap:wrap;font-size:0.73rem;color:#64748b;'>
                <span>&#128209; Page {trace.get('page_number','?')}</span>
                <span>&middot;</span>
                <span>&#128205; Chars {trace.get('char_start','?')}&ndash;{trace.get('char_end','?')}</span>
                <span>&middot;</span>
                <span>&#128279; {trace.get('chunk_id','?')}</span>
            </div>"""
        st.markdown(f"""
        <details class="custom-acc">
          <summary>
            <span class="acc-arrow">&#9654;</span>
            Paragraph {i}
            &nbsp;<span style="color:{ratio_color};font-size:0.78rem;font-weight:700;">{ratio:.0f}% reduced</span>
          </summary>
          <div class="acc-body">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div>
                <div style="font-size:0.7rem;font-weight:700;color:#10b981;text-transform:uppercase;letter-spacing:.08em;margin-bottom:0.4rem;">&#10003; Compressed</div>
                <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(99,179,237,0.14);border-left:3px solid #10b981;border-radius:12px;padding:1rem 1.2rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem;">{comp_text}</div>
              </div>
              <div>
                <div style="font-size:0.7rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:0.4rem;">&#128196; Original</div>
                <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(99,179,237,0.14);border-left:3px solid #334155;border-radius:12px;padding:1rem 1.2rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem;">{orig_text}</div>
              </div>
            </div>
            {trace_html}
          </div>
        </details>
        """, unsafe_allow_html=True)



# =========================================================
# 4️⃣  KEY FACTS / EXCEPTIONS / RISKS
# =========================================================
elif view == "⚠️  Critical Facts & Risks":

    TYPE_CONFIG = {
        "numbers":    ("🔢", "#3b82f6", "59,130,246"),
        "dates":      ("📅", "#8b5cf6", "139,92,246"),
        "exceptions": ("⚠️", "#f59e0b", "245,158,11"),
        "risks":      ("🚨", "#ef4444", "239,68,68"),
        "obligations":("📋", "#10b981", "16,185,129"),
    }

    if not critical_items:
        st.info("No critical items detected in this document.")
    else:
        # Group by type
        by_type: dict = {}
        for item in critical_items:
            t = item["type"]
            by_type.setdefault(t, []).append(item)

        # Summary row
        cols = st.columns(len(by_type))
        for i, (t, items) in enumerate(by_type.items()):
            icon, color, _ = TYPE_CONFIG.get(t, ("📌","#64748b","100,116,139"))
            with cols[i]:
                st.metric(f"{icon} {t.capitalize()}", len(items))

        st.markdown("<br>", unsafe_allow_html=True)

        for t, items in by_type.items():
            icon, color, rgb = TYPE_CONFIG.get(t, ("📌","#64748b","100,116,139"))
            st.markdown(f"""
            <div style="font-size:0.8rem;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:.08em;margin:1.2rem 0 0.5rem 0;">{icon} {t}</div>
            """, unsafe_allow_html=True)
            for j, item in enumerate(items, 1):
                val_display = item['value'][:80] + ('…' if len(item['value']) > 80 else '')
                val_safe = item['value'].replace('"', '&quot;').replace('<', '&lt;')
                chunk_id = item['source']['chunk_id']
                page_num = item['source']['page_number']
                st.markdown(f"""
                <details class="custom-acc">
                  <summary>
                    <span class="acc-arrow">&#9654;</span>
                    <span style="color:{color};font-size:0.88rem;font-weight:600;">{val_display}</span>
                  </summary>
                  <div class="acc-body">
                    <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(99,179,237,0.14);border-left:3px solid {color};border-radius:12px;padding:0.9rem 1.2rem;line-height:1.7;color:{color};font-weight:600;font-size:0.9rem;margin-bottom:0.6rem;">{val_safe}</div>
                    <div style="font-size:0.75rem;color:#64748b;">&#128279; Chunk: <code style="color:#93c5fd;background:rgba(59,130,246,0.1);padding:2px 6px;border-radius:4px;">{chunk_id}</code> &nbsp;&middot;&nbsp; &#128196; Page {page_num}</div>
                  </div>
                </details>
                """, unsafe_allow_html=True)



# =========================================================
# 5️⃣  CONTRADICTIONS
# =========================================================
elif view == "🚨  Contradictions":

    if not contradictions:
        st.markdown("""
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:14px;padding:2rem;text-align:center;margin:1rem 0;">
            <div style="font-size:2rem">✅</div>
            <div style="font-size:1rem;font-weight:600;color:#10b981;margin-top:0.5rem;">No Contradictions Detected</div>
            <div style="font-size:0.82rem;color:#64748b;margin-top:0.3rem;">The document passed all semantic consistency checks.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;">
            <span style="color:#ef4444;font-weight:700">{len(contradictions)} potential contradiction(s)</span>
            <span style="color:#94a3b8;font-size:0.85rem;"> detected via semantic similarity embeddings.</span>
        </div>
        """, unsafe_allow_html=True)

        for i, c in enumerate(contradictions, 1):
            conf = c['confidence']
            conf_color = "#ef4444" if conf > 0.9 else ("#f59e0b" if conf > 0.75 else "#64748b")
            st_a = c["statement_a"]["content"].replace('\n','<br>').replace('"','&quot;')
            st_b = c["statement_b"]["content"].replace('\n','<br>').replace('"','&quot;')
            st.markdown(f"""
            <details class="custom-acc">
              <summary>
                <span class="acc-arrow">&#9654;</span>
                Contradiction {i}
                &nbsp;<span style="color:{conf_color};font-size:0.78rem;font-weight:700;">Confidence {conf:.2%}</span>
              </summary>
              <div class="acc-body">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                  <div>
                    <div style="font-size:0.7rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.07em;margin-bottom:0.4rem;">Statement A</div>
                    <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(239,68,68,0.2);border-left:3px solid #ef4444;border-radius:12px;padding:0.9rem 1.2rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem;">{st_a}</div>
                  </div>
                  <div>
                    <div style="font-size:0.7rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.07em;margin-bottom:0.4rem;">Statement B</div>
                    <div style="background:rgba(13,28,54,0.82);border:1px solid rgba(245,158,11,0.2);border-left:3px solid #f59e0b;border-radius:12px;padding:0.9rem 1.2rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem;">{st_b}</div>
                  </div>
                </div>
                <div style="background:rgba(239,68,68,0.05);border:1px dashed rgba(239,68,68,0.25);border-radius:8px;padding:0.7rem 1rem;margin-top:0.8rem;font-size:0.78rem;color:#94a3b8;">
                  Similarity confidence: <strong style="color:{conf_color}">{conf:.2%}</strong> &nbsp;&middot;&nbsp; Review recommended for policy clarity.
                </div>
              </div>
            </details>
            """, unsafe_allow_html=True)



# =========================================================
# 6️⃣  EXPLAINABILITY
# =========================================================
elif view == "🧠  Explainability Report":

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Chars",    f"{orig_chars:,}")
    with col2:
        st.metric("Compressed Chars",  f"{comp_chars:,}")
    with col3:
        st.metric("Reduction",         f"{reduction:.2f}%", delta="information saved")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📊 Compression Breakdown")
    levels_data = {
        "Level 1 · Paragraphs":  len(compressed.get("level_1",[])),
        "Level 2 · Sections":    len(compressed.get("level_2",[])),
        "Level 3 · Chapters":    len(compressed.get("level_3",[])),
        "Level 4 · Executive":   1,
    }
    cols = st.columns(4)
    colors = ["#3b82f6","#8b5cf6","#22d3ee","#10b981"]
    for i, (label, count) in enumerate(levels_data.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background:rgba(13,28,54,0.8);border:1px solid rgba(99,179,237,0.13);border-radius:13px;padding:1.2rem;text-align:center;">
                <div style="font-size:1.6rem;font-weight:700;color:{colors[i]};font-family:'Space Grotesk',sans-serif">{count}</div>
                <div style="font-size:0.72rem;color:#64748b;font-weight:500;margin-top:4px;text-transform:uppercase;letter-spacing:.06em">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✅ Why This Compression is Trustworthy")
    pillars = [
        ("🏗️  Hierarchical", "Not one-shot summarisation. Paragraphs → Sections → Chapters → Executive."),
        ("🔒  Fact-Preserving", "Critical numbers, dates, exceptions, and obligations are explicitly extracted."),
        ("🔗  Fully Traceable", "Every statement maps back to a source paragraph, page, and character range."),
        ("🚨  Contradiction-Aware", f"{report['contradictions']} semantic conflicts surfaced—not hidden."),
    ]
    cols2 = st.columns(2)
    for i, (title, desc) in enumerate(pillars):
        with cols2[i % 2]:
            card(f"<strong style='color:#e2e8f0'>{title}</strong><br><span style='font-size:0.83rem'>{desc}</span>", accent=colors[i], padding="1.1rem 1.4rem")

    st.markdown("### 📄 Full Report JSON")
    st.json(report)


# =========================================================
# 7️⃣  RAW JSON
# =========================================================
elif view == "🧾  Raw JSON Output":
    tab1, tab2, tab3, tab4 = st.tabs(["Compressed", "Chunks", "Traceability", "Critical Items"])
    with tab1:
        st.json(compressed)
    with tab2:
        st.json(chunks)
    with tab3:
        st.json(traceability)
    with tab4:
        st.json(critical_items)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="
    margin-top: 3rem;
    border-top: 1px solid rgba(99,179,237,0.1);
    padding-top: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <div style="font-size:0.75rem;color:#334155;">
        <strong style="color:#475569">⚡ PhantomX</strong>  ·  Pan2026 Hackathon  ·  Contextual Compression Engine
    </div>
    <div style="display:flex;gap:0.5rem;">
        <span style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);color:#93c5fd;border-radius:99px;font-size:0.7rem;font-weight:600;padding:3px 10px">✔ Structure</span>
        <span style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;border-radius:99px;font-size:0.7rem;font-weight:600;padding:3px 10px">✔ Traceability</span>
        <span style="background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);color:#c4b5fd;border-radius:99px;font-size:0.7rem;font-weight:600;padding:3px 10px">✔ Explainability</span>
    </div>
</div>
""", unsafe_allow_html=True)
