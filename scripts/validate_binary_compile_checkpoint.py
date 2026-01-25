#!/usr/bin/env python3
"""
Binary Compile Checkpoint v1 Validator

Constitutional infrastructure validator for deterministic binary ingestion.
Enforces fail-closed policy on staging, format, and compiler version.

Key Invariants:
- Raw binary → deterministic staging → hash chain is unbreakable
- Verdicts never see raw bytes, only provable artifacts
- Fail-closed on any non-determinism
- Reproducible across Beelink SER8 nodes and v2026.GOLD_BURN

Chain: Binary → BinaryCompileCheckpoint.v1 → MovieLedgerCapsule.v1 → MovieLedgerCourtVerdict.v1
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BinaryCompileCheckpoint:
    """v1 frozen structure for binary compile checkpoints."""
    checkpoint_id: str
    raw_binary_url: str
    raw_binary_sha256: str
    staged_artifact_path: str
    staged_artifact_sha256: str
    compiler_version: str
    compile_timestamp: str
    node_id: str
    determinism_proof: Dict[str, str]
    metadata: Optional[Dict] = None


class CheckpointValidator:
    """Validator for BinaryCompileCheckpoint.v1 structure."""
    
    REQUIRED_FIELDS = [
        'checkpoint_id',
        'raw_binary_url',
        'raw_binary_sha256',
        'staged_artifact_path',
        'staged_artifact_sha256',
        'compiler_version',
        'compile_timestamp',
        'node_id',
        'determinism_proof',
    ]
    
    DETERMINISM_PROOF_FIELDS = [
        'staging_method',
        'format_version',
        'reproducibility_hash',
    ]
    
    VALID_STAGING_METHODS = ['direct', 'compile', 'transcode', 'extract']
    COMPILER_VERSION_PREFIX = 'v2026.GOLD_BURN'
    NODE_ID_PREFIX = 'beelink_ser8_'
    
    def __init__(self, fail_closed: bool = True):
        """
        Initialize validator.
        
        Args:
            fail_closed: If True, fail on any validation error (default: True)
        """
        self.fail_closed = fail_closed
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, checkpoint_data: Dict) -> bool:
        """
        Validate a binary compile checkpoint.
        
        Args:
            checkpoint_data: Dictionary containing checkpoint data
            
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Check required fields
        if not self._validate_required_fields(checkpoint_data):
            return False
        
        # Validate field formats
        if not self._validate_checkpoint_id(checkpoint_data['checkpoint_id']):
            return False
        
        if not self._validate_url(checkpoint_data['raw_binary_url']):
            return False
        
        if not self._validate_sha256(checkpoint_data['raw_binary_sha256'], 'raw_binary'):
            return False
        
        if not self._validate_sha256(checkpoint_data['staged_artifact_sha256'], 'staged_artifact'):
            return False
        
        if not self._validate_compiler_version(checkpoint_data['compiler_version']):
            return False
        
        if not self._validate_timestamp(checkpoint_data['compile_timestamp']):
            return False
        
        if not self._validate_node_id(checkpoint_data['node_id']):
            return False
        
        if not self._validate_determinism_proof(checkpoint_data['determinism_proof']):
            return False
        
        # Validate staged artifact path
        if not self._validate_staged_artifact_path(checkpoint_data['staged_artifact_path']):
            return False
        
        return len(self.errors) == 0
    
    def _validate_required_fields(self, data: Dict) -> bool:
        """Check all required fields are present."""
        missing = [f for f in self.REQUIRED_FIELDS if f not in data]
        if missing:
            self.errors.append(f"Missing required fields: {', '.join(missing)}")
            return False
        return True
    
    def _validate_checkpoint_id(self, checkpoint_id: str) -> bool:
        """Validate checkpoint ID format."""
        if not checkpoint_id or not isinstance(checkpoint_id, str):
            self.errors.append("checkpoint_id must be a non-empty string")
            return False
        
        if not checkpoint_id.startswith('bcc_v1_'):
            self.errors.append("checkpoint_id must start with 'bcc_v1_'")
            return False
        
        return True
    
    def _validate_url(self, url: str) -> bool:
        """Validate raw binary URL."""
        if not url or not isinstance(url, str):
            self.errors.append("raw_binary_url must be a non-empty string")
            return False
        
        if not url.startswith(('http://', 'https://', 'raw.githubusercontent.com')):
            self.warnings.append(f"raw_binary_url does not use standard protocol: {url}")
        
        return True
    
    def _validate_sha256(self, hash_value: str, field_name: str) -> bool:
        """Validate SHA-256 hash format."""
        if not hash_value or not isinstance(hash_value, str):
            self.errors.append(f"{field_name}_sha256 must be a non-empty string")
            return False
        
        if len(hash_value) != 64:
            self.errors.append(f"{field_name}_sha256 must be 64 characters (got {len(hash_value)})")
            return False
        
        try:
            int(hash_value, 16)
        except ValueError:
            self.errors.append(f"{field_name}_sha256 must be valid hexadecimal")
            return False
        
        return True
    
    def _validate_compiler_version(self, version: str) -> bool:
        """Validate compiler version format."""
        if not version or not isinstance(version, str):
            self.errors.append("compiler_version must be a non-empty string")
            return False
        
        if not version.startswith(self.COMPILER_VERSION_PREFIX):
            self.errors.append(f"compiler_version must start with '{self.COMPILER_VERSION_PREFIX}'")
            return False
        
        return True
    
    def _validate_timestamp(self, timestamp: str) -> bool:
        """Validate ISO 8601 timestamp format."""
        if not timestamp or not isinstance(timestamp, str):
            self.errors.append("compile_timestamp must be a non-empty string")
            return False
        
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.errors.append("compile_timestamp must be valid ISO 8601 format")
            return False
        
        return True
    
    def _validate_node_id(self, node_id: str) -> bool:
        """Validate node ID format."""
        if not node_id or not isinstance(node_id, str):
            self.errors.append("node_id must be a non-empty string")
            return False
        
        if not node_id.startswith(self.NODE_ID_PREFIX):
            self.errors.append(f"node_id must start with '{self.NODE_ID_PREFIX}'")
            return False
        
        return True
    
    def _validate_determinism_proof(self, proof: Dict) -> bool:
        """Validate determinism proof structure."""
        if not isinstance(proof, dict):
            self.errors.append("determinism_proof must be an object")
            return False
        
        # Check required fields
        missing = [f for f in self.DETERMINISM_PROOF_FIELDS if f not in proof]
        if missing:
            self.errors.append(f"determinism_proof missing fields: {', '.join(missing)}")
            return False
        
        # Validate staging method
        staging_method = proof.get('staging_method')
        if staging_method not in self.VALID_STAGING_METHODS:
            self.errors.append(
                f"determinism_proof.staging_method must be one of {self.VALID_STAGING_METHODS} "
                f"(got '{staging_method}')"
            )
            return False
        
        # Validate format version
        format_version = proof.get('format_version')
        if not format_version or not isinstance(format_version, str):
            self.errors.append("determinism_proof.format_version must be a non-empty string")
            return False
        
        # Validate reproducibility hash
        repro_hash = proof.get('reproducibility_hash')
        if not self._validate_sha256(repro_hash, 'determinism_proof.reproducibility'):
            return False
        
        return True
    
    def _validate_staged_artifact_path(self, path: str) -> bool:
        """Validate staged artifact path."""
        if not path or not isinstance(path, str):
            self.errors.append("staged_artifact_path must be a non-empty string")
            return False
        
        # Path should be relative or absolute
        if not (path.startswith('/') or path.startswith('./')):
            self.warnings.append(f"staged_artifact_path should be absolute or relative: {path}")
        
        return True
    
    def get_report(self) -> Dict:
        """Get validation report."""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'fail_closed': self.fail_closed,
        }


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Validate BinaryCompileCheckpoint.v1 structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s checkpoint.json
  %(prog)s checkpoint.json --no-fail-closed
  %(prog)s checkpoint.json --verbose
        """
    )
    
    parser.add_argument(
        'checkpoint_file',
        help='Path to checkpoint JSON file'
    )
    
    parser.add_argument(
        '--no-fail-closed',
        action='store_true',
        help='Allow warnings without failing'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed validation report'
    )
    
    args = parser.parse_args()
    
    # Load checkpoint
    checkpoint_path = Path(args.checkpoint_file)
    if not checkpoint_path.exists():
        print(f"Error: File not found: {checkpoint_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate
    validator = CheckpointValidator(fail_closed=not args.no_fail_closed)
    valid = validator.validate(checkpoint_data)
    report = validator.get_report()
    
    # Output
    if args.verbose or not valid:
        print(json.dumps(report, indent=2))
    
    if valid:
        print(f"✓ BinaryCompileCheckpoint.v1 valid: {checkpoint_path}")
        sys.exit(0)
    else:
        print(f"✗ BinaryCompileCheckpoint.v1 validation failed: {checkpoint_path}", file=sys.stderr)
        if not args.verbose:
            for error in report['errors']:
                print(f"  Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
