"""Universal agent — any domain. Presets are example questions only."""

AGENT_ID = "proofchain-agent-001"
NAMESPACE = "proofchain"

JSON_SUFFIX = (
    ' Respond ONLY as compact JSON with exactly two keys: "answer" (a sentence) '
    'and "reasoning" (a sentence). No markdown, no code fences, no extra text.'
)

UNIVERSAL_PROMPT = (
    "You are ProofChain, a universal verifiable decision-support agent — like ChatGPT "
    "but every answer you give will be cryptographically recorded. You handle ANY "
    "industry or topic: healthcare, legal, finance, education, HR, logistics, "
    "government, tech, or anything else. Give a clear decision and short reasoning. "
    "If past decisions are provided, stay consistent with them."
)

# Example questions for judges — NOT a limit on what users can ask
EXAMPLES = {
    "Healthcare": {
        "emoji": "🏥",
        "question": (
            "Should a hospital approve a high-cost antibiotic for a patient "
            "with limited evidence of benefit?"
        ),
        "followup": "What did we decide about the high-cost antibiotic last time?",
    },
    "Legal": {
        "emoji": "⚖️",
        "question": "Should we approve this vendor contract given the liability clause in section 4.2?",
        "followup": "What was our prior decision on the vendor contract liability clause?",
    },
    "Finance": {
        "emoji": "💰",
        "question": "Should we approve this $50k business loan based on the applicant's cash flow data?",
        "followup": "What did we decide about the $50k business loan previously?",
    },
    "Education": {
        "emoji": "🎓",
        "question": "Should the university adopt AI-assisted grading for large introductory courses?",
        "followup": "What did we decide about AI-assisted grading?",
    },
    "HR": {
        "emoji": "👥",
        "question": "Should we approve remote work permanently for this engineering team?",
        "followup": "What was our decision on permanent remote work?",
    },
    "Supply Chain": {
        "emoji": "📦",
        "question": "Should we switch to a new supplier with lower cost but less track record?",
        "followup": "What did we decide about the new supplier?",
    },
}

EXAMPLE_NAMES = list(EXAMPLES.keys())


def resolve_context(industry_hint: str = "") -> dict:
    """
    Build agent context. Empty hint = universal (any domain).
    Optional hint tailors tone, e.g. 'Healthcare' or 'Real estate'.
    """
    hint = (industry_hint or "").strip()
    if not hint or hint.lower() in ("any", "general", "all"):
        return {
            "label": "Any domain",
            "emoji": "🌐",
            "agent_id": AGENT_ID,
            "namespace": NAMESPACE,
            "prompt": UNIVERSAL_PROMPT,
        }
    return {
        "label": hint,
        "emoji": EXAMPLES.get(hint, {}).get("emoji", "💬"),
        "agent_id": AGENT_ID,
        "namespace": NAMESPACE,
        "prompt": (
            f"You are ProofChain, a verifiable decision-support agent advising in the "
            f"context of **{hint}**. Give a clear decision and short reasoning. "
            f"If past decisions are provided, stay consistent with them."
        ),
    }


def get_example(name: str) -> dict:
    return EXAMPLES.get(name, {"emoji": "💬", "question": "", "followup": ""})
