import React, { useState } from 'react';
import { analyzeBatch } from '../services/api';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

function BatchAnalyzer() {
  const [texts, setTexts] = useState('');
  const [language, setLanguage] = useState('');
  const [model, setModel] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!texts.trim()) return;

    const textArray = texts.split('\n').filter(t => t.trim());
    if (textArray.length === 0) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeBatch(
        textArray,
        language || null,
        model || null
      );
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing batch');
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: [
        result.summary.positive,
        result.summary.negative,
        result.summary.neutral
      ],
      backgroundColor: [
        '#28a745',
        '#dc3545',
        '#17a2b8'
      ],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  } : null;

  return (
    <div className="card">
      <h2>Batch Analysis</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Analyze multiple texts at once (one per line)
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Texts to Analyze (one per line)</label>
          <textarea
            value={texts}
            onChange={(e) => setTexts(e.target.value)}
            placeholder="Enter each text on a new line...&#10;Example:&#10;I love this product!&#10;This is terrible.&#10;It's okay."
            className="batch-textarea"
            required
          />
          <div className="help-text">
            {texts.split('\n').filter(t => t.trim()).length} texts
          </div>
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
          {loading ? 'Analyzing...' : 'Analyze Batch'}
        </button>
      </form>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {result && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{result.results.length}</div>
              <div className="stat-label">Total Texts</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#28a745' }}>
                {result.summary.positive}
              </div>
              <div className="stat-label">Positive</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#dc3545' }}>
                {result.summary.negative}
              </div>
              <div className="stat-label">Negative</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#17a2b8' }}>
                {result.summary.neutral}
              </div>
              <div className="stat-label">Neutral</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {(result.average_confidence * 100).toFixed(1)}%
              </div>
              <div className="stat-label">Avg Confidence</div>
            </div>
          </div>

          {chartData && (
            <div className="chart-container">
              <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>
                Sentiment Distribution
              </h3>
              <div style={{ maxWidth: '400px', margin: '0 auto' }}>
                <Pie data={chartData} />
              </div>
            </div>
          )}

          <div style={{ marginTop: '30px' }}>
            <h3 style={{ marginBottom: '15px' }}>Individual Results</h3>
            {result.results.map((item, index) => (
              <div key={index} className="result-card" style={{ marginBottom: '15px' }}>
                <div style={{ marginBottom: '10px', color: '#333' }}>
                  <strong>Text {index + 1}:</strong> {item.text}
                </div>
                <span className={`sentiment-badge sentiment-${item.label}`}>
                  {item.label}
                </span>
                <span style={{ marginLeft: '10px', color: '#666', fontSize: '0.9rem' }}>
                  Confidence: {(item.confidence * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default BatchAnalyzer;
