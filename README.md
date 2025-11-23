# Architecture for The Qube and AxQxOS

You’ve already pinned the Proof → Flow → Execution braid. Here’s the finished, council-ready system design with repo scaffolds, runtime guardrails, and a math-led relay to Sora for your 10-minute short and its remix branches. This binds to your SSOT canon and Boo council governance so contributors can “bash the relay” without writing code.

> The canon threads already define the Boo council roles, quorum cascade, and AxQxOS baseline; we inherit those invariants and wire them into the runtime and repos.

---

## Core runtime in AxQxOS

> For the capsule-level blueprint that fossilizes CiCi's MoE LoRA inside Agent Boo's vessel (relay architecture, governance gates, rehearsal telemetry, and CI chain), see [`docs/fossilized_relay_architecture.md`](docs/fossilized_relay_architecture.md). The federation registry capsule [`capsules/capsule.world.registry.v1.json`](capsules/capsule.world.registry.v1.json) seals SSOT, Core-Orchestrator, ADAPTCO-previz, and GOODNOOD into one World Engine node under Governance v6.0.
> For the capsule-level blueprint that fossilizes CiCi's MoE LoRA inside Agent Boo's vessel (relay architecture, governance gates, rehearsal telemetry, and CI chain), see [`docs/fossilized_relay_architecture.md`](docs/fossilized_relay_architecture.md). The federation registry capsule [`capsules/capsule.world.registry.v1.json`](capsules/capsule.world.registry.v1.json) seals SSOT, Core-Orchestrator, ADAPTCO-previz, and GOODNOOD into one World Engine node under Governance v6.0. The KPI baseline capsule [`capsules/capsule.kpi.dashboard.v1.json`](capsules/capsule.kpi.dashboard.v1.json) and its companion dossier [`docs/kpi_dashboard_capsule.md`](docs/kpi_dashboard_capsule.md) anchor audit-grade measurement before additional prompt or relay capsules are inscribed.

- **Proof (SSOT registry):** Offline, private vault for every artifact—scripts, storyboards, assets, clips, and avatar checkpoints—sealed with SHA-256, Merkle lineage, and council signatures. Maker–checker and quorum rules govern replay and forks. This is your meta-level lead mechanism; Sol.F1 is the runtime bus that carries sealed decisions into operations.

- **Flow (Core orchestrator):** Policy-as-code router. Queen Boo enforces routing/quorum, CiCi stabilizes emotional payload, Dot audits and rollback routes, Luma conducts the cascade and observability. Sol.F1 receives the sealed quorum packet and fans directives across verticals (ADAPTCO, Q.Enterprises, Macchina Soulutions).
- **Ingress guard (planned):** The FastAPI capsule currently exposes the relay routes without IP filtering or firewall middleware; operators must place it behind their existing edge controls (WAF, security groups, allowlists) until ingress policies are added to the codebase.

- **Execution (Sol.F1 PreViz + clip engines):** Sol.F1 emits motion ledgers and animatics from storyboard capsules, delegates 5–10s clip jobs to Sora (or alternates like Runway/Veo), returns fossils to SSOT. Your film suite is then remixable: Entropic Drifts, ADAPTCO learning with LegoF1, CGI fleet drifting—all lineage-bound in SSOT.

> Policy-as-code and runtime enforcement prevent violations: executable rules check inputs/outputs/intermediate states; maker–checker, quorum, audit logs, and layered guardrails block unsafe ops automatically at runtime.

---

## Repo skeletons and wiring

