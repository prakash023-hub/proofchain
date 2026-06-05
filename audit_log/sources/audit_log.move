/// ProofChain — Verifiable AI Decision Audit Log
/// Stores a tamper-proof record of what an AI agent decided,
/// what data it used (Walrus blob), and when.
module audit_log::audit_log;

use std::string::String;

/// A single verifiable AI decision record
public struct DecisionRecord has key, store {
    id: UID,
    agent_id: String,        // which agent made the decision
    input_hash: String,      // hash of the input/question
    output_hash: String,     // hash of the AI's decision/output
    walrus_blob_id: String,  // Walrus blob holding the source data
    timestamp: u64,          // when it was recorded
    creator: address,        // who submitted it
}

/// Event emitted when a decision is logged (for easy querying)
public struct DecisionLogged has copy, drop {
    record_id: ID,
    agent_id: String,
    walrus_blob_id: String,
    timestamp: u64,
}

/// Log a new AI decision on-chain. Anyone can call this.
public entry fun log_decision(
    agent_id: String,
    input_hash: String,
    output_hash: String,
    walrus_blob_id: String,
    timestamp: u64,
    ctx: &mut TxContext
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

    // Make the record a shared object so anyone can verify it
    transfer::share_object(record);
}

/// Read fields from a record (for verification)
public fun get_hashes(record: &DecisionRecord): (String, String) {
    (record.input_hash, record.output_hash)
}

public fun get_walrus_blob(record: &DecisionRecord): String {
    record.walrus_blob_id
}
