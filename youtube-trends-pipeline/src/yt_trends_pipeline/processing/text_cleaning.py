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

# TODO: Transform into function for extracting urls
# Currently not needed as alphanum already clears them  
def remove_urls(text: str) -> str:
    """Replace URLs with a space to avoid joining words."""
    return _URL_PATTERN.sub(" ", text)

# TODO: Transform into function for extracting emojis
# Currently not needed as alphanum already clears them
#def remove_emojis(text: str) -> str:
#    """Remove emoji and similar symbols."""
#    return _EMOJI_PATTERN.sub(" ", text)

def remove_extra_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines to a single space and strip."""
    return " ".join(text.split())

# TODO: refactor function, takeaway uneeeded arguments
def clean_for_lemma(text: str,) -> str:
    """
    Clean raw text before lemmatization. Returns a single string.
    Only letters and spaces are kept (for bag-of-words style).
    """
    text = _ALPHANUM_SPACE.sub(" ", text.lower())  
    return remove_extra_whitespace(text)   
