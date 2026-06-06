# DeepSurge Submission — ProofChain

Copy/paste sections below into the Sui Overflow submission form.

---

## Project name

**ProofChain**

---

## One-line description

Verifiable AI audit trail — every agent decision stored on Walrus Memory, anchored on Sui, tamper-proof forever.

---

## Track

**Walrus** (primary)

Also demonstrates Agentic Web: autonomous agent records decisions on Sui testnet.

---

## Full description

ProofChain solves AI accountability. Today, LLM decisions are unverifiable — you cannot prove what an AI decided, whether outputs were altered, or what it remembered from prior sessions.

ProofChain is like ChatGPT for high-stakes decisions in **any domain** (healthcare, legal, finance, education, HR, etc.) — but every answer runs through a verifiable pipeline:

1. **Walrus Memory** recalls relevant past decisions across browser sessions
2. A **local Ollama agent** produces a decision + reasoning (no cloud API keys)
3. The full record is stored on **Walrus** as an off-chain blob
4. A tamper-proof hash is anchored on **Sui testnet** via our Move smart contract
5. The decision is **remembered** in Walrus Memory for future sessions
6. Anyone can **verify integrity** or **detect tampering** instantly

**Why Walrus:** We use both Walrus blob storage AND the newly launched Walrus Memory (June 2026) — making ProofChain one of the first production-style apps built on the full Walrus AI memory stack.

**Live contract (v2):** `0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809` (Sui testnet)  
**Move functions:** `log_and_certify` (mints DecisionCredential) · `DecisionRegistry` on-chain counter

---

## GitHub repository

`https://github.com/prakash023-hub/proofchain`

---

## Demo video

`https://youtu.be/YOUR_VIDEO_ID` *(add after recording)*

---

## How to run

```bash
git clone https://github.com/prakash023-hub/proofchain.git
cd proofchain && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add Walrus Memory delegate key
python test_memwal.py
python app.py          # open http://127.0.0.1:7860
```

Requires: Sui CLI, Walrus CLI, Ollama — see README.md.

---

## 30-second pitch (Demo Day)

> "AI is a black box. ProofChain fixes that. Every decision is stored on Walrus Memory, the full reasoning on Walrus, and a tamper-proof hash on Sui. Watch — I change one word and verification fails instantly. Built on Walrus Memory and Sui testnet — ProofChain."

---

## Checklist before submit

- [x] GitHub repo: `prakash023-hub/proofchain`
- [ ] Push Move v2 upgrade to GitHub (pending commit)
- [ ] Record demo video (≤5 min, YouTube)
- [ ] Add video URL above
- [ ] Submit on DeepSurge (deadline: **June 20, 2026**)
- [ ] Wallet connected on DeepSurge profile
- [ ] Select track: **Special - Walrus**
