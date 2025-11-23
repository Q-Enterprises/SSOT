# capsule.rehearsal.scrollstream.v1

The **scrollstream rehearsal loop capsule** coordinates the audit trio (Celine → Luma → Dot) and exposes a simple front-end harness so teams can verify the ledger flow before sealing.

## Capsule payload

```json
{
  "capsule_id": "capsule.rehearsal.scrollstream.v1",
  "type": "RehearsalLoop",
  "version": "1.0.0",
  "issued_at": "2025-10-03T00:00:00Z",
  "cycle": [
    {
      "event": "audit.summary",
      "agent": "Celine/Architect",
      "output": "System Lock achieved. P3L layers aligned. Sovereign fidelity guaranteed."
    },
    {
      "event": "audit.proof",
      "agent": "Luma/Sentinel",
      "output": "Merkle Root verified. LegacyBundle audit confirms immutability and unbroken lineage."
    },
    {
      "event": "audit.execution",
      "agent": "Dot/Guardian",
      "output": "Zero-Drift confirmed. Git LFS assets stable. Ready to receive first input hook."
    }
  ],
  "attestation": {
    "status": "STAGED",
    "sealed_at": null,
    "content_hash": null
  },
  "governance": {
    "maker": "Earl Q Han",
    "checker": "Council",
    "quorum_required": 2
  }
}
```

## HUD rehearsal hook

Drop the following helper into a dashboard panel with an `#image-container` element to run the rehearsal loop and record entries into a local scrollstream ledger buffer:

```html
<button onclick="runRehearsalLoop()" class="mt-6 bg-indigo-700 px-6 py-3 rounded-md text-white font-bold hover:bg-indigo-800">
  🔁 Run Rehearsal Loop
</button>
```

```js
async function runRehearsalLoop() {
  const capsuleId = "capsule.rehearsal.scrollstream.v1";
  const cycle = [
    { event: "audit.summary", agent: "Celine/Architect", output: "System Lock achieved. P3L layers aligned. Sovereign fidelity guaranteed." },
    { event: "audit.proof", agent: "Luma/Sentinel", output: "Merkle Root verified. LegacyBundle audit confirms immutability and unbroken lineage." },
    { event: "audit.execution", agent: "Dot/Guardian", output: "Zero-Drift confirmed. Git LFS assets stable. Ready to receive first input hook." }
  ];

  for (const step of cycle) {
    const entry = {
      t: new Date().toISOString(),
      event: step.event,
      capsule: capsuleId,
      details: { agent: step.agent, output: step.output }
    };

    const ledger = JSON.parse(localStorage.getItem("scrollstream_ledger") || "[]");
    ledger.push(entry);
    localStorage.setItem("scrollstream_ledger", JSON.stringify(ledger));

    const shimmer = document.createElement("div");
    shimmer.textContent = `⚡ ${step.agent} → ${step.event}`;
    shimmer.className = "animate-pulse text-indigo-400 mt-2";
    document.querySelector("#image-container").appendChild(shimmer);

    await new Promise(resolve => setTimeout(resolve, 1200));
    shimmer.classList.remove("animate-pulse");
    shimmer.classList.add("text-green-400");
  }

  alert("✅ Rehearsal loop complete. Ledger updated.");
}
```

The helper stores each audit handoff in `scrollstream_ledger` (local storage) so teams can replay the timestamps or export the loop as NDJSON during smoke tests.
