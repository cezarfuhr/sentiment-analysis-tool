import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health check returns correct status"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "models_loaded" in data


class TestSentimentEndpoint:
    """Test sentiment analysis endpoint"""

    def test_analyze_sentiment_positive(self):
        """Test positive sentiment analysis"""
        response = client.post(
            "/api/v1/sentiment",
            json={"text": "I love this product! It's amazing!"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["label"] == "positive"
        assert "scores" in data
        assert "confidence" in data
        assert data["confidence"] > 0

    def test_analyze_sentiment_negative(self):
        """Test negative sentiment analysis"""
        response = client.post(
            "/api/v1/sentiment",
            json={"text": "This is terrible! I hate it!"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["label"] == "negative"
        assert data["scores"]["negative"] > 0

    def test_analyze_sentiment_with_language(self):
        """Test sentiment analysis with language specification"""
        response = client.post(
            "/api/v1/sentiment",
            json={
                "text": "Eu amo este produto!",
                "language": "pt"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data["language"] == "pt"
        assert data["label"] == "positive"

    def test_analyze_sentiment_with_model(self):
        """Test sentiment analysis with model selection"""
        response = client.post(
            "/api/v1/sentiment",
            json={
                "text": "This is great!",
                "model": "nltk"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "NLTK" in data["model_used"]

    def test_analyze_sentiment_empty_text(self):
        """Test sentiment analysis with empty text"""
        response = client.post(
            "/api/v1/sentiment",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error

    def test_analyze_sentiment_long_text(self):
        """Test sentiment analysis with very long text"""
        long_text = "This is a great product. " * 1000
        response = client.post(
            "/api/v1/sentiment",
            json={"text": long_text}
        )
        # Should handle long text (up to max_length limit)
        assert response.status_code in [200, 422]


class TestEmotionEndpoint:
    """Test emotion analysis endpoint"""

    def test_analyze_emotion_joy(self):
        """Test joy emotion detection"""
        response = client.post(
            "/api/v1/emotion",
            json={"text": "I'm so happy and excited!"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["primary_emotion"] in ["joy", "love", "surprise"]
        assert "scores" in data
        assert data["confidence"] > 0

    def test_analyze_emotion_sadness(self):
        """Test sadness emotion detection"""
        response = client.post(
            "/api/v1/emotion",
            json={"text": "I'm so sad and depressed."}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["primary_emotion"] in ["sadness", "fear", "anger"]

    def test_analyze_emotion_anger(self):
        """Test anger emotion detection"""
        response = client.post(
            "/api/v1/emotion",
            json={"text": "This makes me so angry!"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["primary_emotion"] in ["anger", "sadness"]


class TestCombinedAnalysisEndpoint:
    """Test combined analysis endpoint"""

    def test_analyze_combined(self):
        """Test combined sentiment and emotion analysis"""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "I love this product! It's amazing!"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "sentiment" in data
        assert "emotion" in data
        assert data["sentiment"]["label"] == "positive"
        assert data["emotion"]["primary_emotion"] in ["joy", "love", "surprise"]


class TestBatchEndpoint:
    """Test batch analysis endpoint"""

    def test_analyze_batch(self):
        """Test batch sentiment analysis"""
        response = client.post(
            "/api/v1/sentiment/batch",
            json={
                "texts": [
                    "I love this!",
                    "This is terrible!",
                    "It's okay."
                ]
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert "summary" in data
        assert "average_confidence" in data

        # Check summary
        assert data["summary"]["positive"] >= 1
        assert data["summary"]["negative"] >= 1

    def test_analyze_batch_empty(self):
        """Test batch analysis with empty list"""
        response = client.post(
            "/api/v1/sentiment/batch",
            json={"texts": []}
        )
        assert response.status_code == 422  # Validation error

    def test_analyze_batch_too_many(self):
        """Test batch analysis with too many texts"""
        response = client.post(
            "/api/v1/sentiment/batch",
            json={"texts": ["text"] * 101}
        )
        assert response.status_code == 422  # Validation error


class TestModelsEndpoint:
    """Test models information endpoint"""

    def test_list_models(self):
        """Test listing available models"""
        response = client.get("/api/v1/models")
        assert response.status_code == 200

        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0

        # Check model structure
        model = data["models"][0]
        assert "name" in model
        assert "type" in model
        assert "loaded" in model


class TestLanguagesEndpoint:
    """Test languages information endpoint"""

    def test_list_languages(self):
        """Test listing supported languages"""
        response = client.get("/api/v1/languages")
        assert response.status_code == 200

        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0

        # Check language structure
        lang = data["languages"][0]
        assert "code" in lang
        assert "name" in lang
        assert "models" in lang


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
