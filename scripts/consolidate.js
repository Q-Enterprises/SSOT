#!/usr/bin/env node
/**
 * Consolidate manifest according to RFC 8785 (JSON Canonicalization Scheme)
 * Ensures deterministic JSON serialization with lexicographical key ordering
 */

const fs = require('fs');
const path = require('path');

// RFC 8785 canonical JSON serialization
function canonicalize(obj) {
  if (obj === null || typeof obj !== 'object' || obj.toJSON != null) {
    return JSON.stringify(obj);
  }
  
  if (Array.isArray(obj)) {
    return '[' + obj.map(item => canonicalize(item)).join(',') + ']';
  }
  
  // Sort keys lexicographically
  const keys = Object.keys(obj).sort();
  const pairs = keys.map(key => {
    const value = obj[key];
    return JSON.stringify(key) + ':' + canonicalize(value);
  });
  
  return '{' + pairs.join(',') + '}';
}

function main() {
  const manifestPath = path.join(process.cwd(), 'manifest.json');
  const outputDir = path.join(process.cwd(), 'dist');
  const outputPath = path.join(outputDir, 'consolidated-manifest.json');
  
  // Read source manifest
  if (!fs.existsSync(manifestPath)) {
    console.error('Error: manifest.json not found');
    process.exit(1);
  }
  
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Consolidate with RFC 8785 canonicalization
  const consolidated = {
    ...manifest,
    consolidated_at: new Date().toISOString(),
    canonical_form: true,
    rfc: 8785
  };
  
  // Write canonical JSON
  const canonicalJson = canonicalize(consolidated);
  fs.writeFileSync(outputPath, canonicalJson, 'utf8');
  
  console.log(`Consolidated manifest written to ${outputPath}`);
  console.log(`Size: ${canonicalJson.length} bytes`);
}

main();
