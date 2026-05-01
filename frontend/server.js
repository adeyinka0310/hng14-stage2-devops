const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

// BUG FIX: Original had no JSON body parsing middleware
// Without this, req.body is always undefined when frontend sends JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// BUG FIX: Original hardcoded "localhost:8000" — must use service name in Docker
const API_URL = process.env.API_URL || 'http://api:8000';

// Health check endpoint for Docker
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Proxy route: frontend calls this, which calls the API
app.post('/submit', async (req, res) => {
  try {
    const { payload } = req.body;
    // BUG FIX: Original sent wrong field name to API
    const response = await axios.post(`${API_URL}/jobs`, { payload });
    res.json(response.data);
  } catch (err) {
    console.error('Error submitting job:', err.message);
    res.status(500).json({ error: 'Failed to submit job' });
  }
});

// Proxy route: check job status
app.get('/status/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const response = await axios.get(`${API_URL}/jobs/${jobId}`);
    res.json(response.data);
  } catch (err) {
    console.error('Error fetching status:', err.message);
    res.status(500).json({ error: 'Failed to fetch status' });
  }
});

// BUG FIX: Original used PORT=3000 hardcoded, must read from env
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  // BUG FIX: Original listened on 127.0.0.1 which is unreachable from other containers
  console.log(`Frontend running on port ${PORT}`);
});