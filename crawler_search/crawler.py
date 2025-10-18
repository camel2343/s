"""Web crawler implementation for building a small search index."""

from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


_LINK_RE = re.compile(r"^https?://", re.IGNORECASE)


@dataclass
class Page:
    """Representation of a crawled page."""

    url: str
    text: str
    links: List[str] = field(default_factory=list)


class Crawler:
    """A polite breadth-first crawler with optional domain restrictions."""

    def __init__(
        self,
        user_agent: str = "SimpleCrawler/1.0",
        delay: float = 1.0,
        timeout: float = 10.0,
    ) -> None:
        self.user_agent = user_agent
        self.delay = delay
        self.timeout = timeout

    def crawl(
        self,
        start_urls: Iterable[str],
        max_pages: int = 50,
        allowed_domains: Optional[Iterable[str]] = None,
    ) -> List[Page]:
        """Crawl pages starting from ``start_urls`` up to ``max_pages``.

        Parameters
        ----------
        start_urls:
            Seed URLs for the crawl.
        max_pages:
            Maximum number of pages to visit.
        allowed_domains:
            Optional collection of domains to restrict the crawl to.
        """

        normalized_domains: Optional[Set[str]] = (
            {self._normalize_domain(d) for d in allowed_domains}
            if allowed_domains
            else None
        )

        queue: Deque[str] = deque()
        visited: Set[str] = set()
        results: List[Page] = []

        for url in start_urls:
            normalized = self._normalize_url(url)
            if normalized and normalized not in visited:
                queue.append(normalized)

        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})

        while queue and len(results) < max_pages:
            current_url = queue.popleft()
            if current_url in visited:
                continue

            if normalized_domains and not self._url_allowed(current_url, normalized_domains):
                visited.add(current_url)
                continue

            try:
                response = session.get(current_url, timeout=self.timeout)
                response.raise_for_status()
            except requests.RequestException:
                visited.add(current_url)
                continue

            visited.add(current_url)
            text, links = self._extract_content(current_url, response.text)
            results.append(Page(url=current_url, text=text, links=links))

            for link in links:
                normalized_link = self._normalize_url(link)
                if (
                    normalized_link
                    and normalized_link not in visited
                    and normalized_link not in queue
                    and (not normalized_domains or self._url_allowed(normalized_link, normalized_domains))
                ):
                    queue.append(normalized_link)

            if queue and self.delay:
                time.sleep(self.delay)

        return results

    def _normalize_url(self, url: str) -> Optional[str]:
        url = url.strip()
        if not url:
            return None

        if not _LINK_RE.match(url):
            return None

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None

        normalized = parsed._replace(fragment="", query="").geturl()
        return normalized

    def _normalize_domain(self, domain: str) -> str:
        parsed = urlparse(f"http://{domain}")
        return parsed.netloc.lower()

    def _url_allowed(self, url: str, allowed_domains: Set[str]) -> bool:
        netloc = urlparse(url).netloc.lower()
        return any(netloc == domain or netloc.endswith(f".{domain}") for domain in allowed_domains)

    def _extract_content(self, base_url: str, html: str) -> Tuple[str, List[str]]:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = " ".join(soup.stripped_strings)
        links = []
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            absolute = urljoin(base_url, href)
            links.append(absolute)
        return text, links
