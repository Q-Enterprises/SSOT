#!/usr/bin/env python3
"""
Tests for BinaryCompileCheckpoint.v1 validator.

Validates constitutional infrastructure for deterministic binary ingestion.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from validate_binary_compile_checkpoint import CheckpointValidator


def test_valid_checkpoint():
    """Test validation of a valid checkpoint."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_001",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert validator.validate(checkpoint), f"Valid checkpoint failed: {validator.errors}"
    print("✓ test_valid_checkpoint passed")


def test_missing_required_field():
    """Test that missing required fields are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_002",
        # Missing raw_binary_url
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with missing field"
    assert any("raw_binary_url" in err for err in validator.errors), \
        f"Should report missing raw_binary_url: {validator.errors}"
    print("✓ test_missing_required_field passed")


def test_invalid_checkpoint_id():
    """Test that invalid checkpoint IDs are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "invalid_prefix_001",  # Wrong prefix
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid checkpoint_id"
    assert any("bcc_v1_" in err for err in validator.errors), \
        f"Should report checkpoint_id format: {validator.errors}"
    print("✓ test_invalid_checkpoint_id passed")


def test_invalid_sha256():
    """Test that invalid SHA-256 hashes are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_003",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "not_a_valid_hash",  # Invalid hash
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid SHA-256"
    assert any("raw_binary_sha256" in err for err in validator.errors), \
        f"Should report SHA-256 error: {validator.errors}"
    print("✓ test_invalid_sha256 passed")


def test_invalid_compiler_version():
    """Test that invalid compiler versions are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_004",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2025.OLD_VERSION",  # Wrong version
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid compiler version"
    assert any("GOLD_BURN" in err for err in validator.errors), \
        f"Should report compiler version error: {validator.errors}"
    print("✓ test_invalid_compiler_version passed")


def test_invalid_node_id():
    """Test that invalid node IDs are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_005",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "wrong_prefix_node_01",  # Wrong prefix
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid node_id"
    assert any("beelink_ser8_" in err for err in validator.errors), \
        f"Should report node_id error: {validator.errors}"
    print("✓ test_invalid_node_id passed")


def test_invalid_staging_method():
    """Test that invalid staging methods are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_006",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "invalid_method",  # Invalid method
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid staging method"
    assert any("staging_method" in err for err in validator.errors), \
        f"Should report staging method error: {validator.errors}"
    print("✓ test_invalid_staging_method passed")


def test_invalid_timestamp():
    """Test that invalid timestamps are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_007",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "not-a-valid-timestamp",  # Invalid timestamp
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            "format_version": "pdf-1.7",
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with invalid timestamp"
    assert any("ISO 8601" in err for err in validator.errors), \
        f"Should report timestamp error: {validator.errors}"
    print("✓ test_invalid_timestamp passed")


def test_missing_determinism_proof_field():
    """Test that missing determinism proof fields are detected."""
    validator = CheckpointValidator()
    checkpoint = {
        "checkpoint_id": "bcc_v1_test_008",
        "raw_binary_url": "https://example.com/binary.pdf",
        "raw_binary_sha256": "a" * 64,
        "staged_artifact_path": "/var/ssot/staged/binary.pdf",
        "staged_artifact_sha256": "b" * 64,
        "compiler_version": "v2026.GOLD_BURN.1",
        "compile_timestamp": "2026-01-25T17:30:00Z",
        "node_id": "beelink_ser8_node_01",
        "determinism_proof": {
            "staging_method": "direct",
            # Missing format_version
            "reproducibility_hash": "c" * 64
        }
    }
    
    assert not validator.validate(checkpoint), "Should fail with missing determinism proof field"
    assert any("format_version" in err for err in validator.errors), \
        f"Should report missing format_version: {validator.errors}"
    print("✓ test_missing_determinism_proof_field passed")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_valid_checkpoint,
        test_missing_required_field,
        test_invalid_checkpoint_id,
        test_invalid_sha256,
        test_invalid_compiler_version,
        test_invalid_node_id,
        test_invalid_staging_method,
        test_invalid_timestamp,
        test_missing_determinism_proof_field,
    ]
    
    print("Running BinaryCompileCheckpoint.v1 validator tests...")
    print()
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
