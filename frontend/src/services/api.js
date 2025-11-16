import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Sentiment analysis
export const analyzeSentiment = async (text, language = null, model = null) => {
  const response = await api.post('/sentiment', {
    text,
    language,
    model,
  });
  return response.data;
};

// Emotion analysis
export const analyzeEmotion = async (text, language = null) => {
  const response = await api.post('/emotion', {
    text,
    language,
  });
  return response.data;
};

// Combined analysis
export const analyzeCombined = async (text, language = null, model = null) => {
  const response = await api.post('/analyze', {
    text,
    language,
    model,
  });
  return response.data;
};

// Batch sentiment analysis
export const analyzeBatch = async (texts, language = null, model = null) => {
  const response = await api.post('/sentiment/batch', {
    texts,
    language,
    model,
  });
  return response.data;
};

// Twitter analysis
export const analyzeTwitter = async (query, maxResults = 10, language = null) => {
  const response = await api.post('/twitter/analyze', {
    query,
    max_results: maxResults,
    language,
  });
  return response.data;
};

// Get available models
export const getModels = async () => {
  const response = await api.get('/models');
  return response.data;
};

// Get supported languages
export const getLanguages = async () => {
  const response = await api.get('/languages');
  return response.data;
};

export default api;
