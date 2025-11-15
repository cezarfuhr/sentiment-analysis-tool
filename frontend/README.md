# Sentiment Analysis Frontend

Interface React para análise de sentimentos e emoções.

## Estrutura

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/       # Componentes React
│   ├── services/         # Serviços de API
│   ├── tests/            # Testes
│   ├── App.js
│   ├── App.css
│   └── index.js
├── Dockerfile
└── package.json
```

## Instalação Local

```bash
# Instalar dependências
npm install

# Iniciar desenvolvimento
npm start

# Build para produção
npm run build
```

## Testes

```bash
# Executar testes
npm test

# Com coverage
npm run test:coverage
```

## Componentes

- **SentimentAnalyzer**: Análise de sentimento de texto único
- **EmotionAnalyzer**: Detecção de emoções
- **BatchAnalyzer**: Análise em lote com visualizações
- **TwitterAnalyzer**: Busca e análise de tweets

## Tecnologias

- React 18
- Chart.js para visualizações
- Axios para chamadas API
- React Testing Library para testes
