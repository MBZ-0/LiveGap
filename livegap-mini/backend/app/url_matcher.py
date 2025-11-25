from urllib.parse import urlsplit


def normalize_url(url: str) -> str:
    """Drop query + fragment, remove trailing slash, lowercase. Preserve root '/' if empty path."""
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    return f"{parts.scheme}://{parts.netloc}{path}".lower()

__all__ = ["normalize_url"]