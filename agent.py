"""
ProofChain Agent — universal decision agent (any domain, like ChatGPT)
Every decision stored on Walrus Memory + Walrus + Sui.
"""

import json
import requests
import proofchain
import memory
from domains import JSON_SUFFIX, get_example, resolve_context

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"


def ask_agent(
    question: str,
    context: dict,
    past_memories: list[str] | None = None,
) -> dict:
    memory_block = ""
    if past_memories:
        lines = "\n".join(f"- {m}" for m in past_memories)
        memory_block = f"\n\nPast decisions from Walrus Memory:\n{lines}\n"

    system = context["prompt"] + JSON_SUFFIX
    prompt = f"{system}{memory_block}\n\nQuestion: {question}\n\nJSON:"
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

    if answer is None:
        answer = text or "(no answer)"
    if reasoning is None:
        reasoning = "(model gave no separate reasoning)"
    return {"answer": str(answer), "reasoning": str(reasoning)}


def run(question: str, industry_hint: str = "") -> dict:
    ctx = resolve_context(industry_hint)
    label = ctx["label"]
    print(f"\n🤖 ProofChain [{label}] — {question}\n")

    print("→ Recalling relevant past decisions from Walrus Memory...")
    past = memory.recall_for_question(
        question,
        namespace=ctx["namespace"],
        domain=label if label != "Any domain" else None,
    )
    if past:
        print(f"  Found {len(past)} relevant memory(ies)")
    else:
        print("  No prior memories (or first question)")

    result = ask_agent(question, ctx, past_memories=past or None)
    print(f"  Answer: {result['answer']}")
    print(f"  Reasoning: {result['reasoning']}\n")

    record = proofchain.record_decision(
        agent_id=ctx["agent_id"],
        question=question,
        answer=result["answer"],
        reasoning=result["reasoning"],
        domain=label,
    )

    print("→ Remembering in Walrus Memory...")
    mem_blob = memory.remember_decision(
        domain=label,
        namespace=ctx["namespace"],
        question=question,
        answer=result["answer"],
        reasoning=result["reasoning"],
        walrus_blob_id=record["walrus_blob_id"],
        sui_record_id=record["sui_record_id"],
    )
    record["domain"] = label
    record["industry_hint"] = industry_hint
    record["memories_recalled"] = past
    record["memory_blob_id"] = mem_blob
    return record


if __name__ == "__main__":
    import sys
    hint = sys.argv[1] if len(sys.argv) > 1 else ""
    q = sys.argv[2] if len(sys.argv) > 2 else "Should we proceed with this decision?"
    rec = run(q, industry_hint=hint)
    print(json.dumps(rec, indent=2))
