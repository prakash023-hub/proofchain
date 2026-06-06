"""
ProofChain — Universal verifiable AI (any domain, like ChatGPT + proof)
"""

import gradio as gr
import agent
import proofchain
import memory
from domains import EXAMPLE_NAMES, get_example, resolve_context
from ui_theme import CUSTOM_CSS, FOOTER_HTML, HERO_HTML, get_theme

SUI_EXPLORER = "https://suiscan.xyz/testnet/object/"
PACKAGE_ID = proofchain.PACKAGE_ID

OVERVIEW_MD = """
<div class="pc-card">

### ChatGPT for decisions — but every answer is provable

ProofChain works for **any domain**: healthcare, legal, finance, education, HR,
logistics, government, tech — or anything you type. Unlike ChatGPT, every decision is:

| Step | Technology |
|---|---|
| Recalled from | **Walrus Memory** (past sessions) |
| Stored on | **Walrus** (full reasoning blob) |
| Anchored on | **Sui** (tamper-proof hash) |

```
Ask anything → Recall memory → Agent answers → Walrus + Sui → Remember for next time
```

Package `{package_id}`

</div>

<div class="pc-card">

### Demo ideas (examples only — ask anything)

🏥 Healthcare · ⚖️ Legal · 💰 Finance · 🎓 Education · 👥 HR · 📦 Supply Chain

Or type your own: *"Should our startup hire a CTO now?"* · *"Should the city approve the zoning change?"*

</div>
""".format(package_id=PACKAGE_ID)


def _wrap(content: str, style: str = "info") -> str:
    return f'<div class="pc-result-{style}">\n\n{content}\n\n</div>'


def do_ask(question, industry_hint, state):
    if not question.strip():
        return _wrap("⚠️ Type any decision question — any industry, any topic.", "info"), state
    rec = agent.run(question, industry_hint=industry_hint or "")
    state = rec
    ctx = resolve_context(industry_hint or "")
    recalled = rec.get("memories_recalled") or []
    memory_lines = "\n".join(f"- {m[:100]}…" if len(m) > 100 else f"- {m}" for m in recalled)
    memory_section = (
        f"**Walrus Memory recalled ({len(recalled)}):**\n{memory_lines}"
        if recalled else "*No related past decisions — this may be a new topic.*"
    )
    mem_blob = rec.get("memory_blob_id")
    mem_row = f"| Walrus Memory | `{mem_blob[:28]}…` |" if mem_blob else ""
    cred_id = rec.get("sui_credential_id")
    cred_row = (
        f"| DecisionCredential (Move) | [View NFT ↗]({SUI_EXPLORER}{cred_id}) |"
        if cred_id else ""
    )
    move_fn = rec.get("move_function", "log_decision")

    body = f"""
### {ctx['emoji']} Decision Recorded — {ctx['label']}

**Question**  
{rec['question']}

**Agent Answer**  
{rec['answer']}

---

{memory_section}

---

| Field | Value |
|---|---|
| Context | **{ctx['label']}** |
| Agent | `{rec['agent_id']}` |
| Input hash | `{rec['input_hash'][:20]}…` |
| Output hash | `{rec['output_hash'][:20]}…` |
| Walrus blob | `{rec['walrus_blob_id'][:28]}…` |
| Sui record | [View on-chain ↗]({SUI_EXPLORER}{rec['sui_record_id']}) |
| Move function | `{move_fn}` |
{mem_row}
{cred_row}
"""
    return _wrap(body, "success"), state


def do_verify(state):
    if not state:
        return _wrap("⚠️ Ask a question first on the **Ask** tab.", "info")
    raw = proofchain.read_from_walrus(state["walrus_blob_id"])
    import json
    data = json.loads(raw)
    recomputed = proofchain.sha256(data["answer"])
    match = recomputed == state["output_hash"]
    domain = state.get("domain", "Any domain")
    if match:
        return _wrap(f"""
### ✅ VERIFIED — Untampered

| | |
|---|---|
| Context | **{domain}** |
| On-chain hash | `{state['output_hash'][:24]}…` |
| Walrus hash | `{recomputed[:24]}…` |
| **Result** | **MATCH** |
""", "success")
    return _wrap("🚨 Hash mismatch — record may have been altered.", "warn")


