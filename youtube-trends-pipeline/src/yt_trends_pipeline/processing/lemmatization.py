"""Lemmatization using spaCy (with optional fallback)."""

from typing import List, Optional

from .text_cleaning import clean_for_lemma

_NLP = None


def _get_nlp():
    """Lazy-load spaCy model (en_core_web_sm)."""
    global _NLP
    if _NLP is None:
        try:
            import spacy
            _NLP = spacy.load("en_core_web_sm")
        except OSError:
            import spacy
            spacy.cli.download("en_core_web_sm")
            _NLP = spacy.load("en_core_web_sm")
    return _NLP


def lemmatize_text(
    text: Optional[str],
    clean_first: bool = True,
    remove_stop: bool = True,
    min_len: int = 2,
) -> str:
    """
    Lemmatize text and return space-joined lemmas. Skips stop words if remove_stop.
    Uses en_core_web_sm; for non-English consider a multilingual model later.
    """
    if not text:
        return ""
    if clean_first:
        text = clean_for_lemma(text, strip_non_alpha=False)
    if not text.strip():
        return ""
    nlp = _get_nlp()
    doc = nlp(text[:1_000_000])  # spaCy length limit
    lemmas: List[str] = []
    for tok in doc:
        if tok.is_space or tok.is_punct:
            continue
        if remove_stop and tok.is_stop:
            continue
        if len(tok.lemma_) < min_len:
            continue
        lemmas.append(tok.lemma_)
    return " ".join(lemmas)


def lemmatize_joined(title: Optional[str], description: Optional[str], **kwargs) -> str:
    """Join title and description with a space, then lemmatize. Good for theme analysis."""
    parts = [p for p in (title, description) if p and str(p).strip()]
    combined = " ".join(parts) if parts else ""
    return lemmatize_text(combined, **kwargs)
