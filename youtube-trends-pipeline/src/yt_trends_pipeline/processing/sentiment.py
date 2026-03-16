"""Simple sentiment scoring for comments (VADER)."""

from typing import List, Optional, Tuple

from .text_cleaning import clean_for_lemma

_VADER = None


def _get_analyzer():
    """Lazy-load VADER sentiment analyzer."""
    global _VADER
    if _VADER is None:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _VADER = SentimentIntensityAnalyzer()
    return _VADER


def score_text(text: Optional[str]) -> float:
    """
    Return compound sentiment score in [-1, 1]. Positive = more positive sentiment.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return 0.0
    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)
    return float(scores.get("compound", 0.0))


def aggregate_sentiment(scores: List[float]) -> Tuple[float, float, int]:
    """Return (mean, std, count). If no scores, returns (0.0, 0.0, 0)."""
    if not scores:
        return 0.0, 0.0, 0
    n = len(scores)
    mean = sum(scores) / n
    variance = sum((x - mean) ** 2 for x in scores) / n if n > 0 else 0
    std = variance ** 0.5
    return round(mean, 4), round(std, 4), n
