.PHONY: qube-stage qube-seal qube-export echo-flare

QUBE_DRAFT ?= capsules/capsule.patentDraft.qube.v1.json
QUBE_EXPORT_REQ ?= capsules/capsule.export.qubePatent.v1.request.json
QUBE_ECHO_FLARE ?= capsules/capsule.echoFlare.qube.v1.json

qube-stage: freeze post verify
	@echo "📜 Staging QUBE draft capsule → $(QUBE_DRAFT)"
	@jq -n --arg ts "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" '{
	  capsule_id: "capsule.patentDraft.qube.v1",
	  qube: {
	    p3l_ref: "urn:p3l:phase1:qLock:LiD:QBits",
	    sr_gate: "v1",
	    moe_topology: {
	      experts: "N",
	      router: "SR",
	      ab_determinism_seed: "phase1-seed"
	    },
	    malintent: "BLQB9X/MIT.01",
	    artifact: {
	      type: "R0P3",
	      format: "iRQLxTR33",
	      packaging_map: [
	        "P3L",
	        "qLock/LiD",
	        "QBits",
	        "SR Gate",
	        "MoE",
	        "BLQB9X",
	        "R0P3"
	      ]
	    }
	  },
	  lineage: {
	    qonledge_ref: "urn:qon:phase1:pending",
	    scrollstream: true,
	    dual_run: {
	      mode: "A/B",
	      seed: "phase1-seed",
	      delta_emit: true
	    }
	  },
	  integrity: {
	    sha256_p3l: "sha256:TODO",
	    merkle_root: "TODO",
	    attestation_quorum: "2-of-3"
	  },
	  governance: {
	    gates: [
	      "G01-ticket-hash",
	      "G02-fitment",
	      "G03-artifact-hashes",
	      "G04-expected-verify",
	      "SEAL"
	    ]
	  },
	  meta: {
	    epoch: "phase.1.x",
	    issuer: "Council",
	    policy: "P3L.vX",
	    issued_at: $ts,
	    notes: "Generated for council staging; fill hashes before seal."
	  }
	}' > $(QUBE_DRAFT)

qube-seal: seal
	@echo "🔏 QUBE draft sealed; see capsule.federation.receipt.v1.json"

qube-export: qube-seal
	@echo "🚚 Emitting DAO export request → $(QUBE_EXPORT_REQ)"
	@jq -n '{
	  deploymentId: "phase.1.qube",
	  capsuleId: "capsule.patentDraft.qube.v1",
	  replayPacketId: "replay:cdpy71:pathA",
	  archiveRef: "s3://qube/bundles/qube.v1.tar.zst",
	  dao: {
	    protocol: "capsule.export.qubePatent.v1",
	    format: "artifactBundle",
	    integrity: {
	      sha256_verification: true,
	      merkle_proof: true,
	      attestation_quorum: "2-of-3"
	    },
	    ledger_binding: {
	      append_target: "ledger/federation.jsonl",
	      proof_binding: "sha256:REQUEST"
	    }
	  },
	  meta: {
	    issued_at: "ISO-UTC",
	    issuer: "Council",
	    epoch: "phase.1.x",
	    trigger_event: "SEAL",
	    export_policy_ref: "policy:QUBE"
	  }
	}' > $(QUBE_EXPORT_REQ)

echo-flare:
	@echo "📡 Emitting echoFlare resonance map → $(QUBE_ECHO_FLARE)"
	@jq -n '{capsule_id:"capsule.echoFlare.qube.v1", contributors:[]}' > $(QUBE_ECHO_FLARE)
