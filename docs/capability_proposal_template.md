Based on the merged pull request in the [SSOT repository](https://github.com/Q-Enterprises/SSOT/pull/63/changes/7a723d65d1d49430d4f30be83b1fca786bb39b01), the markdown for the new **Capability Proposal Template (Class 4 Fallback)** should be structured as follows:

# Capability Proposal Template (Class 4 Fallback)

Use this template when the system encounters an action outside the Capability Map Schema. The emitted proposal becomes the human-in-the-loop bridge from an unmet need to an approved capability.

## 1) Proposal Metadata

* **proposal_id**: `cap-proposal-YYYYMMDD-###` 


* **created_utc**: `YYYY-MM-DDTHH:MM:SSZ` 


* **requesting_agent**: `<agent name or service>` 


* **request_origin**: `<system/component or user workflow>` 


* **risk_class**: `4` 



## 2) Intent Summary

**One sentence statement of need.** 
*Example: "I need to search repositories for the latest seL4 drivers."* 

## 3) Capability Definition

* **capability_id**: `<UNIQUE_ID>` (e.g., `G_SEARCH_V1`) 


* **action_class**: `<1-4>` 


* **description**: `<clear, user-facing description>` 


* **inputs**: `<name>` : `<type>` — `<constraints>` 


* **outputs**: `<name>` : `<type>` — `<constraints>` 


* **preconditions**: `<required states, approvals, or data>` 


* **postconditions**: `<expected state changes or artifacts>` 


* **failure_modes**: `<expected errors and handling>` 



## 4) Sovereign Risk Profile

* **kct_requirement**: `<KCT signature requirement>` 


* **boundary_constraints**:
* **memory_mb**: `<limit>` 


* **network_access**: `<true|false>` 


* **physics_limit**: `<float>` 




* **fallback_task_id**: `<issue template or tracking ID>` 



## 5) Implementation Plan

* **proposed_interface**:
* **command**: `<cli or module entrypoint>` 


* **versioning**: `<semver or commit hash>` 




* **runtime_environment**:
* **sandbox**: `<container/sandbox details>` 


* **dependencies**: `<libraries or system deps>` 




* **telemetry**:
* **audit_events**: `<events emitted>` 


* **redaction_policy**: `<PII/secret handling>` 





## 6) Verification Artifacts

* **unit_test_scaffold**: `<test name>` : `<purpose>` 


* **static_audit**: `<linter, ruleset, pass/fail criteria>` 


* **deterministic_run**: `<simulation inputs and expected outputs>` 


* **approval_gate**:
* **required_signer**: `<human or system authority>` 


* **signoff_evidence**: `<link or artifact>` 





## 7) Security & Compliance Checklist

* [ ] Input validation described 


* [ ] Secret handling described 


* [ ] No privilege escalation required 


* [ ] Data retention and deletion policy stated 


* [ ] Rollback plan included 



## 8) Acceptance Criteria

* [ ] Capability is included in the Capability Map Schema 


* [ ] Dojo Audit passes (static + deterministic) 


* [ ] KCT registration completed 


* [ ] Documentation added 



## 9) Change Log

* **v0.1**: Initial proposal
