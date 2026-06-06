/// ProofChain — Verifiable AI Decision Audit Log (Sui Move)
///
/// Compatible upgrade: original `DecisionRecord` / `DecisionLogged` / `log_decision`
/// unchanged. New types added alongside for registry + credential minting.
module audit_log::audit_log;

use std::string::String;

// ============================================================
// Original types (DO NOT change — required for package upgrade)
// ============================================================

public struct DecisionRecord has key, store {
    id: UID,
    agent_id: String,
    input_hash: String,
    output_hash: String,
    walrus_blob_id: String,
    timestamp: u64,
    creator: address,
}

public struct DecisionLogged has copy, drop {
    record_id: ID,
    agent_id: String,
    walrus_blob_id: String,
    timestamp: u64,
}

// ============================================================
// New types (added in v2 upgrade)
// ============================================================

/// Shared registry — agent increments on each certified decision
public struct DecisionRegistry has key {
    id: UID,
    total_decisions: u64,
}

/// Owned credential — minted to caller; carries domain + sequence metadata
public struct DecisionCredential has key, store {
    id: UID,
    record_id: ID,
    agent_id: String,
    domain: String,
    output_hash: String,
    walrus_blob_id: String,
    timestamp: u64,
    sequence: u64,
}

public struct RegistryCreated has copy, drop {
    registry_id: ID,
}

public struct CredentialMinted has copy, drop {
    credential_id: ID,
    record_id: ID,
    recipient: address,
    sequence: u64,
    domain: String,
}

// ============================================================
// Init (first publish only — does not re-run on upgrade)
// ============================================================

fun init(ctx: &mut TxContext) {
    let registry = DecisionRegistry {
        id: object::new(ctx),
        total_decisions: 0,
    };
    sui::event::emit(RegistryCreated { registry_id: object::id(&registry) });
    transfer::share_object(registry);
}

// ============================================================
// Entry functions
// ============================================================

/// One-time call after upgrade (init does not re-run on upgrade).
public entry fun create_registry(ctx: &mut TxContext) {
    let registry = DecisionRegistry {
        id: object::new(ctx),
        total_decisions: 0,
    };
    sui::event::emit(RegistryCreated { registry_id: object::id(&registry) });
    transfer::share_object(registry);
}

/// Original entry — unchanged signature and struct layout.
public entry fun log_decision(
    agent_id: String,
    input_hash: String,
    output_hash: String,
    walrus_blob_id: String,
    timestamp: u64,
    ctx: &mut TxContext,
) {
    let record = DecisionRecord {
        id: object::new(ctx),
        agent_id,
        input_hash,
        output_hash,
        walrus_blob_id,
        timestamp,
        creator: tx_context::sender(ctx),
    };
    sui::event::emit(DecisionLogged {
        record_id: object::id(&record),
        agent_id: record.agent_id,
        walrus_blob_id: record.walrus_blob_id,
        timestamp: record.timestamp,
    });
    transfer::share_object(record);
}

/// v2 entry — logs shared record + updates registry + mints credential.
public entry fun log_and_certify(
    registry: &mut DecisionRegistry,
    agent_id: String,
    domain: String,
    input_hash: String,
    output_hash: String,
    walrus_blob_id: String,
    timestamp: u64,
    ctx: &mut TxContext,
) {
    let sender = tx_context::sender(ctx);
    let sequence = registry.total_decisions + 1;
    registry.total_decisions = sequence;

    let record = DecisionRecord {
        id: object::new(ctx),
        agent_id,
        input_hash,
        output_hash,
        walrus_blob_id,
        timestamp,
        creator: sender,
    };
    let record_id = object::id(&record);

    sui::event::emit(DecisionLogged {
        record_id,
        agent_id: record.agent_id,
        walrus_blob_id: record.walrus_blob_id,
        timestamp: record.timestamp,
    });
    transfer::share_object(record);

    let credential = DecisionCredential {
        id: object::new(ctx),
        record_id,
        agent_id,
        domain,
        output_hash,
        walrus_blob_id,
        timestamp,
        sequence,
    };
    let credential_id = object::id(&credential);

    sui::event::emit(CredentialMinted {
        credential_id,
        record_id,
        recipient: sender,
        sequence,
        domain,
    });

    transfer::transfer(credential, sender);
}

// ============================================================
// View helpers
// ============================================================

public fun get_hashes(record: &DecisionRecord): (String, String) {
    (record.input_hash, record.output_hash)
}

public fun get_walrus_blob(record: &DecisionRecord): String {
    record.walrus_blob_id
}

public fun registry_total(registry: &DecisionRegistry): u64 {
    registry.total_decisions
}

public fun credential_record_id(credential: &DecisionCredential): ID {
    credential.record_id
}

public fun credential_sequence(credential: &DecisionCredential): u64 {
    credential.sequence
}
