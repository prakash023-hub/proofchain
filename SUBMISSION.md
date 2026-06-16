# DeepSurge Submission — ProofChain

**Portal:** https://www.deepsurge.xyz/hackathons/b587dc0c-4cb8-4e63-ada5-519df38103bf  
**Deadline:** June 20–21, 2026 · **Track:** Special - Walrus (pick ONE track only)

Copy each section below into the form. Replace `YOUR_VIDEO_ID` after YouTube upload.

---

## Project name

```
ProofChain
```

---

## One-line description (tagline)

```
Verifiable AI audit trail — every agent decision stored on Walrus Memory, anchored on Sui, tamper-proof forever.
```

---

## Project logo

Upload: `assets/logo.png` (512×512 PNG, 1:1)

---

## GitHub repository

```
https://github.com/prakash023-hub/proofchain
```

---

## Demo video (≤5 min, YouTube unlisted)

```
https://youtu.be/YOUR_VIDEO_ID
```

---

## Sui package ID (testnet)

```
0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809
```

**Registry ID:** `0x23c42a96b6272bc85d81eb25a9069ffa720b60243c784d1e1daf357e5beb65fa`

**Explorer:** https://suiscan.xyz/testnet/object/0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809

---

## Full description (paste into long text field)

```
ProofChain solves AI accountability. Today, LLM decisions are unverifiable — you cannot prove what an AI decided, whether outputs were altered, or what it remembered from prior sessions.

ProofChain is like ChatGPT for high-stakes decisions in any domain (healthcare, legal, finance, education, HR, supply chain) — but every answer runs through a verifiable pipeline:

1. Walrus Memory recalls relevant past decisions across browser sessions
2. A local Ollama agent produces a decision + reasoning (no cloud API keys)
3. The full record is stored on Walrus as an off-chain blob
4. A tamper-proof hash is anchored on Sui testnet via our Move smart contract (log_and_certify)
5. The decision is remembered in Walrus Memory for future sessions
6. Anyone can verify integrity or detect tampering instantly

Why Walrus: We use both Walrus blob storage AND Walrus Memory (June 2026) — one of the first production-style apps on the full Walrus AI memory stack.

Live on Sui testnet:
- Package v2: 0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809
- Move: log_and_certify mints DecisionCredential NFT + DecisionRegistry counter
- Tamper demo: change one word → hash mismatch → verification fails

GitHub: https://github.com/prakash023-hub/proofchain
```

---

## Track selection

- **Primary:** Special - Walrus
- **Also demonstrates:** Agentic Web (autonomous agent records on Sui)

---

## 30-second pitch (Demo Day / video close)

> AI is a black box. ProofChain fixes that. Every decision is recalled from Walrus Memory, stored on Walrus, and anchored on Sui. Change one word — verification fails instantly. Built on Walrus Memory + Sui Move — ProofChain.

---

## 3-minute video script (record this)

| Time | Action | Say |
|------|--------|-----|
| 0:00 | Overview tab | "AI decisions are unverifiable. ProofChain makes every answer provable — Walrus Memory, Walrus storage, Sui proof." |
| 0:20 | Ask → Healthcare example → Ask & Record | "Real healthcare decision. Watch the full pipeline run." |
| 1:00 | Point at Walrus blob + Sui link + credential | "Stored on Walrus, anchored on Sui, remembered in Walrus Memory." |
| 1:20 | Memory tab → Load past decisions | "Decisions persist across sessions." |
| 1:40 | Verify → Verify integrity | "Anyone can verify — hashes match." |
| 2:00 | Simulate tampering | "Change one word — tampering detected. That's ProofChain." |
| 2:20 | On-chain tab | "Move v2: log_and_certify, registry, DecisionCredential." |
| 2:40 | Close | "Open source at github.com/prakash023-hub/proofchain. Sui Overflow 2026, Walrus track." |

**Record:** Mac `Cmd+Shift+5` · **Edit:** CapCut · **Upload:** YouTube unlisted

---

## Serious steps — do in order (today + tomorrow)

### Today (non-negotiable)

```bash
# Terminal 1
ollama serve

# Terminal 2
cd ~/proofchain && source venv/bin/activate
python test_memwal.py          # must pass
python app.py                  # record at http://127.0.0.1:7860
```

1. [ ] Record 3–4 min video (script above)
2. [ ] Upload YouTube **unlisted** — title: `ProofChain — Verifiable AI | Walrus Memory + Sui | Sui Overflow 2026`
3. [ ] Replace `YOUR_VIDEO_ID` in this file

### Tomorrow

4. [ ] Open DeepSurge portal → Submit Project → paste all fields above
5. [ ] Upload `assets/logo.png`
6. [ ] Track: **Special - Walrus** → click **Submit**
7. [ ] DeepSurge profile → **KYC** (required to receive prize money)

### Optional (boosts odds)

```bash
python app.py --share    # 72h public gradio.live link — paste in README + DeepSurge if form has website field
```

---

## Tools cheat sheet

| Goal | App |
|------|-----|
| Screen record | QuickTime (`Cmd+Shift+5`) or OBS |
| Edit video | CapCut (free) |
| Logo | `assets/logo.png` (included in repo) |
| Public demo link | `python app.py --share` |
| Submit | DeepSurge portal (link above) |
| KYC | DeepSurge profile settings |

---

## Checklist

- [x] GitHub: `prakash023-hub/proofchain`
- [x] Move v2 on GitHub (`fc4a4df6`)
- [x] Testnet package + registry deployed
- [x] Logo: `assets/logo.png`
- [x] Walrus Memory + Walrus + Sui pipeline working
- [ ] Demo video on YouTube
- [ ] DeepSurge form submitted
- [ ] KYC completed
- [ ] Wallet connected on DeepSurge (Slush)

---

## How judges run it

```bash
git clone https://github.com/prakash023-hub/proofchain.git
cd proofchain && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Walrus Memory key + SUI_REGISTRY_ID
python test_memwal.py
python app.py
```

Requires: Sui CLI, Walrus CLI, Ollama (`gemma3:1b`) — see README.md.
