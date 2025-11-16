import pytest
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.models.schemas import ModelType, SentimentLabel, EmotionLabel


@pytest.fixture
def analyzer():
    """Create sentiment analyzer instance"""
    return SentimentAnalyzer()


class TestSentimentAnalyzer:
    """Test sentiment analyzer service"""

    def test_initialization(self, analyzer):
        """Test that models are loaded"""
        assert analyzer.models_loaded["nltk"] is True
        assert isinstance(analyzer.sia, object)

    def test_language_detection(self, analyzer):
        """Test language detection"""
        # English
        lang = analyzer.detect_language("Hello, how are you?")
        assert lang == "en"

        # Portuguese
        lang = analyzer.detect_language("Olá, como você está?")
        assert lang == "pt"

        # Spanish
        lang = analyzer.detect_language("Hola, ¿cómo estás?")
        assert lang == "es"

    def test_sentiment_analysis_positive(self, analyzer):
        """Test positive sentiment analysis"""
        text = "I love this product! It's amazing and wonderful!"
        result = analyzer.analyze_sentiment(text, model=ModelType.NLTK)

        assert result.label == SentimentLabel.POSITIVE
        assert result.scores.positive > 0.5
        assert result.confidence > 0
        assert result.language == "en"

    def test_sentiment_analysis_negative(self, analyzer):
        """Test negative sentiment analysis"""
        text = "This is terrible and awful. I hate it!"
        result = analyzer.analyze_sentiment(text, model=ModelType.NLTK)

        assert result.label == SentimentLabel.NEGATIVE
        assert result.scores.negative > 0.3
        assert result.confidence > 0

    def test_sentiment_analysis_neutral(self, analyzer):
        """Test neutral sentiment analysis"""
        text = "This is a product."
        result = analyzer.analyze_sentiment(text, model=ModelType.NLTK)

        assert result.label in [SentimentLabel.NEUTRAL, SentimentLabel.POSITIVE, SentimentLabel.NEGATIVE]
        assert result.confidence >= 0

    def test_sentiment_analysis_multilingual(self, analyzer):
        """Test sentiment analysis in different languages"""
        # Portuguese
        text_pt = "Eu amo este produto! É incrível!"
        result_pt = analyzer.analyze_sentiment(text_pt)
        assert result_pt.language == "pt"
        assert result_pt.label == SentimentLabel.POSITIVE

        # Spanish
        text_es = "¡Me encanta este producto! Es increíble!"
        result_es = analyzer.analyze_sentiment(text_es)
        assert result_es.language == "es"
        assert result_es.label == SentimentLabel.POSITIVE

    def test_emotion_analysis(self, analyzer):
        """Test emotion analysis"""
        # Joy
        text = "I'm so happy and excited about this!"
        result = analyzer.analyze_emotions(text)
        assert result.primary_emotion in [EmotionLabel.JOY, EmotionLabel.LOVE, EmotionLabel.SURPRISE]
        assert result.confidence > 0

        # Sadness
        text = "I'm so sad and depressed about this."
        result = analyzer.analyze_emotions(text)
        assert result.primary_emotion in [EmotionLabel.SADNESS, EmotionLabel.ANGER, EmotionLabel.FEAR]

        # Anger
        text = "This makes me so angry and furious!"
        result = analyzer.analyze_emotions(text)
        assert result.primary_emotion in [EmotionLabel.ANGER, EmotionLabel.SADNESS]

    def test_batch_analysis(self, analyzer):
        """Test batch sentiment analysis"""
        texts = [
            "I love this!",
            "This is terrible!",
            "It's okay."
        ]

        results = analyzer.analyze_batch(texts, model=ModelType.NLTK)

        assert len(results) == 3
        assert results[0].label == SentimentLabel.POSITIVE
        assert results[1].label == SentimentLabel.NEGATIVE
        assert all(r.confidence >= 0 for r in results)

    def test_empty_text(self, analyzer):
        """Test handling of empty or very short text"""
        try:
            text = "a"
            result = analyzer.analyze_sentiment(text)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Should handle short text: {e}")

    def test_long_text(self, analyzer):
        """Test handling of long text"""
        text = "This is a great product. " * 100
        result = analyzer.analyze_sentiment(text, model=ModelType.NLTK)

        assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.NEGATIVE, SentimentLabel.NEUTRAL]
        assert len(result.text) <= 103  # Truncated to 100 chars + "..."

    def test_special_characters(self, analyzer):
        """Test handling of special characters"""
        text = "I love this!!! 😊 ❤️ #amazing @product"
        result = analyzer.analyze_sentiment(text, model=ModelType.NLTK)

        assert result.label == SentimentLabel.POSITIVE
        assert result.confidence > 0

    def test_model_selection(self, analyzer):
        """Test different model selection"""
        text = "This is great!"

        # NLTK
        result_nltk = analyzer.analyze_sentiment(text, model=ModelType.NLTK)
        assert "NLTK" in result_nltk.model_used

        # Transformers
        result_transformers = analyzer.analyze_sentiment(text, model=ModelType.TRANSFORMERS)
        assert "Transformers" in result_transformers.model_used
