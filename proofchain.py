"""
ProofChain — Verifiable AI Decision Audit Trail
Stores an AI agent's reasoning on Walrus, anchors a tamper-proof
record on Sui via Move smart contract, mints DecisionCredential.
"""

import subprocess
import hashlib
import json
import time
import tempfile
import os

# ---- CONFIG ----
PACKAGE_ID = "0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809"
MODULE = "audit_log"
GAS_BUDGET = "100000000"
WALRUS_EPOCHS = "5"


def _load_dotenv() -> None:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

REGISTRY_ID = os.environ.get("SUI_REGISTRY_ID", "")


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


def _find_all_keys(obj, key) -> list:
    """Collect all values for `key` in nested JSON."""
    found = []
    if isinstance(obj, dict):
        if key in obj:
            found.append(obj[key])
        for v in obj.values():
            found.extend(_find_all_keys(v, key))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_find_all_keys(item, key))
    return found


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


def log_on_sui(
    agent_id: str,
    input_hash: str,
    output_hash: str,
    blob_id: str,
    timestamp: int,
    domain: str = "",
) -> dict:
    """Log decision on Sui via Move. Returns record + credential IDs when available."""
    registry_id = os.environ.get("SUI_REGISTRY_ID", REGISTRY_ID)

    if registry_id:
        return _log_and_certify(
            registry_id, agent_id, domain or "Any domain",
            input_hash, output_hash, blob_id, timestamp,
        )
    return _log_decision_legacy(
        agent_id, input_hash, output_hash, blob_id, timestamp,
    )


def _log_and_certify(
    registry_id: str,
    agent_id: str,
    domain: str,
    input_hash: str,
    output_hash: str,
    blob_id: str,
    timestamp: int,
) -> dict:
    """Call Move `log_and_certify` — registry update + credential mint."""
    result = subprocess.run(
        [
            "sui", "client", "call",
            "--package", PACKAGE_ID,
            "--module", MODULE,
            "--function", "log_and_certify",
            "--args",
            registry_id,
            agent_id,
            domain,
            input_hash,
            output_hash,
            blob_id,
            str(timestamp),
            "--gas-budget", GAS_BUDGET,
            "--json",
        ],
        capture_output=True, text=True, check=True,
    )
    out = json.loads(result.stdout)
    object_ids = _find_all_keys(out, "objectId")
    record_id = object_ids[0] if object_ids else _find_key(out, "objectId")
    credential_id = object_ids[1] if len(object_ids) > 1 else None
    return {
        "record_id": record_id,
        "credential_id": credential_id,
        "move_function": "log_and_certify",
    }


def _log_decision_legacy(
    agent_id: str,
    input_hash: str,
    output_hash: str,
    blob_id: str,
    timestamp: int,
) -> dict:
    """Fallback: original `log_decision` without credential mint."""
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
    record_id = _find_key(out, "record_id") or _find_key(out, "objectId")
    return {
        "record_id": record_id,
        "credential_id": None,
        "move_function": "log_decision",
    }


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

    print("→ Anchoring proof on Sui (Move)...")
    sui_result = log_on_sui(
        agent_id, input_hash, output_hash, blob_id, timestamp, domain=domain,
    )
    record_id = sui_result["record_id"]
    credential_id = sui_result.get("credential_id")
    move_fn = sui_result.get("move_function", "log_decision")
    print(f"  Sui record ID: {record_id}")
    print(f"  Move function: {move_fn}")
    if credential_id:
        print(f"  DecisionCredential minted: {credential_id}")
    elif not os.environ.get("SUI_REGISTRY_ID"):
        print("  (Set SUI_REGISTRY_ID in .env after upgrade — see audit_log/DEPLOY.md)")

    return {
        "agent_id": agent_id,
        "domain": domain,
        "question": question,
        "answer": answer,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "walrus_blob_id": blob_id,
        "sui_record_id": record_id,
        "sui_credential_id": credential_id,
        "move_function": move_fn,
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
    print("=== ProofChain Demo ===\n")
    rec = record_decision(
        agent_id="proofchain-agent-001",
        question="Is approach A safe given the available evidence?",
        answer="Yes, approach A is supported by sources 1 and 2.",
        reasoning="Both sources independently confirm safety under the stated conditions.",
        domain="Healthcare",
    )
    print("\n--- Decision recorded ---")
    print(json.dumps(rec, indent=2))

    print("\n=== Verifying the record ===\n")
    v = verify_decision(rec["walrus_blob_id"], expected_answer=rec["answer"])
    print(json.dumps(v, indent=2))
    print(f"\n✅ Verified: {v['verified']}")
