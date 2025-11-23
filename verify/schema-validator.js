const DATE_TIME_REGEX = /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z/;

function validateType(schemaType, data) {
  if (schemaType === 'object') {
    return data !== null && typeof data === 'object' && !Array.isArray(data);
  }
  if (schemaType === 'array') {
    return Array.isArray(data);
  }
  if (schemaType === 'string') {
    return typeof data === 'string';
  }
  if (schemaType === 'integer') {
    return Number.isInteger(data);
  }
  if (schemaType === 'number') {
    return typeof data === 'number';
  }
  if (schemaType === 'boolean') {
    return typeof data === 'boolean';
  }
  return false;
}

function validateFormat(format, value) {
  if (format === 'date-time') {
    if (typeof value !== 'string' || !DATE_TIME_REGEX.test(value)) {
      return false;
    }
    const date = new Date(value);
    return !Number.isNaN(date.getTime());
  }
  return true;
}

function validate(schema, data, path = '') {
  const errors = [];

  if (schema.type) {
    if (!validateType(schema.type, data)) {
      errors.push(`${path || '<root>'} should be of type ${schema.type}`);
      return errors;
    }
  }

  if (schema.const !== undefined && data !== schema.const) {
    errors.push(`${path || '<root>'} must equal ${schema.const}`);
  }

  if (schema.enum && !schema.enum.includes(data)) {
    errors.push(`${path || '<root>'} must be one of ${schema.enum.join(', ')}`);
  }

  if (schema.pattern && typeof data === 'string') {
    const regex = new RegExp(schema.pattern);
    if (!regex.test(data)) {
      errors.push(`${path || '<root>'} does not match pattern ${schema.pattern}`);
    }
  }

  if (schema.format && !validateFormat(schema.format, data)) {
    errors.push(`${path || '<root>'} is not a valid ${schema.format}`);
  }

  if (schema.minimum !== undefined && typeof data === 'number') {
    if (data < schema.minimum) {
      errors.push(`${path || '<root>'} must be >= ${schema.minimum}`);
    }
  }

  if (schema.minItems !== undefined && Array.isArray(data)) {
    if (data.length < schema.minItems) {
      errors.push(`${path || '<root>'} must contain at least ${schema.minItems} items`);
    }
  }

  if (schema.type === 'object') {
    const required = schema.required || [];
    for (const key of required) {
      if (!(key in data)) {
        errors.push(`${path || '<root>'}.${key} is required`);
      }
    }

    const properties = schema.properties || {};
    for (const [key, value] of Object.entries(data)) {
      const childPath = path ? `${path}.${key}` : key;
      if (properties[key]) {
        errors.push(...validate(properties[key], value, childPath));
      } else if (schema.additionalProperties === false) {
        errors.push(`${childPath} is not allowed`);
      }
    }
  }

  if (schema.type === 'array' && schema.items) {
    data.forEach((item, index) => {
      const childPath = `${path || '<root>'}[${index}]`;
      errors.push(...validate(schema.items, item, childPath));
    });
  }

  return errors;
}

export function validateWithSchema(schema, data) {
  return validate(schema, data);
}
