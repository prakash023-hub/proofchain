"""
Walrus Memory integration for ProofChain.

Uses the same relayer as the TypeScript SDK:
  https://relayer.memory.walrus.xyz
"""

import os
from typing import List, Optional

from memwal import MemWalSync, RecallParams

DEFAULT_SERVER_URL = "https://relayer.memory.walrus.xyz"
DEFAULT_ACCOUNT_ID = "0xad3af9e3a609adcfdc698583724377b0d8c67a1c621198a44eecf97fe405bdfa"
DEFAULT_NAMESPACE = "proofchain"
MAX_RECALL_DISTANCE = 0.75


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

_clients: dict[str, MemWalSync] = {}
_PLACEHOLDERS = {"<your_private_key>", "<your-private-key>", "your-64-char-hex-key"}


def _normalize_key(raw: str) -> str:
    key = raw.strip().strip('"').strip("'")
    if key.startswith("0x"):
        key = key[2:]
    return key


def validate_key(raw: str | None) -> str | None:
    if not raw or not raw.strip():
        return "MEMWAL_PRIVATE_KEY is not set."
    key = _normalize_key(raw)
    lower = key.lower()
    if lower in _PLACEHOLDERS or "<" in key or ">" in key:
        return (
            "MEMWAL_PRIVATE_KEY is still the placeholder. "
            "Copy the real 64-char hex delegate key from the Walrus Memory dashboard."
        )
    if len(key) != 64:
        return f"MEMWAL_PRIVATE_KEY must be 64 hex chars. Yours is {len(key)} chars."
    try:
        int(key, 16)
    except ValueError:
        return "MEMWAL_PRIVATE_KEY must be hexadecimal only."
    return None


def is_configured() -> bool:
    key = os.environ.get("MEMWAL_PRIVATE_KEY")
    account_id = os.environ.get("MEMWAL_ACCOUNT_ID", DEFAULT_ACCOUNT_ID)
    return bool(key and account_id and validate_key(key) is None)


def get_client(namespace: str = DEFAULT_NAMESPACE) -> MemWalSync:
    if namespace in _clients:
        return _clients[namespace]

    raw_key = os.environ.get("MEMWAL_PRIVATE_KEY")
    err = validate_key(raw_key)
    if err:
        raise RuntimeError(err)

    key = _normalize_key(raw_key)
    account_id = os.environ.get("MEMWAL_ACCOUNT_ID", DEFAULT_ACCOUNT_ID)
    server_url = os.environ.get("MEMWAL_SERVER_URL", DEFAULT_SERVER_URL)

    client = MemWalSync.create(
        key=key,
        account_id=account_id,
        server_url=server_url,
        namespace=namespace,
    )
    _clients[namespace] = client
    return client


def _filter_decisions(memories, domain: str | None = None) -> List[str]:
    texts = []
    for m in memories:
        if m.distance >= MAX_RECALL_DISTANCE:
            continue
        if not m.text.startswith("ProofChain decision"):
            continue
        if domain and f"[{domain}]" not in m.text:
            continue
        texts.append(m.text)
    return texts


def recall_for_question(
    query: str, namespace: str, domain: str | None = None, limit: int = 5
) -> List[str]:
    if not is_configured():
        return []
    try:
        result = get_client(namespace).recall(
            RecallParams(query=query, limit=limit, max_distance=MAX_RECALL_DISTANCE)
        )
        return _filter_decisions(result.results, domain=domain)
    except Exception as exc:
        print(f"  (Walrus Memory recall skipped: {exc})")
        return []


def remember_decision(
    domain: str,
    namespace: str,
    question: str,
    answer: str,
    reasoning: str,
    walrus_blob_id: str,
    sui_record_id: str,
) -> Optional[str]:
    if not is_configured():
        return None
    text = (
        f"ProofChain decision [{domain}] — Q: {question} | A: {answer} | "
        f"Reasoning: {reasoning} | Walrus: {walrus_blob_id} | Sui: {sui_record_id}"
    )
    try:
        result = get_client(namespace).remember_and_wait(text)
        print(f"  Walrus Memory stored [{domain}] (blob: {result.blob_id})")
        return result.blob_id
    except Exception as exc:
        print(f"  (Walrus Memory remember skipped: {exc})")
        return None


def list_recent_memories(
    namespace: str | None = None,
    domain: str | None = None,
    query: str = "ProofChain decision",
    limit: int = 15,
) -> List[dict]:
    if not is_configured():
        return []
    ns = namespace or DEFAULT_NAMESPACE
    try:
        result = get_client(ns).recall(RecallParams(query=query, limit=limit))
        items = []
        for m in result.results:
            if not m.text.startswith("ProofChain decision"):
                continue
            if domain and domain != "Any domain" and f"[{domain}]" not in m.text:
                continue
            items.append({
                "text": m.text,
                "blob_id": m.blob_id,
                "distance": m.distance,
                "namespace": ns,
            })
        return items
    except Exception as exc:
        return [{"text": f"Memory recall failed: {exc}", "blob_id": "", "distance": 0, "namespace": ""}]
