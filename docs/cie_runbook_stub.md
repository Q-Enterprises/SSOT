# CIE-V1 Operational Runbook (Neutral Perturbation Edition)

## 1. Mission Context
- **Service**: `content.integrity.eval.v1`
- **Mandates**: ZERO-DRIFT, Ethical Compliance
- **Objective**: Validate content robustness using neutral perturbations and contradiction analysis without introducing bias.

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
6. **Legacy Component Lockout**
   - Confirm no orchestrator configs reference deprecated `CNE` or `FSV` components.
   - Validate `legacy_deprecations` in `content_integrity_eval.json` are marked `retired`.

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

## 5. Acceptance Criteria
- Neutral perturbations remain within manifest amplitude bounds.
- Contradiction scenarios remain policy neutral and reference canonical dataset entries.
- Audit report, noise receipt, and contradiction ledger all present in SSOT with matching hashes.
- ZERO-DRIFT attestation captured in ledger.
- Model policy attestation confirming exclusive use of neutral perturbation models recorded alongside guardrail receipts.

## 6. Escalation Path
- **Integrity Guild Hotline**: `world-engine://integrity-guild/contact`
- **Ethics Gateway Pager**: `world-engine://ethics-gateway/page`
- **Fallback**: Suspend CIE-V1 operations and notify World Engine council.
