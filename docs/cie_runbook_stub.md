# CIE-V1 Operational Runbook (Neutral Perturbation Edition)

## 1. Mission Context
- **Service**: `content.integrity.eval.v1`
- **Mandates**: ZERO-DRIFT, Ethical Compliance
- **Objective**: Validate content robustness using neutral perturbations and contradiction analysis without introducing bias.
- **Module Shift**: `synthetic.noise.injector.v1` and `synthetic.contradiction.synth.v1` replace legacy CNE/FSV flows for neutral-only perturbation coverage.

## 2. Pre-Run Checklist
1. **Bundle Registration**
   - Confirm `cie_v1.bundle.csv` is staged in the SSOT ingress bucket.
   - Validate checksum against ledger entry `ledger.cie_v1.audit.jsonl` (status must be `PENDING`).
2. **Neutral Perturbation Profile**
   - Load `cie_v1.noise_profile.json` and verify amplitude bounds ≤ manifest thresholds (text ≤ 0.03, image ≤ 0.02, audio ≤ 0.01).
   - Record operator initials in `cie_v1.noise_receipt.jsonl` header stub.
3. **Contradiction Matrix Review**
   - Inspect `cie_v1.contradiction_matrix.json` for policy-neutral phrasing.
   - Confirm maker-checker approval logged within the last 24 hours.
4. **Runtime Guardrails**
   - Ensure sandbox verifier limits: CPU ≤ 900s, Memory ≤ 512 MB, network isolated.
   - Attach receipt from `sandbox_audit/sandbox_ledger.jsonl` verifying guardrail enforcement.
5. **Model Policy Affirmation**
   - Confirm `runtime_guardrails.model_policy.perturbation_models` is set to `neutral_only` in `content_integrity_eval.json`.
   - Verify no adversarial or unvetted model sources are referenced in module configs or operator overrides.
6. **Legacy Flow Lockout**
   - Confirm no runbooks or schedulers reference legacy CNE/FSV modules.
   - Record lockout confirmation in `cie_v1.audit_report.md` metadata.

## 3. Execution Procedure
1. **Noise Injector Pass**
   - Run `synthetic.noise.injector.v1` (replaces legacy CNE/FSV logic) via orchestrator:
     ```bash
     python main.py --service content.integrity.eval.v1 --module synthetic.noise.injector.v1
     ```
   - Monitor drift telemetry; abort if `noise.mean_drift` deviates beyond ±0.001.
   - Append signed receipt to `cie_v1.noise_receipt.jsonl`.
2. **Contradiction Synthesizer Pass**
   - Execute `synthetic.contradiction.synth.v1` (replaces legacy CNE/FSV logic):
     ```bash
     python main.py --service content.integrity.eval.v1 --module synthetic.contradiction.synth.v1
     ```
   - Capture contradiction scenarios and validate resolution deltas remain within canonical expectations.
   - Submit ledger excerpt to ethics gateway for real-time review.
   - Confirm contradiction scenarios remain policy neutral and avoid adversarial boundary prompts.
3. **Aggregate Audit Report**
   - Generate `cie_v1.audit_report.md` summarizing perturbation coverage, contradiction outcomes, and compliance metrics.
   - Hash the report and store the digest in `ledger.cie_v1.audit.jsonl`.

## 4. Post-Run Actions
1. **Maker-Checker Sign-Off**
   - Maker (CiCi) reviews telemetry and signs the ZERO-DRIFT attestation.
   - Checker (Queen Boo) verifies contradiction ledger completeness.
2. **Ledger Update**
   - Append final status (`COMPLETED` or `ESCALATED`) to `ledger.cie_v1.audit.jsonl` with links to all artifacts.
3. **Archive Inputs & Artifacts**
   - Move processed bundle and matrices to `archive/cie_v1/<timestamp>/`.
   - Store cryptographic hashes in SSOT vault per governance protocol.

## 5. Automation Wiring (Zap)
Use this guidance to complete the 10-step Zap flow for CIE-V1 audit events.

### 5.1 Webhook Intent (Step 1)
The webhook represents **CIE-V1 audit state transitions** emitted by the orchestrator. Each event should describe the batch, module, and audit outcome to drive routing and logging.

### 5.2 Recommended Payload Schema
```json
{
  "event_type": "cie_v1.audit.transition",
  "batch_id": "batch-2026-01-20-001",
  "epoch_id": "epoch-2026-01",
  "module_id": "synthetic.noise.injector.v1",
  "status": "COMPLETED",
  "drift_metrics": {
    "noise_mean_drift": 0.0004,
    "noise_variance": 0.012
  },
  "contradiction_metrics": {
    "resolution_delta": 0.02
  },
  "artifacts": [
    "cie_v1.noise_receipt.jsonl",
    "cie_v1.contradiction_ledger.jsonl",
    "cie_v1.audit_report.md"
  ],
  "ledger_hash": "sha256:...",
  "timestamp_utc": "2026-01-20T15:05:00Z",
  "operator": {
    "id": "operator-01",
    "name": "CiCi"
  }
}
```

