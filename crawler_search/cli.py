"""Command line interface for the crawler-based search engine."""

from __future__ import annotations

import argparse
import json
from typing import List, Optional

from .crawler import Crawler
from .index import SearchIndex


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl websites and search their content.")
    parser.add_argument("start_urls", nargs="+", help="Seed URLs to crawl.")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum number of pages to crawl.")
    parser.add_argument(
        "--allowed-domains",
        nargs="*",
        default=None,
        help="Restrict crawling to the given domains (space separated).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds to avoid overloading servers.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start an interactive prompt to issue multiple search queries.",
    )
    parser.add_argument(
        "--query",
        help="Execute a single search query after crawling (ignored when --interactive is set).",
    )
    parser.add_argument(
        "--export",
        metavar="PATH",
        help="Optional path to export the index metadata as JSON.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    crawler = Crawler(delay=args.delay, timeout=args.timeout)
    pages = crawler.crawl(args.start_urls, max_pages=args.max_pages, allowed_domains=args.allowed_domains)

    if not pages:
        print("No pages crawled. Check your start URLs or connectivity.")
        return 1

    index = SearchIndex()
    for page in pages:
        index.add_document(page.url, page.text)

    if args.export:
        export_index(args.export, index)

    if args.interactive:
        interactive_search(index)
        return 0

    if args.query:
        run_query(index, args.query)
        return 0

    print("Crawled {count} pages. Use --query to search or --interactive for REPL.".format(count=len(pages)))
    return 0


def interactive_search(index: SearchIndex) -> None:
    print("Enter search queries (type 'exit' to quit).")
    while True:
        try:
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query.lower() in {"exit", "quit"}:
            break

        if not query:
            continue

        run_query(index, query)


def run_query(index: SearchIndex, query: str) -> None:
    results = index.search(query)
    if not results:
        print("No results found.")
        return

    for score, document in results:
        print(f"[{score:.3f}] {document.url}")


def export_index(path: str, index: SearchIndex) -> None:
    data = {
        "documents": [
            {
                "doc_id": doc.doc_id,
                "url": doc.url,
                "text_preview": doc.text[:200],
            }
            for doc in index.documents()
        ]
    }
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
