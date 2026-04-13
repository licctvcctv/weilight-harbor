"""Sensitive word detection with application-level caching."""
import time

_cache = {'words': None, 'ts': 0}
_CACHE_TTL = 300  # 5 minutes


def _load_words():
    now = time.time()
    if _cache['words'] is not None and (now - _cache['ts']) < _CACHE_TTL:
        return _cache['words']

    from applications.models.sensitive_word import SensitiveWord
    words = SensitiveWord.query.all()
    _cache['words'] = [(w.word.lower(), w.severity) for w in words]
    _cache['ts'] = now
    return _cache['words']


def check_sensitive(text):
    """Check text for sensitive words. Returns list of matches with severity."""
    if not text:
        return []
    words = _load_words()
    text_lower = text.lower()
    return [{'word': w, 'severity': s} for w, s in words if w in text_lower]


def has_crisis_words(text):
    """Check if text contains crisis-level (severity >= 2) sensitive words."""
    if not text:
        return False
    words = _load_words()
    text_lower = text.lower()
    return any(s >= 2 for w, s in words if w in text_lower)
