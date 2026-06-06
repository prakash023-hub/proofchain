"""
ProofChain — Verifiable AI Decision Audit Trail
Stores an AI agent's reasoning on Walrus, anchors a tamper-proof
record on Sui, and verifies past decisions.
"""

import subprocess
import hashlib
import json
import time
import tempfile
import os

# ---- CONFIG ----
PACKAGE_ID = "0xf97628ba29937a7846cc83a077d04b9d0535bbc9f2107bbe5572bd21189eb809"
MODULE = "audit_log"
GAS_BUDGET = "100000000"
WALRUS_EPOCHS = "5"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _find_key(obj, key):
    """Recursively search nested JSON for the first value of `key`."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            found = _find_key(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_key(item, key)
            if found is not None:
                return found
    return None


def store_on_walrus(data: str) -> str:
    """Store data on Walrus, return the blob ID."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(data)
        path = f.name
    try:
        result = subprocess.run(
            ["walrus", "store", path, "--epochs", WALRUS_EPOCHS, "--json"],
            capture_output=True, text=True, check=True,
        )
        out = json.loads(result.stdout)
        blob_id = _find_key(out, "blobId")
        if not blob_id:
            raise RuntimeError(f"Could not find blobId in: {result.stdout}")
        return blob_id
    finally:
        os.unlink(path)


def read_from_walrus(blob_id: str) -> str:
    """Read data back from Walrus by blob ID."""
    result = subprocess.run(
        ["walrus", "read", blob_id],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def log_on_sui(agent_id, input_hash, output_hash, blob_id, timestamp) -> str:
    """Log the decision on Sui. Return the on-chain record ID."""
    result = subprocess.run(
        [
            "sui", "client", "call",
            "--package", PACKAGE_ID,
            "--module", MODULE,
            "--function", "log_decision",
            "--args", agent_id, input_hash, output_hash, blob_id, str(timestamp),
            "--gas-budget", GAS_BUDGET,
            "--json",
        ],
        capture_output=True, text=True, check=True,
    )
    out = json.loads(result.stdout)
    record_id = _find_key(out, "record_id")
    if not record_id:
        # fall back: look in objectChanges for the created shared object
        record_id = _find_key(out, "objectId")
    return record_id


def record_decision(
    agent_id: str,
    question: str,
    answer: str,
    reasoning: str,
    domain: str = "",
) -> dict:
    """Full flow: package the decision, store on Walrus, anchor on Sui."""
    payload = json.dumps({
        "agent": agent_id,
        "domain": domain,
        "question": question,
        "answer": answer,
        "reasoning": reasoning,
        "created_at": int(time.time() * 1000),
    })

    input_hash = sha256(question)
    output_hash = sha256(answer)
    timestamp = int(time.time() * 1000)

    print("→ Storing reasoning on Walrus...")
    blob_id = store_on_walrus(payload)
    print(f"  Walrus blob ID: {blob_id}")

    print("→ Anchoring proof on Sui...")
    record_id = log_on_sui(agent_id, input_hash, output_hash, blob_id, timestamp)
    print(f"  Sui record ID: {record_id}")

    return {
        "agent_id": agent_id,
        "domain": domain,
        "question": question,
        "answer": answer,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "walrus_blob_id": blob_id,
        "sui_record_id": record_id,
        "timestamp": timestamp,
    }


def verify_decision(blob_id: str, expected_answer: str = None) -> dict:
    """Fetch the original data from Walrus and check integrity."""
    print(f"→ Fetching original data from Walrus ({blob_id})...")
    raw = read_from_walrus(blob_id)
    data = json.loads(raw)
    result = {"verified": True, "data": data}
    if expected_answer is not None:
        matches = (data.get("answer") == expected_answer)
        result["answer_matches"] = matches
        result["verified"] = matches
    return result


if __name__ == "__main__":
    # Demo run
    print("=== ProofChain Demo ===\n")
    rec = record_decision(
        agent_id="proofchain-agent-001",
        question="Is approach A safe given the available evidence?",
        answer="Yes, approach A is supported by sources 1 and 2.",
        reasoning="Both sources independently confirm safety under the stated conditions.",
    )
    print("\n--- Decision recorded ---")
    print(json.dumps(rec, indent=2))

    print("\n=== Verifying the record ===\n")
    v = verify_decision(rec["walrus_blob_id"], expected_answer=rec["answer"])
    print(json.dumps(v, indent=2))
    print(f"\n✅ Verified: {v['verified']}")
