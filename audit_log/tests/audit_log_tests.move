#[test_only]
module audit_log::audit_log_tests;

use audit_log::audit_log::{Self, DecisionCredential, DecisionRecord, DecisionRegistry};
use std::string;
use sui::test_scenario::{Self as ts, Scenario};

const AGENT: vector<u8> = b"proofchain-agent-001";
const DOMAIN: vector<u8> = b"Healthcare";
const INPUT_HASH: vector<u8> = b"abc123inputhash00000000000000000000000000000000000000000001";
const OUTPUT_HASH: vector<u8> = b"def456outputhash0000000000000000000000000000000000000000001";
const BLOB_ID: vector<u8> = b"walrus-blob-id-xyz";
const TS: u64 = 1_700_000_000_000;

#[test]
fun test_create_registry_and_log_and_certify() {
    let mut scenario = ts::begin(@0xA);
    let agent_id = string::utf8(AGENT);
    let domain = string::utf8(DOMAIN);
    let input_hash = string::utf8(INPUT_HASH);
    let output_hash = string::utf8(OUTPUT_HASH);
    let blob_id = string::utf8(BLOB_ID);

    ts::next_tx(&mut scenario, @0xA);
    {
        audit_log::create_registry(ts::ctx(&mut scenario));
    };

    ts::next_tx(&mut scenario, @0xA);
    {
        let mut registry = ts::take_shared<DecisionRegistry>(&scenario);
        audit_log::log_and_certify(
            &mut registry,
            agent_id,
            domain,
            input_hash,
            output_hash,
            blob_id,
            TS,
            ts::ctx(&mut scenario),
        );
        ts::return_shared(registry);
    };

    ts::next_tx(&mut scenario, @0xA);
    {
        let registry = ts::take_shared<DecisionRegistry>(&scenario);
        assert!(audit_log::registry_total(&registry) == 1, 0);
        ts::return_shared(registry);
    };

    ts::next_tx(&mut scenario, @0xA);
    {
        let credential = ts::take_from_sender<DecisionCredential>(&scenario);
        assert!(audit_log::credential_sequence(&credential) == 1, 1);
        let _ = audit_log::credential_record_id(&credential);
        ts::return_to_sender(&scenario, credential);
    };

    ts::next_tx(&mut scenario, @0xA);
    {
        let record = ts::take_shared<DecisionRecord>(&scenario);
        let (inp, out) = audit_log::get_hashes(&record);
        assert!(inp == string::utf8(INPUT_HASH), 2);
        assert!(out == string::utf8(OUTPUT_HASH), 3);
        ts::return_shared(record);
    };

    ts::end(scenario);
}

#[test]
fun test_legacy_log_decision() {
    let mut scenario = ts::begin(@0xB);
    ts::next_tx(&mut scenario, @0xB);
    {
        audit_log::log_decision(
            string::utf8(AGENT),
            string::utf8(INPUT_HASH),
            string::utf8(OUTPUT_HASH),
            string::utf8(BLOB_ID),
            TS,
            ts::ctx(&mut scenario),
        );
    };
    ts::next_tx(&mut scenario, @0xB);
    {
        let record = ts::take_shared<DecisionRecord>(&scenario);
        assert!(audit_log::get_walrus_blob(&record) == string::utf8(BLOB_ID), 4);
        ts::return_shared(record);
    };
    ts::end(scenario);
}
