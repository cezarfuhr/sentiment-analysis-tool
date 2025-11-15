import React, { useState } from 'react';
import { analyzeTwitter } from '../services/api';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function TwitterAnalyzer() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [language, setLanguage] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeTwitter(
        query,
        maxResults,
        language || null
      );
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing Twitter. Make sure API credentials are configured.');
    } finally {
      setLoading(false);
    }
  };

  const sentimentChartData = result ? {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: [
        result.sentiment_distribution.positive,
        result.sentiment_distribution.negative,
        result.sentiment_distribution.neutral
      ],
      backgroundColor: ['#28a745', '#dc3545', '#17a2b8'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  } : null;

  const emotionChartData = result ? {
    labels: Object.keys(result.emotion_distribution),
    datasets: [{
      label: 'Emotions',
      data: Object.values(result.emotion_distribution),
      backgroundColor: [
        '#ffc107',
        '#6c757d',
        '#dc3545',
        '#6f42c1',
        '#17a2b8',
        '#e83e8c'
      ]
    }]
  } : null;

  return (
    <div className="card">
      <h2>Twitter Analysis</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Search and analyze sentiment of tweets (requires Twitter API credentials)
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Search Query</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter search query (e.g., #python, @elonmusk)"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Maximum Results</label>
            <input
              type="number"
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              min="1"
              max="100"
              required
            />
          </div>

          <div className="form-group">
            <label>Language (optional)</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="">Any</option>
              <option value="en">English</option>
              <option value="pt">Portuguese</option>
              <option value="es">Spanish</option>
            </select>
          </div>
        </div>

        <button type="submit" className="button" disabled={loading}>
          {loading ? 'Searching & Analyzing...' : 'Analyze Tweets'}
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
              <div className="stat-value">{result.total_tweets}</div>
              <div className="stat-label">Tweets Analyzed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#28a745' }}>
                {result.sentiment_distribution.positive}
              </div>
              <div className="stat-label">Positive</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#dc3545' }}>
                {result.sentiment_distribution.negative}
              </div>
              <div className="stat-label">Negative</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#17a2b8' }}>
                {result.sentiment_distribution.neutral}
              </div>
              <div className="stat-label">Neutral</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '30px' }}>
            {sentimentChartData && (
              <div className="chart-container">
                <h3 style={{ textAlign: 'center', marginBottom: '15px' }}>
                  Sentiment Distribution
                </h3>
                <Pie data={sentimentChartData} />
              </div>
            )}

            {emotionChartData && (
              <div className="chart-container">
                <h3 style={{ textAlign: 'center', marginBottom: '15px' }}>
                  Emotion Distribution
                </h3>
                <Bar data={emotionChartData} options={{ indexAxis: 'y' }} />
              </div>
            )}
          </div>

          <div className="tweets-list">
            <h3 style={{ marginBottom: '15px' }}>Tweets</h3>
            {result.tweets.map((tweet, index) => (
              <div key={tweet.id || index} className="tweet-card">
                <div className="tweet-header">
                  <div className="tweet-author">
                    {tweet.author.name} @{tweet.author.username}
                  </div>
                  <div>
                    <span className={`sentiment-badge sentiment-${tweet.sentiment.label}`}>
                      {tweet.sentiment.label}
                    </span>
                  </div>
                </div>
                <div className="tweet-text">{tweet.text}</div>
                <div style={{ marginBottom: '10px' }}>
                  <span className={`emotion-badge emotion-${tweet.emotion.label}`}>
                    {tweet.emotion.label}
                  </span>
                </div>
                <div className="tweet-metrics">
                  <span>❤️ {tweet.metrics.likes}</span>
                  <span>🔄 {tweet.metrics.retweets}</span>
                  <span>💬 {tweet.metrics.replies}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default TwitterAnalyzer;