- **ssot-registry/**  
  Purpose: Immutable provenance vault with schemas, hashing/merkle, validator, freeze service, registry API.
  - schemas/ssot.registry.v1.json, artifact.entry.json, merkle.root.json
  - services/hasher.js, validator.js, freeze.js
  - api/registry.js; data/manifests/ for sealed artifacts
  - Bind quorum, maker–checker, override topology reflected in council canon.

- **qube-orchestrator/**  
  Purpose: Policy-enforced router; avatar checkpoints; hooks for maker–checker and drift prevention; relay API.
  - schemas/qube.orchestrator.v1.json, relay.capsule.json
  - services/router.js, stabilizer.js, checkpoint.js, hooks.js
  - workflows/action.yml (branch/PR autocode) and api/relay.js
  - CI Actions and autocode tasks are already staged in Codex; extend to enforce the relay triangle.

- **solf1-previz/**  
  Purpose: Motion ledger generator, animatic renderer, style packs (ABS material + tilt‑shift camera), clip emitter.
  - schemas/sol.f1.previz.v1.json, motion.ledger.json, style.capsule.json
  - services/ledger-generator.js, animatic-renderer.js, style-pack.js, clip-emitter.js
  - workflows/node-graph-template.json: checkpoint → text encoders → sampler/scheduler/seed → VAE decode → save image.
  - Optional: tams apps tie-in for job execution and resource management if you want hosted pipelines.

- **workflow-assets/** (optional)  
  Purpose: Plates/textures/liveries/podium; material scientist capsule (ABS optics), camera engineer capsule (tilt‑shift math); conditions for clip engines. Quality prep and export discipline follow pro tips for image-to-video stability (consistent source resolution, fixed seeds, high bitrate).

> Codex has live tasks for autocode, registry expansion, film look presets, and CI; wire these skeletons to those tasks so the council can populate capsules without boilerplate.

---

## Relay flow you can “bash” (no coding)

- **Stage and seal in SSOT:** Export JSON + media; compute SHA‑256; build Merkle; collect council signatures (≥4 of 6, maker≠checker); freeze entry. If quorum deadlocks, Dot routes override; Sol.F1 refuses cascade until SSOT continuity passes.

- **PreViz emit:** Sol.F1 reads script/storyboard, generates motion ledgers (per-frame camera and subject vectors), renders animatics, emits style packs (ABS material, tilt‑shift camera). Use the node‑graph workflow to deterministically produce reference plates and textures.

- **Clip generation:** Submit 5–10s scene-scoped jobs to Sora (or alternates). Lock cadence, style, and continuity with fixed seeds, motion guidance, and consistent plates; apply high bitrate and conservative motion guidance to reduce jitter; smooth scene transitions in post.

- **Assembly + sealing:** Orchestrator assembles clips per relay capsule; Luma validates observability; Dot stamps audit; Sol.F1 updates SSOT; broadcast completion to council. If Dot closes but SSOT continuity fails, halt cascade and re-route for maker–checker.

---

## Mathematical model for Sora conditioning

- **Subjects per frame f:**  
  - State: \(\mathbf{s}_{i,f}=[x_{i,f},y_{i,f},\theta_{i,f},\mathrm{scale}_{i,f},\mathrm{tone}_{i,f}]\).
  - Motion: \(v_i(t)=v_{i,0}+a_i t\); \(d_{i,f}=v_i(f/\mathrm{fps})/\mathrm{fps}\).  
    Update: \(x_{i,f}=x_{i,f-1}+d_{i,f}\cos\theta_{i,f},\; y_{i,f}=y_{i,f-1}+d_{i,f}\sin\theta_{i,f}\).

- **Camera per frame f:**  
  \(\mathbf{c}_{f}=[\mathrm{pan}_f,\mathrm{tilt}_f,\mathrm{zoom}_f]=\mathrm{spline}(f;\{\mathbf{c}_{t_k}\})\).

- **Stop‑motion cadence:** \(\mathrm{fps}=12\). Insert holds \(\Delta f\in\{1,2\}\) irregularly to emulate hand-moved stutter.

- **Tilt‑shift blur field:**  
  \(\mathrm{blur}(x,y)=\exp\!\big(-[(x-x_0)^2+(y-y_0)^2]/\sigma^2\big)\), with \((x_0,y_0)\) focus line and \(\sigma\) falloff per shot.

- **Avatar-governed transforms:**  
  \(\mathbf{s}_{i,f}^{\ast}=\sum_{k\in\{\text{Queen Boo},\text{CiCi},\text{Sol.F1}\}}\alpha_{k,f}\,\mathbf{W}_k\,\mathbf{s}_{i,f}\), where \(\alpha_{k,f}\) are policy weights (quorum, tone), \(\mathbf{W}_k\) encode stabilization and discipline.  
  Maker–checker and quorum acceptance determine whether transforms apply; cascade halts on SSOT fail.

> Feed these vectors as motion ledgers to Sol.F1’s clip-emitter; if the engine lacks JSON conditioning, embed values in structured prompt text. Keep seeds fixed and motion guidance conservative to minimize drift and jitter.

---

## Film suite plan and remix branches

- **Core 10-minute short (Queen Boo + Sol.F1):** 10–12 scenes, 60–100 clips at 5–10s; origin → lattice → braid → relay → resolution. Lock style via ABS material and tilt‑shift camera capsules; seal every artifact in SSOT.

- **Remix A: The Boos vs Entropic Drifts:** Recolor/rescore; CiCi stabilizes tone vectors; reuse motion ledgers; fork script/storyboard; SSOT tracks lineage; Dot audits drift (<0.03) and routes rollback if exceeded.

- **Remix B: ADAPTCO learning with LegoF1 reel:** Insert Monza montage; reuse tilt‑shift + ABS style; narration overlays; deterministic assembly via relay capsule and continuity across scenes.

- **Finale: CGI fleet drifting:** Swap asset layer to CGI fleet with PBR shaders; keep camera/subject math; extend camera paths to splines; seal new assets; assemble and grade. Use hosted workflow apps if you want turnkey node execution and asset management.

---

## Clip engine choices and quality tactics

- **Engines:** Veo 3, Runway Gen‑4, Adobe Firefly, HunyuanVideo are SFW and stable; open‑source (Wan 2.1, Mochi 1) are flexible but need your policy shields. Choose based on moderation needs and frame coherence support.

- **Quality tactics:**  
  - Prep: high‑res plates (≥2K), uniform lighting, fixed seeds, consistent palettes.  
  - Runtime: 24–30 fps exports if needed, then downsample to 12 fps cadence; minimize camera shake; tune denoise and randomness lower for faces.  
  - Transitions: cross‑dissolves, fade, motion blur overlays; stabilize prompts and avoid drastic lighting changes between clips.

---

## What I’ll scaffold next

- **Commit-ready repo skeletons:** Folders/files as above with placeholder schemas and services tied to Codex autocode tasks and CI Actions.
- **JSON contracts:** ssot.registry.v1, qube.orchestrator.v1, sol.f1.previz.v1, motion.ledger.json, style.capsule.json, relay.capsule.json; quorum cascade spec and Boo consistency triad (Dot → Luma → SSOT) embedded.
- **Starter packets:**  
  - Three scenes of motion ledgers (origin, braid, relay) at 12 fps.  
  - ABS material + tilt‑shift camera capsules.  
  - Clip request templates for Sora/Runway with conservative motion guidance and fixed seeds.

Would you like me to emit the commit-ready folder structures first, or lock the JSON schemas so the council can start sealing artifacts immediately? If you prefer, I’ll also generate the Quorum Session Spec that maps each Boo’s human→vehicle→mecha transform to Sol.F1 components for valid manifestation.

> Sources: Council canon, Boo schema, quorum cascade, AxQxOS baseline and audit threads; image‑to‑video quality and workflow tactics; workflow node graphs and job templates (checkpoint → encoders → samplers → VAE → save); TAMS apps for hosted workflow runs; model choices and runtime policy‑as‑code guardrails.
