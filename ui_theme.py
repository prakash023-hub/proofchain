"""ProofChain UI theme — polished demo for hackathon judges."""

CUSTOM_CSS = """
/* ── Page shell ── */
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── Hero header ── */
.pc-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 8px;
    border: 1px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}
.pc-hero h1 {
    color: #f8fafc !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
    letter-spacing: -0.02em;
}
.pc-hero .pc-tagline {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0 0 18px 0;
    line-height: 1.5;
}
.pc-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.pc-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}
.pc-badge-walrus { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56,189,248,0.4); }
.pc-badge-sui    { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.35); }
.pc-badge-agent  { background: rgba(167, 139, 250, 0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.35); }
.pc-badge-live   { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.35); }

/* ── Section cards ── */
.pc-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
}
.pc-card h3 { color: #f1f5f9 !important; margin-top: 0 !important; }
.pc-card p, .pc-card li { color: #cbd5e1 !important; }

/* ── Result panels (markdown output) ── */
.pc-result-success {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 100%) !important;
    border: 1px solid #10b981 !important;
    border-radius: 12px !important;
    padding: 20px !important;
}
.pc-result-warn {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%) !important;
    border: 1px solid #ef4444 !important;
    border-radius: 12px !important;
    padding: 20px !important;
}
.pc-result-info {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* ── Tabs ── */
.tab-nav button {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
.tab-nav button.selected {
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

/* ── Primary CTA ── */
button.primary {
    background: linear-gradient(135deg, #0284c7, #0369a1) !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4) !important;
}

/* ── Domain radio pills ── */
label span { font-weight: 500 !important; }

/* ── Tables in markdown ── */
.prose table, .markdown table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.88rem;
}
.prose th, .markdown th {
    background: #334155 !important;
    color: #f1f5f9 !important;
    padding: 10px 14px !important;
    text-align: left;
}
.prose td, .markdown td {
    padding: 9px 14px !important;
    border-bottom: 1px solid #334155 !important;
    color: #e2e8f0 !important;
}
.prose code, .markdown code {
    background: #0f172a !important;
    color: #38bdf8 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.82rem !important;
}

/* ── Footer ── */
.pc-footer {
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    padding: 16px 0 8px;
    border-top: 1px solid #334155;
    margin-top: 24px;
}
"""

HERO_HTML = """
<div class="pc-hero">
  <h1>🔗 ProofChain</h1>
  <p class="pc-tagline">
    ChatGPT for any decision — healthcare, legal, finance, or anything you ask —
    but every answer is stored on Walrus Memory, anchored on Sui, tamper-proof.
  </p>
  <div class="pc-badges">
    <span class="pc-badge pc-badge-walrus">Walrus Track</span>
    <span class="pc-badge pc-badge-agent">Agentic Web</span>
    <span class="pc-badge pc-badge-sui">Sui Testnet</span>
    <span class="pc-badge pc-badge-live">● Live Demo</span>
  </div>
</div>
"""

FOOTER_HTML = """
<div class="pc-footer">
  ProofChain · Sui Overflow 2026 · Walrus Memory + Walrus Storage + Sui Proof · Local Ollama Agent
</div>
"""

THEME = None  # set in app.py after import


def get_theme():
    import gradio as gr
    return gr.themes.Base(
        primary_hue=gr.themes.colors.sky,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.slate,
        font=gr.themes.GoogleFont("Inter"),
    ).set(
        body_background_fill="#0f172a",
        body_background_fill_dark="#0f172a",
        block_background_fill="#1e293b",
        block_background_fill_dark="#1e293b",
        block_border_color="#334155",
        block_border_color_dark="#334155",
        block_label_text_color="#94a3b8",
        block_label_text_color_dark="#94a3b8",
        block_title_text_color="#f1f5f9",
        block_title_text_color_dark="#f1f5f9",
        body_text_color="#e2e8f0",
        body_text_color_dark="#e2e8f0",
        button_primary_background_fill="linear-gradient(90deg, #0284c7, #0369a1)",
        button_primary_background_fill_dark="linear-gradient(90deg, #0284c7, #0369a1)",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        input_background_fill="#0f172a",
        input_background_fill_dark="#0f172a",
        border_color_primary_dark="#38bdf8",
    )
