import React, { useState } from 'react';
import './App.css';
import SentimentAnalyzer from './components/SentimentAnalyzer';
import EmotionAnalyzer from './components/EmotionAnalyzer';
import BatchAnalyzer from './components/BatchAnalyzer';
import TwitterAnalyzer from './components/TwitterAnalyzer';

function App() {
  const [activeTab, setActiveTab] = useState('sentiment');

  const tabs = [
    { id: 'sentiment', label: 'Sentiment Analysis', icon: '📊' },
    { id: 'emotion', label: 'Emotion Detection', icon: '🎭' },
    { id: 'batch', label: 'Batch Analysis', icon: '📦' },
    { id: 'twitter', label: 'Twitter Analysis', icon: '🐦' }
  ];

  return (
    <div className="App">
      <div className="container">
        <header>
          <h1>Sentiment Analysis Tool</h1>
          <p>Powerful AI-driven sentiment and emotion analysis</p>
        </header>

        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span style={{ marginRight: '8px' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'sentiment' && <SentimentAnalyzer />}
        {activeTab === 'emotion' && <EmotionAnalyzer />}
        {activeTab === 'batch' && <BatchAnalyzer />}
        {activeTab === 'twitter' && <TwitterAnalyzer />}

        <footer>
          <p>
            Powered by NLTK, spaCy, and Transformers
          </p>
          <p style={{ fontSize: '0.9rem', marginTop: '5px' }}>
            Multi-language support: English, Portuguese, Spanish
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
