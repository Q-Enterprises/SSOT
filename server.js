/**
 * Google Fonts Proxy Server
 * Provides caching and rate limiting for Google Fonts API
 */

const express = require('express');
const app = express();

const PORT = process.env.PORT || 8787;
const GOOGLE_FONTS_API_KEY = process.env.GOOGLE_FONTS_API_KEY || '';
const PROXY_KEY = process.env.PROXY_KEY || '';

// Middleware
app.use(express.json());

// API Key validation middleware
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || apiKey !== PROXY_KEY) {
    return res.status(401).json({ message: 'Unauthorized', code: 'INVALID_API_KEY' });
  }
  
  next();
};

// Health check endpoint (no auth required)
app.get('/healthz', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// List fonts endpoint
app.get('/api/fonts/list', validateApiKey, async (req, res) => {
  try {
    const { sort = 'popularity', subset } = req.query;
    
    // Mock response for now - in production would call Google Fonts API
    const response = {
      kind: 'webfonts#webfontList',
      items: [
        {
          family: 'Roboto',
          category: 'sans-serif',
          variants: ['regular', 'italic', '700', '700italic'],
          subsets: ['latin', 'cyrillic']
        },
        {
          family: 'Inter',
          category: 'sans-serif',
          variants: ['regular', 'italic', '700'],
          subsets: ['latin']
        }
      ]
    };
    
    res.json(response);
  } catch (error) {
    console.error('Error listing fonts:', error);
    res.status(500).json({ message: 'Internal server error', code: 'INTERNAL_ERROR' });
  }
});

// Get font files endpoint
app.get('/api/fonts/files', validateApiKey, async (req, res) => {
  try {
    const { family } = req.query;
    
    if (!family) {
      return res.status(400).json({ 
        message: 'Family parameter is required', 
        code: 'MISSING_FAMILY' 
      });
    }
    
    // Mock response for now - in production would call Google Fonts API
    const response = {
      kind: 'webfonts#webfont',
      items: {
        'regular': 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2',
        '700': 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuGKYAZ9hiA.woff2'
      }
    };
    
    res.json(response);
  } catch (error) {
    console.error('Error getting font files:', error);
    res.status(500).json({ message: 'Internal server error', code: 'INTERNAL_ERROR' });
  }
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ message: 'Not found', code: 'NOT_FOUND' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ message: 'Internal server error', code: 'INTERNAL_ERROR' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Google Fonts Proxy listening on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/healthz`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});
