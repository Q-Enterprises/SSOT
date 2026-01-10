# Photo → Prompt → Print → P3L Pipeline

This document captures the staged workflow for transforming a reference photo into a proof-of-learning record within the SSOT ledger.

## 1. Photo → Prompt

* **Input**: Reference photo of a real object or scene.
* **Goal**: Extract a structured description to drive asset generation.
* **Method**:
  * Apply computer-vision tagging to detect objects, materials, colors, and proportions.
  * Encode the results using the minimal prompt schema:

    ```json
    {
      "subject": "GT3 race car",
      "scale": "1:7",
      "materials": ["PLA", "resin"],
      "style": "studio model"
    }
    ```
  * Optionally enrich the prompt with contextual language such as a pose, display base, or environmental cues.

## 2. Prompt → Print

* **Input**: Enriched prompt data.
* **Goal**: Generate a printable 3D asset.
* **Steps**:
  1. Convert the prompt into parametric CAD via an OpenSCAD or Fusion 360 template.
  2. Export an STL file and validate watertightness.
  3. Slice the STL at 0.15 mm layer height for a 0.4 mm nozzle.
  4. Print a tolerance test module.
  5. Assemble the physical sandbox model at the target scale (1:7).

## 3. Print → P3L

* **Goal**: Translate fabrication outputs into a proof-of-learning sequence.
* **Mapping**:
  * **Proof** – Digital record including the photo, prompt, and print G-code with SHA-256 digests.
  * **Flow** – Execution metadata such as printer ID, filament batch, runtime, and energy usage.
  * **Execution** – Physical validation (sensor or photo) anchored into the SSOT ledger.

## 4. P3L Protocol Record Template

Use the following JSON structure to record sandbox results for the GT3 race car subject:

```json
{
  "stage": "sandbox_model_v1",
  "subject": "GT3 race car",
  "inputs": {
    "photo_hash": "",
    "prompt_hash": "",
    "stl_hash": ""
  },
  "proof": "sha256:",
  "flow": {
    "printer": "PrusaMK4",
    "duration_min": 0,
    "material_g": 0
  },
  "execution": {
    "result": "PENDING",
    "timestamp_utc": ""
  }
}
```

Populate the placeholder fields with actual values once each stage is completed. Update the `result` and `timestamp_utc` when the physical validation succeeds and the record is ready for ledger anchoring.
