import pytest
from ssot.sovereign_gates import extract_invariants, ReplayCapsule, ReplayReceipt, GateError

def h(i):
    return f"sha256:{i:064x}"

def test_extract_invariants_valid():
    receipts = [
        ReplayReceipt(tick=0, tick_hash=h(0), prev_tick_hash=None),
        ReplayReceipt(tick=1, tick_hash=h(1), prev_tick_hash=h(0)),
        ReplayReceipt(tick=10, tick_hash=h(2), prev_tick_hash=h(1)),
    ]
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=receipts)
    result = extract_invariants(capsule, extractor_version="1.0")
    assert result.tick_count == 3
    assert result.world_id == "w1"

def test_extract_invariants_empty():
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=[])
    with pytest.raises(GateError, match="ReplayCapsule must include at least one receipt"):
        extract_invariants(capsule, extractor_version="1.0")

def test_extract_invariants_single():
    receipts = [ReplayReceipt(tick=5, tick_hash=h(5), prev_tick_hash=None)]
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=receipts)
    result = extract_invariants(capsule, extractor_version="1.0")
    assert result.tick_count == 1

def test_extract_invariants_unsorted():
    receipts = [
        ReplayReceipt(tick=10, tick_hash=h(10), prev_tick_hash=None),
        ReplayReceipt(tick=5, tick_hash=h(5), prev_tick_hash=h(10)),
    ]
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=receipts)
    with pytest.raises(GateError, match="Receipts must be sorted by ascending tick"):
        extract_invariants(capsule, extractor_version="1.0")

def test_extract_invariants_duplicate():
    receipts = [
        ReplayReceipt(tick=10, tick_hash=h(10), prev_tick_hash=None),
        ReplayReceipt(tick=10, tick_hash=h(11), prev_tick_hash=h(10)),
    ]
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=receipts)
    with pytest.raises(GateError, match="Receipts must not include duplicate ticks"):
        extract_invariants(capsule, extractor_version="1.0")

def test_extract_invariants_hash_mismatch():
    receipts = [
        ReplayReceipt(tick=0, tick_hash=h(0), prev_tick_hash=None),
        ReplayReceipt(tick=1, tick_hash=h(1), prev_tick_hash=h(999)),
    ]
    capsule = ReplayCapsule(world_id="w1", capsule_digest=h(100), receipts=receipts)
    with pytest.raises(GateError, match="Receipt chain integrity failure: prev_tick_hash mismatch"):
        extract_invariants(capsule, extractor_version="1.0")