def do_tamper(state):
    if not state:
        return _wrap("⚠️ Ask a question first on the **Ask** tab.", "info")
    tampered = state["answer"] + " (secretly altered!)"
    tampered_hash = proofchain.sha256(tampered)
    match = tampered_hash == state["output_hash"]
    domain = state.get("domain", "Any domain")
    return _wrap(f"""
### 🚨 TAMPERING DETECTED

| | |
|---|---|
| Context | **{domain}** |
| Original hash | `{state['output_hash'][:24]}…` |
| Tampered hash | `{tampered_hash[:24]}…` |
| **Match** | **FALSE** |

> *"{tampered}"*

Any change after the fact is instantly detectable. That is ProofChain.
""", "warn")


def do_memory():
    if not memory.is_configured():
        return _wrap("⚠️ Walrus Memory not configured.", "info")
    items = memory.list_recent_memories()
    if not items:
        return _wrap("*No memories yet. Ask any question on the **Ask** tab.*", "info")
    lines = []
    for i, m in enumerate(items, 1):
        blob = f"`{m['blob_id'][:14]}…`" if m.get("blob_id") else ""
        text = m["text"][:150] + ("…" if len(m["text"]) > 150 else "")
        lines.append(f"**{i}.** {text} {blob}")
    return _wrap("### 🧠 Walrus Memory — all your decisions\n\n" + "\n\n".join(lines), "info")


def load_example(name):
    ex = get_example(name)
    return ex["question"], name


def load_followup(name):
    ex = get_example(name)
    return ex["followup"], name


with gr.Blocks(title="ProofChain") as demo:
    gr.HTML(HERO_HTML)
    state = gr.State(None)
    selected_example = gr.State("")

    with gr.Tabs():
        with gr.Tab("📋 Overview"):
            gr.Markdown(OVERVIEW_MD)

        with gr.Tab("💬 Ask"):
            gr.Markdown(
                '<div class="pc-card">'
                "<b>Ask anything</b> — any industry, any decision. "
                "Optional industry hint tailors the agent. Every answer is recorded on Walrus + Sui."
                "</div>"
            )
            question = gr.Textbox(
                label="Your question (any domain)",
                lines=3,
                placeholder=(
                    "e.g. Should we approve this decision? "
                    "(healthcare, legal, finance, education, HR, tech — anything)"
                ),
            )
            industry_hint = gr.Textbox(
                label="Industry context (optional)",
                placeholder="Leave blank for universal — or type: Healthcare, Legal, Real Estate, …",
            )
            gr.Markdown("**Example questions** — click to load (not a limit on what you can ask):")
            with gr.Row():
                for name in EXAMPLE_NAMES:
                    gr.Button(f"{get_example(name)['emoji']} {name}", size="sm").click(
                        lambda n=name: (*load_example(n), n),
                        outputs=[question, industry_hint, selected_example],
                    )
            with gr.Row():
                ask_btn = gr.Button("Ask & Record →", variant="primary", scale=3)
                followup_btn = gr.Button("🔄 Follow-up to last example", size="sm")
            record_out = gr.Markdown()

            def do_followup(example_name):
                if not example_name:
                    return "What did we decide last time?", ""
                q, hint = load_followup(example_name)
                return q, hint

            followup_btn.click(do_followup, selected_example, [question, industry_hint])

        with gr.Tab("🧠 Memory"):
            gr.Markdown(
                '<div class="pc-card">All decisions remembered — any domain, one Walrus Memory.</div>'
            )
            memory_btn = gr.Button("Load past decisions", variant="secondary")
            memory_out = gr.Markdown()
            memory_btn.click(do_memory, [], memory_out)

        with gr.Tab("🔐 Verify"):
            gr.Markdown('<div class="pc-card">Verify integrity or simulate tampering.</div>')
            with gr.Row():
                verify_btn = gr.Button("✅ Verify integrity", variant="secondary")
                tamper_btn = gr.Button("🚨 Simulate tampering", variant="primary")
            verify_out = gr.Markdown()

        with gr.Tab("⛓️ On-chain"):
            gr.Markdown(f"""
<div class="pc-card">

### Sui Move — on-chain proof layer

| | |
|---|---|
| Package ID | `{PACKAGE_ID}` |
| Module | `audit_log` (Move) |
| Primary entry | `log_and_certify` |
| Move objects | `DecisionRecord` · `DecisionRegistry` · `DecisionCredential` |

Each decision: shared audit record + registry counter + credential minted to wallet.

Upgrade guide: `audit_log/DEPLOY.md`

</div>
""")

    gr.HTML(FOOTER_HTML)

    ask_btn.click(do_ask, [question, industry_hint, state], [record_out, state])
    verify_btn.click(do_verify, [state], [verify_out])
    tamper_btn.click(do_tamper, [state], [verify_out])


if __name__ == "__main__":
    demo.launch(share=False, theme=get_theme(), css=CUSTOM_CSS)