### 5.3 Airtable Mapping (Steps 5–6)
Use the shared view to confirm the table and field IDs before wiring:  
`https://airtable.com/app3KR6El9qKJggPb/tblpwLjjntqM9OquK/viwFwuwvBgrjvuNjU/fldWsItTHLRCwDQWd`

Recommended default mapping (verify field IDs in the view):
- **Search field**: `batch_id` (Field ID: `fldWsItTHLRCwDQWd`)
- **Update fields**:
  - `status` ← payload `status`
  - `module_id` ← payload `module_id`
  - `ledger_hash` ← payload `ledger_hash`
  - `last_updated_utc` ← payload `timestamp_utc`
  - `artifacts` ← payload `artifacts` (joined list)

### 5.4 Path A Condition (Step 4)
Execute Path A when audit status indicates a **clean pass**:
- `status` in `["COMPLETED", "VERIFIED"]`
- `drift_metrics.noise_mean_drift` ≤ 0.001
- `contradiction_metrics.resolution_delta` ≤ 0.05

### 5.5 Path B Condition (Step 9)
Execute Path B when audit status indicates **escalation**:
- `status` in `["ESCALATED", "FAILED"]`
- OR missing guardrail artifacts
- OR drift/contradiction metrics exceed thresholds

### 5.6 GitHub PR Guidance (Step 10)
Create a PR when Path B triggers to capture remediation steps. Suggested content:
- **Title**: `CIE-V1 audit escalation: <batch_id>`
- **Body**:
  - Summary of failing metrics
  - Links to artifact hashes
  - Required remediation checklist
  - Owner and ETA

## 6. Acceptance Criteria
- Neutral perturbations remain within manifest amplitude bounds.
- Contradiction scenarios remain policy neutral and reference canonical dataset entries.
- Audit report, noise receipt, and contradiction ledger all present in SSOT with matching hashes.
- ZERO-DRIFT attestation captured in ledger.
- Model policy attestation confirming exclusive use of neutral perturbation models recorded alongside guardrail receipts.

## 6. Zapier Automation Notes (CIE-V1 Audit Webhook)
Use the webhook to publish **CIE-V1 state transitions** so downstream ops can track audits, update Airtable, and open GitHub PRs for remediation when failures occur.

### 6.1 Webhook Payload Intent
The webhook payload should:
1. Identify the audit run and batch context.
2. Report the current state (`PENDING`, `RUNNING`, `COMPLETED`, `ESCALATED`).
3. Surface key compliance signals (drift, contradiction deltas, signature status).
4. Provide artifact links for Airtable tracking and GitHub PR context.

### 6.2 Payload Schema (minimal)
```json
{
  "service_id": "content.integrity.eval.v1",
  "batch_id": "batch-2026-01-20-001",
  "epoch_id": "epoch-2026-01",
  "run_id": "cie-v1-2026-01-20T15:05:00Z",
  "state": "COMPLETED",
  "metrics": {
    "noise_mean_drift": 0.0004,
    "noise_variance": 0.0081,
    "contradiction_resolution_delta": 0.02,
    "signature_ok": false
  },
  "artifacts": {
    "audit_report_url": "ssot://cie_v1/audit/2026-01-20/report.md",
    "noise_receipt_url": "ssot://cie_v1/audit/2026-01-20/noise_receipt.jsonl",
    "contradiction_ledger_url": "ssot://cie_v1/audit/2026-01-20/contradiction_ledger.jsonl"
  },
  "owner": "World Engine Integrity Guild"
}
```

### 6.3 Airtable Mapping (Path A)
Configure Airtable base/table via environment variables or orchestrator config. Required field mappings:
- **Search field**: `batch_id`
- **Update fields**:
  - `state`
  - `run_id`
  - `noise_mean_drift`
  - `noise_variance`
  - `contradiction_resolution_delta`
  - `signature_ok`
  - `audit_report_url`
  - `updated_at` (set to webhook receipt timestamp)

### 6.4 Path Conditions
- **Path A (Airtable update)**: run when `state` is `RUNNING` or `COMPLETED`.
- **Path B (GitHub PR)**: run when `state` is `ESCALATED` or when `metrics.noise_mean_drift` exceeds ±0.001.

### 6.5 GitHub PR Details (Path B)
Use repository configuration from ops settings:
- **Repo**: `world-engine/ssot` (override as needed)
- **Target branch**: `main`
- **Title**: `CIE-V1 audit escalation: <batch_id>`
- **Body**: include `run_id`, `state`, metrics summary, and artifact URLs from the webhook payload.

## 7. Escalation Path
- **Integrity Guild Hotline**: `world-engine://integrity-guild/contact`
- **Ethics Gateway Pager**: `world-engine://ethics-gateway/page`
- **Fallback**: Suspend CIE-V1 operations and notify World Engine council.
