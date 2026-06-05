"""Quick health check for Walrus Memory credentials."""

import os
import sys

from memwal import MemWalSync


def main() -> int:
    key = os.environ.get("MEMWAL_PRIVATE_KEY")
    account_id = os.environ.get("MEMWAL_ACCOUNT_ID")
    env = os.environ.get("MEMWAL_ENV", "prod")

    if not key or not account_id:
        print("Missing credentials. Set MEMWAL_PRIVATE_KEY and MEMWAL_ACCOUNT_ID.")
        print("Copy .env.example to .env and fill in values from the Walrus Memory dashboard.")
        return 1

    print(f"Connecting to Walrus Memory (env={env})...")
    client = MemWalSync.create(key=key, account_id=account_id, env=env)
    health = client.health()
    print(f"memwal works — server status: {health.status}, version: {health.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
