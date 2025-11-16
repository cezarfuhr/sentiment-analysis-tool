# Sentiment Analysis Backend

API FastAPI para análise de sentimentos e emoções usando NLTK, spaCy e Transformers.

## Estrutura

```
backend/
├── app/
│   ├── api/              # Endpoints da API
│   ├── core/             # Configurações
│   ├── models/           # Schemas Pydantic
│   ├── services/         # Lógica de negócio
│   ├── tests/            # Testes automatizados
│   └── main.py           # Entrada da aplicação
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

## Instalação Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Download modelos
python -m spacy download en_core_web_sm
python -m spacy download pt_core_news_sm
python -m spacy download es_core_news_sm
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('stopwords')"

# Iniciar servidor
uvicorn app.main:app --reload
```

## Testes

```bash
# Executar testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes específicos
pytest app/tests/test_api.py
pytest app/tests/test_sentiment_analyzer.py -v
```

## Endpoints

Veja a documentação completa em: http://localhost:8000/docs

## Modelos

- **NLTK (VADER)**: Análise rápida, ótima para textos curtos
- **spaCy**: NLP avançado com múltiplos idiomas
- **Transformers**: State-of-the-art usando BERT e RoBERTa
