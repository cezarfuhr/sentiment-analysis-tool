import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

function HistoryDashboard() {
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [statsRes, trendsRes, historyRes] = await Promise.all([
        axios.get(`${API_URL}/stats?days=${days}`),
        axios.get(`${API_URL}/trends?days=${days}`),
        axios.get(`${API_URL}/history?limit=10`)
      ]);

      setStats(statsRes.data);
      setTrends(trendsRes.data);
      setHistory(historyRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format) => {
    try {
      const response = await axios.get(`${API_URL}/export/${format}?days=${days}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sentiment_analysis.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(`Error exporting ${format.toUpperCase()}: ${err.message}`);
    }
  };

  const trendChartData = trends ? {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Positive',
        data: trends.map(t => t.positive_count),
        borderColor: '#28a745',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        tension: 0.4
      },
      {
        label: 'Negative',
        data: trends.map(t => t.negative_count),
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        tension: 0.4
      },
      {
        label: 'Neutral',
        data: trends.map(t => t.neutral_count),
        borderColor: '#17a2b8',
        backgroundColor: 'rgba(23, 162, 184, 0.1)',
        tension: 0.4
      }
    ]
  } : null;

  if (loading && !stats) {
    return (
      <div className="card">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>History & Analytics Dashboard</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        View historical data, trends, and export results
      </p>

      {error && <div className="error">{error}</div>}

      {/* Period Selector */}
      <div className="form-group">
        <label>Time Period</label>
        <select value={days} onChange={(e) => setDays(parseInt(e.target.value))}>
          <option value="1">Last 24 hours</option>
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Analyses</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#28a745' }}>
              {stats.positive}
            </div>
            <div className="stat-label">Positive</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#dc3545' }}>
              {stats.negative}
            </div>
            <div className="stat-label">Negative</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#17a2b8' }}>
              {stats.neutral}
            </div>
            <div className="stat-label">Neutral</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {(stats.avg_confidence * 100).toFixed(1)}%
            </div>
            <div className="stat-label">Avg Confidence</div>
          </div>
        </div>
      )}

      {/* Trend Chart */}
      {trendChartData && trends.length > 0 && (
        <div className="chart-container">
          <h3>Sentiment Trends Over Time</h3>
          <Line
            data={trendChartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top',
                },
                title: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true
                }
              }
            }}
          />
        </div>
      )}

      {/* Export Buttons */}
      <div style={{ marginTop: '30px' }}>
        <h3>Export Data</h3>
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap' }}>
          <button
            onClick={() => exportData('csv')}
            className="button"
            style={{ width: 'auto', padding: '10px 20px' }}
          >
            📊 Export CSV
          </button>
          <button
            onClick={() => exportData('json')}
            className="button"
            style={{ width: 'auto', padding: '10px 20px' }}
          >
            📄 Export JSON
          </button>
          <button
            onClick={() => exportData('pdf')}
            className="button"
            style={{ width: 'auto', padding: '10px 20px' }}
          >
            📑 Export PDF
          </button>
        </div>
      </div>

      {/* Recent History */}
      <div style={{ marginTop: '30px' }}>
        <h3>Recent Analyses</h3>
        {history.length > 0 ? (
          <div style={{ marginTop: '15px' }}>
            {history.map((item) => (
              <div key={item.id} className="result-card" style={{ marginBottom: '15px' }}>
                <div style={{ marginBottom: '10px' }}>
                  <strong>Text:</strong> {item.text}
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                  {item.sentiment_label && (
                    <span className={`sentiment-badge sentiment-${item.sentiment_label}`}>
                      {item.sentiment_label}
                    </span>
                  )}
                  {item.emotion_label && (
                    <span className={`emotion-badge emotion-${item.emotion_label}`}>
                      {item.emotion_label}
                    </span>
                  )}
                  <span style={{ color: '#666', fontSize: '0.9rem' }}>
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#666', marginTop: '15px' }}>No analyses yet</p>
        )}
      </div>

      <button
        onClick={fetchData}
        className="button"
        style={{ marginTop: '20px' }}
        disabled={loading}
      >
        {loading ? 'Refreshing...' : '🔄 Refresh Data'}
      </button>
    </div>
  );
}

export default HistoryDashboard;
