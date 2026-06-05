"""
ProofChain Agent — autonomous AI agent (local Ollama, zero cost/offline)
whose every decision is stored verifiably on Walrus and anchored on Sui.
"""

import json
import requests
import proofchain

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"
AGENT_ID = "proofchain-agent-001"

SYSTEM_PROMPT = (
    "You are a careful decision-support agent. For each question give a clear "
    "answer and a short reasoning. Respond ONLY as compact JSON with exactly two "
    "keys: \"answer\" (a sentence) and \"reasoning\" (a sentence). "
    "No markdown, no code fences, no extra text."
)


def ask_agent(question: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {question}\n\nJSON:"
    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }, timeout=120)
    resp.raise_for_status()
    text = resp.json().get("response", "").strip()
    text = text.replace("```json", "").replace("```", "").strip()

    answer, reasoning = None, None
    try:
        data = json.loads(text)
        answer = data.get("answer")
        reasoning = data.get("reasoning")
    except json.JSONDecodeError:
        answer = text

    # Always return clean strings, never crash on missing keys
    if answer is None:
        answer = text or "(no answer)"
    if reasoning is None:
        reasoning = "(model gave no separate reasoning)"
    return {"answer": str(answer), "reasoning": str(reasoning)}


def run(question: str) -> dict:
    print(f"\n🤖 Agent thinking about: {question}\n")
    result = ask_agent(question)
    print(f"  Answer: {result['answer']}")
    print(f"  Reasoning: {result['reasoning']}\n")

    record = proofchain.record_decision(
        agent_id=AGENT_ID,
        question=question,
        answer=result["answer"],
        reasoning=result["reasoning"],
    )
    return record


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else \
        "Should a small clinic adopt a new electronic record system this year?"
    rec = run(q)
    print("\n--- Verifiable record created ---")
    print(json.dumps(rec, indent=2))

    print("\n=== Verifying integrity ===")
    v = proofchain.verify_decision(rec["walrus_blob_id"], expected_answer=rec["answer"])
    print(f"✅ Verified: {v['verified']}")
