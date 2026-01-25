# Qube - Query and Orchestration Framework

The `qube` module provides the query parsing and orchestration framework for the SSOT (Single Source of Truth) system.

## Components

### Qbert Query Parser

`qbert_query_parser.py` - A natural language query parser for the Qube orchestrator system.

**Features:**
- Parses gaming-themed and natural language queries
- Supports multiple query types: capsule lookup, script search, artifact finding, lineage tracing, telemetry checks, and relay status
- Detects gaming culture references (Q*bert, Street Fighter, etc.)
- Structured query output for downstream processing

**Usage:**

```python
from qube.qbert_query_parser import create_parser

parser = create_parser()
result = parser.parse("capsule qube cinematic v1")

print(result.query_type)  # QueryType.CAPSULE_LOOKUP
print(result.filters)      # {'version': 'v1', 'namespace': 'qube'}
```

**Supported Query Types:**
- `CAPSULE_LOOKUP` - Find capsule definitions
- `SCRIPT_SEARCH` - Search for scripts
- `ARTIFACT_FIND` - Locate artifacts
- `LINEAGE_TRACE` - Trace capsule lineage and forks
- `TELEMETRY_CHECK` - Check telemetry data
- `RELAY_STATUS` - Get relay status information

### MoE Model (v1)

Mixture of Experts model implementation for advanced query processing and routing.

See `moemodel/v1/README.md` for details.

## Testing

Run tests with:

```bash
pytest tests/test_qbert_query_parser.py -v
```

## Integration

The Qbert Query Parser integrates with:
- `qube.orchestrator.v1` - Main orchestration capsule
- `qube.telemetry.v1` - Telemetry and monitoring
- Capsule registry and lineage tracking
- SSOT artifact resolution
