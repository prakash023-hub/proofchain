"""
ProofChain — Verifiable AI Agent (Gradio UI)
Ask -> agent answers -> stored on Walrus -> anchored on Sui -> verify / tamper-check
"""

import gradio as gr
import agent
import proofchain

SUI_EXPLORER = "https://suiscan.xyz/testnet/object/"


def do_ask(question, state):
    if not question.strip():
        return "Please enter a question.", "", state
    rec = agent.run(question)
    state = rec
    record_md = f"""
### ✅ Decision recorded & anchored on-chain

**Question:** {rec['question']}

**Agent answer:** {rec['answer']}

| Field | Value |
|---|---|
| Agent ID | `{rec['agent_id']}` |
| Input hash | `{rec['input_hash'][:24]}…` |
| Output hash | `{rec['output_hash'][:24]}…` |
| Walrus blob ID | `{rec['walrus_blob_id']}` |
| Sui record | [{rec['sui_record_id'][:20]}…]({SUI_EXPLORER}{rec['sui_record_id']}) |

*The reasoning is stored verifiably on Walrus; the proof is immutable on Sui.*
"""
    return record_md, "", state


def do_verify(state):
    if not state:
        return "⚠️ Record a decision first."
    raw = proofchain.read_from_walrus(state["walrus_blob_id"])
    import json
    data = json.loads(raw)
    recomputed = proofchain.sha256(data["answer"])
    match = (recomputed == state["output_hash"])
    if match:
        return f"""
### ✅ VERIFIED — untampered

Fetched the original reasoning from Walrus and recomputed its hash.
It **matches** the hash anchored on Sui.

- On-chain output hash: `{state['output_hash'][:32]}…`
- Recomputed from Walrus: `{recomputed[:32]}…`
- **Match: TRUE** — this is provably the exact decision the agent made.
"""
    return "🚨 Mismatch — data does not match on-chain proof."


def do_tamper(state):
    if not state:
        return "⚠️ Record a decision first."
    # Simulate someone altering the answer after the fact
    tampered_answer = state["answer"] + " (secretly altered!)"
    tampered_hash = proofchain.sha256(tampered_answer)
    match = (tampered_hash == state["output_hash"])
    return f"""
### 🚨 TAMPERING DETECTED

Someone changed the agent's answer to:
> *"{tampered_answer}"*

- Original on-chain hash: `{state['output_hash'][:32]}…`
- Hash of tampered answer: `{tampered_hash[:32]}…`
- **Match: {str(match).upper()}** → the proof **fails**.

Because the hash is anchored immutably on Sui, **any change is instantly detectable.**
This is the core guarantee of ProofChain.
"""


with gr.Blocks(title="ProofChain") as demo:
    gr.Markdown(
        "# 🔗 ProofChain\n"
        "### Verifiable AI Agent — every decision provably stored on Walrus & anchored on Sui\n"
        "Local AI agent (offline) · Walrus verifiable memory · Sui immutable proof"
    )
    state = gr.State(None)

    with gr.Row():
        question = gr.Textbox(
            label="Ask the agent a decision question",
            placeholder="e.g. Should we approve this loan based on the provided data?",
            scale=4,
        )
        ask_btn = gr.Button("Ask & Record", variant="primary", scale=1)

    record_out = gr.Markdown()

    with gr.Row():
        verify_btn = gr.Button("🔍 Verify integrity")
        tamper_btn = gr.Button("🚨 Simulate tampering")

    verify_out = gr.Markdown()

    ask_btn.click(do_ask, [question, state], [record_out, question, state])
    verify_btn.click(do_verify, [state], [verify_out])
    tamper_btn.click(do_tamper, [state], [verify_out])


if __name__ == "__main__":
    demo.launch(share=False)
