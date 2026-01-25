#!/usr/bin/env node
/**
 * Validate manifest.json against its JSON schema
 */

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');

function main() {
  const schemaPath = path.join(process.cwd(), 'schemas/manifest.schema.json');
  const manifestPath = path.join(process.cwd(), 'manifest.json');
  
  // Check files exist
  if (!fs.existsSync(schemaPath)) {
    console.error(`Error: Schema not found at ${schemaPath}`);
    process.exit(1);
  }
  
  if (!fs.existsSync(manifestPath)) {
    console.error(`Error: Manifest not found at ${manifestPath}`);
    process.exit(1);
  }
  
  // Load files
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  
  // Validate
  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema);
  const valid = validate(manifest);
  
  if (!valid) {
    console.error('Manifest validation failed:');
    console.error(JSON.stringify(validate.errors, null, 2));
    process.exit(1);
  }
  
  console.log('manifest.json valid');
}

main();
