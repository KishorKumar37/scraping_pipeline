"""
Utility functions for URL normalization, domain validation, and
safe link rewriting during crawling.

This module is designed to be used by:
    - HtmlParser (when cleaning extracted hrefs)
    - Crawler (when filtering same-domain URLs)
    - TraversalStrategy (when pushing normalized URLs)
"""

from __future__ import annotations

from urllib.parse import urlparse, urljoin, urldefrag
from typing import Optional


def extract_domain_root(url: str) -> str:
    """
    Given a full URL, return its scheme + netloc + trailing slash.
    Example:
        https://example.com/some/page  →  https://example.com/
    """
    parsed = urlparse(url)
    # Handle cases like missing scheme or invalid URL
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    return f"{parsed.scheme}://{parsed.netloc}/"


def normalize_url(url: str) -> str:
    """
    Normalize URL:
    - Remove fragments (#...)
    - Keep query parameters intact
    - Ensure trailing slash for consistency
    - Remove default ports if present (e.g., :80, :443 depending on scheme)
    - Lowercase scheme and domain

    This avoids duplicate URLs like:
        /page
        /page/
        /page#index
        /page?ref=123

    NOTE: Deciding whether to keep query params depends on your project.
    We're keeping them because:
        - Many sites use query params for real content
        - Problem statement did NOT instruct removing them
    """
    # 1. Remove fragments
    url, _ = urldefrag(url)

    parsed = urlparse(url)

    # 2. Lowercase scheme + netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # 3. Remove default ports
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # 4. Normalize path
    path = parsed.path

    # Optional: Normalize trailing slash
    # Rule: If no file extension is present → add trailing slash
    if path == "":
        path = "/"
    elif not path.endswith("/") and "." not in path.split("/")[-1]:
        path += "/"

    # 5. Rebuild URL
    normalized = f"{scheme}://{netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"

    return normalized


def ensure_absolute_url(base_url: str, href: str) -> Optional[str]:
    """
    Convert relative links to absolute URLs.

    Examples:
        base = https://example.com/docs/
        href = ../api/index.html → https://example.com/api/index.html

    If href is empty, javascript:void(0), tel:, mailto:, skip → return None.
    """
    if not href:
        return None

    href = href.strip()

    # Skip JS links, mailto:, tel:, etc.
    if (
        href.startswith("javascript:")
        or href.startswith("mailto:")
        or href.startswith("tel:")
    ):
        return None

    # Convert relative URLs:
    return urljoin(base_url, href)


def is_same_domain(url: str, domain_root: str) -> bool:
    """
    Check whether url belongs to the same domain as domain_root.
    Example:
        url = https://example.com/path/
        domain_root = https://example.com/
        → True

        url = https://other.com/page/
        → False
    """
    parsed = urlparse(url)
    domain_parsed = urlparse(domain_root)

    return (
        parsed.scheme == domain_parsed.scheme and parsed.netloc == domain_parsed.netloc
    )


def clean_and_normalize_link(
    href: str, base_url: str, domain_root: str
) -> Optional[str]:
    """
    Full pipeline for taking an extracted <a href="..."> and producing a
    normalized, absolute, same-domain URL.

    Steps:
        1. Convert to absolute URL (using urljoin)
        2. Normalize (remove fragments, normalize path, lowercase, trailing slash)
        3. Check same domain
        4. Return clean or None

    This is what the Crawler should use before pushing URLs to the traversal frontier.
    """
    abs_url = ensure_absolute_url(base_url, href)
    if abs_url is None:
        return None

    norm = normalize_url(abs_url)

    if not is_same_domain(norm, domain_root):
        return None

    path_lower = urlparse(norm).path.lower()
    if "login" in path_lower:
        return None
    if "tag" in path_lower:
        return None

    return norm
