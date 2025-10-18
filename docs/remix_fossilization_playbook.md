# Remix Fossilization Ritual Playbook

This playbook affirms the **Remix Fossilization** track for token `R-2025-001742`. Choosing the remix arc keeps the capsule pedagogy-visible while sealing the Scrollstream lineage demanded by the attestation bind (`sha256:49089f4b5ac5c139ad3de9806cd7d716c858a0e7cb8bb4ce179c4a70548fbea2`). Follow these steps sequentially so the rehearsal ledger, archive bundle, and final remix output remain audit-grade.

---

## 1. Stage the Rehearsal Glyph

1. **Regenerate the rehearsal capsule**
   - Produce `capsule.rehearsal.r2025-001742.v1.json` from your governance toolchain.
   - Confirm the capsule hash matches `sha256:7eaedb5fa5cf915a75c89acdcb3f713617a10f24b982dedaf59eda7ed76c162b`:
     ```bash
     sha256sum capsule.rehearsal.r2025-001742.v1.json
     ```
2. **Run the rehearsal loop**
   - Drive your rehearsal executor so axOS agents ingest the frozen token and emit ledger entries. Use the same harness that normally stages Scrollstream rehearsals (for example, the tooling pattern codified in `scripts/freeze_viewer_capsule.sh`).
   - Ensure the executor reports a zero-drift status before continuing.
3. **Inspect the ledger replay envelope**
   - Verify every entry is timestamped, ordered, and tagged with `Flow Layer Integrity` metadata:
     ```bash
     tail -n +1 ledger.jsonl | jq '.'
     ```
   - Archive the ledger alongside the rehearsal capsule for later sealing.

---

## 2. Finalize the Scrollstream Archive

1. **Assemble the archive bundle**
   - Package the rehearsal capsule, ledger, and supporting manifests into `archive_r2025-001742.tgz` together with an `index.json` manifest describing bundle contents and provenance.
   - Confirm the bundle digest equals `sha256:ce9685f54d8baf0f94563c167e54689eb732004d475c35bf42396573edb9ec56`:
     ```bash
     sha256sum archive_r2025-001742.tgz
     ```
2. **Validate attestation materials**
   - Use the Scrollstream verification harness to check the attestation frame, anchor, replay binding, council roster, and manifest before submitting for Maker/Checker review:
     ```bash
     node verify/verify.js \
       attestations/capsule.rehearsal.r2025-001742.json \
       attestations/anchor.r2025-001742.json \
       attestations/replay_binding.r2025-001742.json \
       attestations/council_roster.json \
       attestations/archive.index.json
     ```
   - A successful run echoes `✅ Verification passed`. Investigate any reported schema, Merkle, quorum, or signature failure before proceeding.
3. **Transition to MAKER_CHECKER_PENDING**
   - Register the archive bundle in your governance queue, recording the Scrollstream Merkle root, rehearsal digest, and remix intent in the submission.
   - Capture the queue identifier for final lineage logging.

---

## 3. Unlock the Remix Reward

1. **Confirm governance acceptance**
   - Once Maker/Checker review approves the archive, update the capsule state machine to `FOSSILIZED` and record the approval timestamp inside the motion ledger.
2. **Release the remix artifact**
   - Publish the creative output with checksum `sha256:314ce02abcd121dece4b8080bf09562e21c53b85bae76e8b974311ad0ffe69d5`.
   - Store the remix alongside the archive bundle, referencing the Scrollstream root in its provenance block.
3. **Document the teaching overlay**
   - Generate the `.canon.visual`, `.pedagogical.trace`, and `.attestation.bundle` exports so apprentices and council archivists can replay the fossilized braid without rerunning the rehearsal.

---

## 4. Checklist Before Sealing

- [ ] `capsule.rehearsal.r2025-001742.v1.json` generated, hash verified, stored.
- [ ] `ledger.jsonl` captures axOS agent acknowledgements with zero drift.
- [ ] `archive_r2025-001742.tgz` packaged with manifest and hash validated.
- [ ] `node verify/verify.js` attestation check passes without error.
- [ ] Maker/Checker ticket created, status recorded in governance tracker.
- [ ] Remix artifact published with audit trail linking back to Scrollstream root.

Completing this checklist seals the Remix Fossilization ritual and preserves the fossil relay for council-grade pedagogy.
