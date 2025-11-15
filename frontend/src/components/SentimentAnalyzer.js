import React, { useState } from 'react';
import { analyzeSentiment } from '../services/api';

function SentimentAnalyzer() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('');
  const [model, setModel] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeSentiment(
        text,
        language || null,
        model || null
      );
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing sentiment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Sentiment Analysis</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Analyze the sentiment of any text - positive, negative, or neutral
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Text to Analyze</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to analyze sentiment..."
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Language (optional)</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="">Auto-detect</option>
              <option value="en">English</option>
              <option value="pt">Portuguese</option>
              <option value="es">Spanish</option>
            </select>
          </div>

          <div className="form-group">
            <label>Model (optional)</label>
            <select value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">Default (Transformers)</option>
              <option value="nltk">NLTK (VADER)</option>
              <option value="transformers">Transformers (BERT)</option>
            </select>
          </div>
        </div>

        <button type="submit" className="button" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Sentiment'}
        </button>
      </form>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {result && (
        <div className="result-card">
          <h3>Results</h3>

          <div style={{ marginTop: '15px' }}>
            <span className={`sentiment-badge sentiment-${result.label}`}>
              {result.label}
            </span>
            <span style={{ marginLeft: '10px', color: '#666' }}>
              Confidence: {(result.confidence * 100).toFixed(1)}%
            </span>
          </div>

          <div className="scores">
            <div className="score-bar">
              <div className="score-label">
                <span>Positive</span>
                <span>{(result.scores.positive * 100).toFixed(1)}%</span>
              </div>
              <div className="score-progress">
                <div
                  className="score-fill"
                  style={{
                    width: `${result.scores.positive * 100}%`,
                    background: '#28a745'
                  }}
                />
              </div>
            </div>

            <div className="score-bar">
              <div className="score-label">
                <span>Negative</span>
                <span>{(result.scores.negative * 100).toFixed(1)}%</span>
              </div>
              <div className="score-progress">
                <div
                  className="score-fill"
                  style={{
                    width: `${result.scores.negative * 100}%`,
                    background: '#dc3545'
                  }}
                />
              </div>
            </div>

            <div className="score-bar">
              <div className="score-label">
                <span>Neutral</span>
                <span>{(result.scores.neutral * 100).toFixed(1)}%</span>
              </div>
              <div className="score-progress">
                <div
                  className="score-fill"
                  style={{
                    width: `${result.scores.neutral * 100}%`,
                    background: '#17a2b8'
                  }}
                />
              </div>
            </div>
          </div>

          <div style={{ marginTop: '15px', fontSize: '0.9rem', color: '#666' }}>
            <strong>Language:</strong> {result.language} | <strong>Model:</strong> {result.model_used}
          </div>
        </div>
      )}
    </div>
  );
}

export default SentimentAnalyzer;
