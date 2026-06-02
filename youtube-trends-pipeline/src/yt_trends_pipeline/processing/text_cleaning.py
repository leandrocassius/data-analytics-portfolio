"""Text cleaning utilities: lowercasing, URL/emoji removal, punctuation normalization."""

import re
from typing import Optional


# Match URLs
_URL_PATTERN = re.compile(
    r"https?://[^\s]+|www\.[^\s]+",
    re.IGNORECASE,
)

# Match common emoji/symbols (simplified)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # misc symbols & pictographs
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)

# Keep only letters, numbers, and spaces (after cleaning)
_ALPHANUM_SPACE = re.compile(r"[^a-z0-9\s]")


def remove_urls(text: str) -> str:
    """Replace URLs with a space to avoid joining words."""
    return _URL_PATTERN.sub(" ", text)


def remove_emojis(text: str) -> str:
    """Remove emoji and similar symbols."""
    return _EMOJI_PATTERN.sub(" ", text)


def to_lower(text: str) -> str:
    """Lowercase for consistent tokenization."""
    return text.lower()


def remove_extra_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines to a single space and strip."""
    return " ".join(text.split())

# TODO: refactor function, takeaway uneeeded arguments
def clean_for_lemma(
    text: Optional[str],
    lowercase: bool = True,
    remove_urls_flag: bool = True,
    remove_emoji: bool = True,
    strip_non_alpha: bool = False,
) -> str:
    """
    Clean raw text before lemmatization. Returns a single string.
    If strip_non_alpha is True, only letters and spaces are kept (for bag-of-words style).
    """
    if not text or not isinstance(text, str):
        return ""
    t = text.strip()
    if remove_urls_flag:
        t = remove_urls(t)
    if remove_emoji:
        t = remove_emojis(t)
    if lowercase:
        t = to_lower(t)
    t = remove_extra_whitespace(t)
    if strip_non_alpha:
        t = _ALPHANUM_SPACE.sub(" ", t)
        t = remove_extra_whitespace(t)
    return t
