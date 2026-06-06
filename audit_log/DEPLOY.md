# ProofChain Move Contract — Deploy & Upgrade

## Build & test

```bash
cd ~/proofchain/audit_log
sui move build
sui move test
```

## Upgrade existing testnet package (recommended)

Your package is already live. Use the upgrade capability from `Published.toml`:

```bash
cd ~/proofchain/audit_log
sui client upgrade \
  --upgrade-capability 0x80f3bf4374c0512bcd85744525a650acef86a16a13fe167f8f92829e37e4c60e \
  --gas-budget 200000000
```

Package ID v2: `0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809`  
Original ID: `0xf97628ba29937a7846cc83a077d04b9d0535bbc9f2107bbe5572bd21189eb809`

## Create registry (once after upgrade)

`init` only runs on first publish. After upgrade, run once:

```bash
sui client call \
  --package 0x352fffa5eb8f0f8b63ee100efc8373e1abffa2ad3f0eece9a12617d4f8764809 \
  --module audit_log \
  --function create_registry \
  --gas-budget 100000000 \
  --json
```

Copy the shared `DecisionRegistry` object ID from the output into `.env`:

```
SUI_REGISTRY_ID=0x...
```

## Primary entry function

`log_and_certify` — agent logs decision + updates registry + mints `DecisionCredential` to your wallet.

Python calls this automatically when `SUI_REGISTRY_ID` is set.

## Objects on Sui

| Object | Type | Purpose |
|---|---|---|
| `DecisionRecord` | shared | Public audit log entry |
| `DecisionRegistry` | shared | Total certified decisions counter |
| `DecisionCredential` | owned | Wallet-held proof of certification |
