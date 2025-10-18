"""In-memory search index with TF-IDF scoring."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

_TOKEN_RE = re.compile(r"\b\w+\b", re.UNICODE)


@dataclass
class Document:
    """Indexed document representation."""

    doc_id: int
    url: str
    text: str


class SearchIndex:
    """A simple inverted index with TF-IDF scoring."""

    def __init__(self) -> None:
        self._documents: List[Document] = []
        self._inverted_index: Dict[str, Dict[int, float]] = defaultdict(dict)
        self._doc_frequencies: Counter[str] = Counter()
        self._doc_lengths: Dict[int, float] = {}

    def add_document(self, url: str, text: str) -> None:
        doc_id = len(self._documents)
        document = Document(doc_id=doc_id, url=url, text=text)
        self._documents.append(document)

        tokens = self._tokenize(text)
        if not tokens:
            self._doc_lengths[doc_id] = 1.0
            return

        term_freqs = Counter(tokens)
        max_freq = max(term_freqs.values())
        squared_sum = 0.0
        for term, freq in term_freqs.items():
            normalized_tf = 0.5 + 0.5 * (freq / max_freq)
            self._inverted_index[term][doc_id] = normalized_tf
            self._doc_frequencies[term] += 1
            squared_sum += normalized_tf ** 2

        length = math.sqrt(squared_sum)
        self._doc_lengths[doc_id] = length if length else 1.0

    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Document]]:
        tokens = self._tokenize(query)
        if not tokens:
            return []

        doc_scores: Dict[int, float] = defaultdict(float)
        num_docs = len(self._documents)

        for term in tokens:
            postings = self._inverted_index.get(term)
            if not postings:
                continue

            idf = math.log((1 + num_docs) / (1 + self._doc_frequencies[term])) + 1
            for doc_id, tf in postings.items():
                doc_scores[doc_id] += tf * idf

        if not doc_scores:
            return []

        results: List[Tuple[float, Document]] = []
        for doc_id, score in doc_scores.items():
            length = self._doc_lengths.get(doc_id, 1.0)
            normalized_score = score / length
            results.append((normalized_score, self._documents[doc_id]))

        results.sort(key=lambda item: item[0], reverse=True)
        return results[:top_k]

    def documents(self) -> Iterable[Document]:
        return list(self._documents)

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in _TOKEN_RE.findall(text)]
