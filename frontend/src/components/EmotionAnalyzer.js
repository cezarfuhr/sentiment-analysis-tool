import React, { useState } from 'react';
import { analyzeEmotion } from '../services/api';

function EmotionAnalyzer() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('');
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
      const data = await analyzeEmotion(text, language || null);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing emotion');
    } finally {
      setLoading(false);
    }
  };

  const emotionEmojis = {
    joy: '😊',
    sadness: '😢',
    anger: '😠',
    fear: '😨',
    surprise: '😮',
    love: '❤️',
    neutral: '😐'
  };

  return (
    <div className="card">
      <h2>Emotion Analysis</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Detect emotions in text - joy, sadness, anger, fear, surprise, and love
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Text to Analyze</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to analyze emotions..."
            required
          />
        </div>

        <div className="form-group">
          <label>Language (optional)</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="">Auto-detect</option>
            <option value="en">English</option>
            <option value="pt">Portuguese</option>
            <option value="es">Spanish</option>
          </select>
        </div>

        <button type="submit" className="button" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Emotions'}
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

          <div style={{ marginTop: '15px', fontSize: '2rem' }}>
            {emotionEmojis[result.primary_emotion]}
            <span className={`emotion-badge emotion-${result.primary_emotion}`} style={{ marginLeft: '15px' }}>
              {result.primary_emotion}
            </span>
          </div>

          <div style={{ marginTop: '10px', color: '#666' }}>
            Confidence: {(result.confidence * 100).toFixed(1)}%
          </div>

          <div className="scores">
            <h4 style={{ marginBottom: '15px', color: '#333' }}>Emotion Scores</h4>

            {Object.entries(result.scores).map(([emotion, score]) => (
              <div key={emotion} className="score-bar">
                <div className="score-label">
                  <span>{emotionEmojis[emotion]} {emotion}</span>
                  <span>{(score * 100).toFixed(1)}%</span>
                </div>
                <div className="score-progress">
                  <div
                    className="score-fill"
                    style={{ width: `${score * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '15px', fontSize: '0.9rem', color: '#666' }}>
            <strong>Language:</strong> {result.language} | <strong>Model:</strong> {result.model_used}
          </div>
        </div>
      )}
    </div>
  );
}

export default EmotionAnalyzer;
