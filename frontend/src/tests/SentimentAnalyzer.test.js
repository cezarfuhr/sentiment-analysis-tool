import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SentimentAnalyzer from '../components/SentimentAnalyzer';
import * as api from '../services/api';

jest.mock('../services/api');

describe('SentimentAnalyzer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders sentiment analyzer form', () => {
    render(<SentimentAnalyzer />);

    expect(screen.getByText(/Sentiment Analysis/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter text to analyze sentiment/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Analyze Sentiment/i })).toBeInTheDocument();
  });

  test('displays error when submitting empty text', async () => {
    render(<SentimentAnalyzer />);

    const button = screen.getByRole('button', { name: /Analyze Sentiment/i });
    fireEvent.click(button);

    // Form validation should prevent submission
    expect(api.analyzeSentiment).not.toHaveBeenCalled();
  });

  test('analyzes sentiment successfully', async () => {
    const mockResult = {
      text: 'I love this!',
      label: 'positive',
      scores: {
        positive: 0.95,
        negative: 0.03,
        neutral: 0.02
      },
      confidence: 0.95,
      language: 'en',
      model_used: 'Transformers (BERT)'
    };

    api.analyzeSentiment.mockResolvedValue(mockResult);

    render(<SentimentAnalyzer />);

    const textarea = screen.getByPlaceholderText(/Enter text to analyze sentiment/i);
    const button = screen.getByRole('button', { name: /Analyze Sentiment/i });

    fireEvent.change(textarea, { target: { value: 'I love this!' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Results')).toBeInTheDocument();
      expect(screen.getByText(/positive/i)).toBeInTheDocument();
    });

    expect(api.analyzeSentiment).toHaveBeenCalledWith('I love this!', null, null);
  });

  test('displays error on API failure', async () => {
    api.analyzeSentiment.mockRejectedValue({
      response: { data: { detail: 'API Error' } }
    });

    render(<SentimentAnalyzer />);

    const textarea = screen.getByPlaceholderText(/Enter text to analyze sentiment/i);
    const button = screen.getByRole('button', { name: /Analyze Sentiment/i });

    fireEvent.change(textarea, { target: { value: 'Test text' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/API Error/i)).toBeInTheDocument();
    });
  });

  test('allows language selection', () => {
    render(<SentimentAnalyzer />);

    const languageSelect = screen.getByLabelText(/Language/i);

    fireEvent.change(languageSelect, { target: { value: 'pt' } });

    expect(languageSelect.value).toBe('pt');
  });

  test('allows model selection', () => {
    render(<SentimentAnalyzer />);

    const modelSelect = screen.getByLabelText(/Model/i);

    fireEvent.change(modelSelect, { target: { value: 'nltk' } });

    expect(modelSelect.value).toBe('nltk');
  });
});
