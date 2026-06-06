"""Test Walrus Memory — uses namespace 'test' so demo data stays clean."""

import os
import sys

from memwal import MemWalSync

from memory import (
    DEFAULT_ACCOUNT_ID,
    DEFAULT_SERVER_URL,
    _normalize_key,
    validate_key,
)


def main() -> int:
    err = validate_key(os.environ.get("MEMWAL_PRIVATE_KEY"))
    if err:
        print(f"ERROR: {err}")
        print("\nFix your ~/proofchain/.env file:")
        print(f"  MEMWAL_PRIVATE_KEY=<paste 64-char hex from Walrus dashboard>")
        print(f"  MEMWAL_ACCOUNT_ID={DEFAULT_ACCOUNT_ID}")
        print(f"  MEMWAL_SERVER_URL={DEFAULT_SERVER_URL}")
        return 1

    server_url = os.environ.get("MEMWAL_SERVER_URL", DEFAULT_SERVER_URL)
    account_id = os.environ.get("MEMWAL_ACCOUNT_ID", DEFAULT_ACCOUNT_ID)
    key = _normalize_key(os.environ["MEMWAL_PRIVATE_KEY"])

    print(f"Server: {server_url}")
    print(f"Account: {account_id}")
    print("Namespace: test (won't mix with ProofChain demo)")

    client = MemWalSync.create(
        key=key,
        account_id=account_id,
        server_url=server_url,
        namespace="test",
    )

    print("\n1. Health check...")
    health = client.health()
    print(f"   status={health.status}, version={health.version}")

    print("\n2. Remember test fact...")
    job = client.remember("I'm allergic to peanuts")
    result = client.wait_for_remember_job(job.job_id)
    print(f"   stored blob_id={result.blob_id}")

    print("\n3. Recall test...")
    recall = client.recall("food allergies")
    if recall.results:
        print(f"   recalled: {recall.results[0].text}")
    else:
        print("   (no results yet — may need a few seconds)")

    print("\nmemwal works")
    return 0


if __name__ == "__main__":
    sys.exit(main())
