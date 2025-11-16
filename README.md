# Sentiment Analysis Tool

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Ferramenta completa de análise de sentimentos e emoções em textos e redes sociais**

[Características](#características) •
[Instalação](#instalação) •
[Uso](#uso) •
[API](#api) •
[Testes](#testes) •
[Arquitetura](#arquitetura)

</div>

---

## 📋 Características

### 📊 Análise de Sentimentos
- **Polaridade**: Detecta se o texto é positivo, negativo ou neutro
- **Pontuação de Confiança**: Fornece scores detalhados para cada categoria
- **Múltiplos Modelos**: Suporte para NLTK (VADER), spaCy e Transformers (BERT)

### 🎭 Detecção de Emoções
- **6 Emoções Principais**: Joy, Sadness, Anger, Fear, Surprise, Love
- **Análise Profunda**: Scores detalhados para cada emoção
- **Alta Precisão**: Usa modelos state-of-the-art (RoBERTa)

### 🌐 Suporte Multi-idioma
- **Português** 🇧🇷
- **Inglês** 🇺🇸
- **Espanhol** 🇪🇸
- **Auto-detecção** de idioma

### 📦 Processamento em Lote
- Analise múltiplos textos simultaneamente
- Estatísticas agregadas e visualizações
- Exportação de resultados

### 🐦 Integração Twitter
- Busca e análise de tweets em tempo real
- Análise de tendências de sentimento
- Métricas de engajamento
- Distribuição de emoções

### 📈 Visualizações
- Gráficos de distribuição de sentimentos
- Charts de emoções
- Dashboards interativos
- Métricas em tempo real

---

## 🚀 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **NLTK** - Natural Language Toolkit
- **spaCy** - Processamento de linguagem natural industrial
- **Transformers** - Modelos de IA state-of-the-art (Hugging Face)
- **Redis** - Cache e otimização de performance
- **Tweepy** - Integração com Twitter API
- **Pytest** - Testes automatizados

### Frontend
- **React** - Biblioteca para interfaces de usuário
- **Chart.js** - Visualizações e gráficos
- **Axios** - Cliente HTTP
- **React Testing Library** - Testes de componentes

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers
- **Makefile** - Automação de comandos

---

## 📦 Instalação

### Pré-requisitos
- Docker e Docker Compose
- Git

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sentiment-analysis-tool.git
cd sentiment-analysis-tool

# Configure as variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edite o arquivo backend/.env e adicione suas credenciais do Twitter (opcional)

# Build e inicie os serviços
make build
make up

# Ou use docker-compose diretamente
docker-compose build
docker-compose up -d
```

### Opção 2: Instalação Local

#### Backend
```bash
cd backend

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Download dos modelos
python -m spacy download en_core_web_sm
python -m spacy download pt_core_news_sm
python -m spacy download es_core_news_sm

# Inicie o servidor
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm start
```

---

## 🎯 Uso

### Acessando a Aplicação

Após iniciar os serviços:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Usando o Makefile

```bash
# Iniciar todos os serviços
make up

# Ver logs
make logs

# Executar testes
make test

# Parar serviços
make down

# Limpar tudo
make clean

# Ver todos os comandos
make help
```

### Interface Web

1. **Análise de Sentimento**
   - Digite ou cole o texto
   - Selecione o idioma (opcional)
   - Escolha o modelo (opcional)
   - Clique em "Analyze Sentiment"

2. **Detecção de Emoções**
   - Digite o texto para análise
   - Veja a emoção dominante e scores detalhados

3. **Análise em Lote**
   - Cole múltiplos textos (um por linha)
   - Veja estatísticas agregadas
   - Visualize distribuições em gráficos

4. **Análise do Twitter**
   - Configure suas credenciais da API do Twitter
   - Digite uma query de busca
   - Analise sentimentos de tweets em tempo real

---

## 🔌 API

### Endpoints Principais

#### Health Check
```http
GET /api/v1/health
```

#### Análise de Sentimento
```http
POST /api/v1/sentiment
Content-Type: application/json

{
  "text": "I love this product!",
  "language": "en",
  "model": "transformers"
}
```

**Resposta:**
```json
{
  "text": "I love this product!",
  "label": "positive",
  "scores": {
    "positive": 0.95,
    "negative": 0.03,
    "neutral": 0.02
  },
  "confidence": 0.95,
  "language": "en",
  "model_used": "Transformers (BERT)"
}
```

#### Análise de Emoção
```http
POST /api/v1/emotion
Content-Type: application/json

{
  "text": "I'm so happy today!"
}
```

#### Análise Combinada
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "text": "Your text here"
}
```

#### Análise em Lote
```http
POST /api/v1/sentiment/batch
Content-Type: application/json

{
  "texts": [
    "I love this!",
    "This is terrible!",
    "It's okay."
  ]
}
```

#### Análise do Twitter
```http
POST /api/v1/twitter/analyze
Content-Type: application/json

{
  "query": "#python",
  "max_results": 10
}
```

### Exemplos com cURL

```bash
# Análise de sentimento
curl -X POST "http://localhost:8000/api/v1/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

# Análise de emoção
curl -X POST "http://localhost:8000/api/v1/emotion" \
  -H "Content-Type: application/json" \
  -d '{"text": "I am so happy!"}'
```

### Exemplos com Python

```python
import requests

# Análise de sentimento
response = requests.post(
    "http://localhost:8000/api/v1/sentiment",
    json={"text": "I love this product!"}
)
result = response.json()
print(f"Sentiment: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")

# Análise em lote
texts = [
    "I love this!",
    "This is terrible!",
    "It's okay."
]
response = requests.post(
    "http://localhost:8000/api/v1/sentiment/batch",
    json={"texts": texts}
)
results = response.json()
print(f"Analyzed {len(results['results'])} texts")
print(f"Summary: {results['summary']}")
```

---

## 🧪 Testes

### Executar Todos os Testes
```bash
make test
```

### Testes do Backend
```bash
# Com Docker
make test-backend

# Localmente
cd backend
pytest

# Com coverage
pytest --cov=app --cov-report=html
```

### Testes do Frontend
```bash
# Com Docker
make test-frontend

# Localmente
cd frontend
npm test

# Com coverage
npm run test:coverage
```

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│     Frontend    │
│   (React App)   │
│   Port: 3000    │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐      ┌──────────────┐
│   Backend API   │◄────►│    Redis     │
│   (FastAPI)     │      │   (Cache)    │
│   Port: 8000    │      │  Port: 6379  │
└────────┬────────┘      └──────────────┘
         │
         ├─► NLTK (VADER)
         ├─► spaCy
         ├─► Transformers (BERT/RoBERTa)
         └─► Twitter API
```

### Estrutura de Diretórios

```
sentiment-analysis-tool/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── sentiment_analyzer.py
│   │   │   └── twitter_service.py
│   │   ├── tests/
│   │   │   ├── test_api.py
│   │   │   └── test_sentiment_analyzer.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SentimentAnalyzer.js
│   │   │   ├── EmotionAnalyzer.js
│   │   │   ├── BatchAnalyzer.js
│   │   │   └── TwitterAnalyzer.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── tests/
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 🔧 Configuração

### Variáveis de Ambiente - Backend

Edite o arquivo `backend/.env`:

```env
# Application
APP_NAME=Sentiment Analysis API
APP_VERSION=1.0.0
DEBUG=True

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Twitter API (opcional)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Models
DEFAULT_MODEL=transformers
ENABLE_CACHING=True
```

### Variáveis de Ambiente - Frontend

Edite o arquivo `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_NAME=Sentiment Analysis Tool
```

---

## 📊 Modelos Disponíveis

### 1. NLTK (VADER)
- **Tipo**: Rule-based
- **Vantagens**: Rápido, bom para redes sociais
- **Idiomas**: Inglês (principalmente)

### 2. spaCy
- **Tipo**: Statistical NLP
- **Vantagens**: Processamento avançado, entidades
- **Idiomas**: Inglês, Português, Espanhol

### 3. Transformers (BERT)
- **Tipo**: Deep Learning
- **Vantagens**: Alta precisão, state-of-the-art
- **Idiomas**: Multilingual

---

## 🐦 Configuração do Twitter

Para usar a funcionalidade de análise do Twitter:

1. Crie uma conta de desenvolvedor no [Twitter Developer Portal](https://developer.twitter.com/)
2. Crie um novo App e obtenha as credenciais
3. Adicione as credenciais no arquivo `backend/.env`
4. Reinicie o backend

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter)

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Hugging Face](https://huggingface.co/) - Modelos Transformers
- [NLTK](https://www.nltk.org/) - Natural Language Toolkit
- [spaCy](https://spacy.io/) - Industrial NLP
- [React](https://reactjs.org/) - UI Framework
- [Chart.js](https://www.chartjs.org/) - Visualizações

---

## 📞 Suporte

Se você tiver alguma dúvida ou problema:

- Abra uma [issue](https://github.com/seu-usuario/sentiment-analysis-tool/issues)
- Entre em contato: seu-email@exemplo.com

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela! ⭐**

Made with ❤️ and Python 🐍

</div>