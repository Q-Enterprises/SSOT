use std::fs;

use serde_yaml;

use crate::corridor::types::{EntryType, FrameCapture, WindchillLedger};

/// Seal a capture frame into the Windchill ledger, enforcing scene identity.
pub fn seal_frame_into_ledger(cap: &FrameCapture, ledger: &mut WindchillLedger) {
    // GUARD: Ensure the identity surface is defined before sealing.
    assert!(
        !cap.scene_id.is_empty(),
        "Identity Breach: Attempted to seal frame with empty Scene ID."
    );

    // Existing seal logic should follow here.
    ledger.seal(cap);
}

/// Export ledger entries into an Obsidian-compatible markdown vault.
pub fn export_to_vault(ledger: &WindchillLedger) -> std::io::Result<()> {
    let vault_path = "vault/audits/burn_in_2026/";
    fs::create_dir_all(vault_path)?;

    for entry in &ledger.entries {
        let yaml = serde_yaml::to_string(&entry).unwrap();
        let content = format!(
            "---\n{}---\n# Audit Entry: Sequence {}\n\n**Status:** {}\n**Timestamp:** {:.4}s\n\n> [!ABSTRACT] Merkle Proof\n> Root: `0x{}`",
            yaml,
            entry.sequence_id,
            match entry.entry_type {
                EntryType::Standard => "✅ Nominal",
                EntryType::Refusal => "🚫 Sentinel Veto",
            },
            entry.timestamp,
            hex::encode(entry.merkle_root)
        );

        let file_name = format!("{}seq_{:06}.md", vault_path, entry.sequence_id);
        fs::write(file_name, content)?;
    }

    Ok(())
}
