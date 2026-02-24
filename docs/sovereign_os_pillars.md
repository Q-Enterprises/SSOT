# Sovereign OS Pillars

This note captures the immediate prioritization for the Sovereign OS concept and the reasoning behind it.

## Current Highest-Weight Pillar

**Pillar 2: Design the Fallback Protocol** holds the most weight right now.

### Why this comes first

1. **It is the operational safety valve.** Without a deterministic fallback, Class 4 failures stall the system or tempt improvisation. The handoff protocol defines the safe boundary between model intent and human execution.
2. **It stabilizes every other layer.** Once the fallback protocol exists, the Capability Map schema and Unit-Test Contract can evolve without blocking delivery because the system always has a compliant escape hatch.
3. **It preserves auditability.** The fallback protocol is where Class 4 emissions become tangible artifacts, enabling traceable change management and later lattice registration.

## Secondary Priorities

1. **Formalize the Capability Map Schema.** This is the ledger backbone that enumerates known tools and their constraints, but it depends on the fallback protocol to handle unknowns.
2. **Define the Unit-Test Contract.** Essential for enforcing the Dojo gate, but it can be tightened iteratively once fallback emissions are reliably generated and captured.

## Immediate Next Step

Draft the fallback protocol contract with a minimal scaffold:

- **Input:** Class 4 failure context + desired action summary.
- **Output:** A signed scaffold artifact (script/YAML) + verification checklist.
- **Registration Hook:** A required step to bind new capabilities back into the lattice after human execution.
