"""Command-line interface for GraphGTM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze_graph, load_graph
from .recommend import find_entry_points
from .routes import routes
from .providers import OpenAIEncoder


class SparseOpenAIEncoder(OpenAIEncoder):
    def encode(self, text):
        return {str(i): v for i, v in enumerate(super().encode(text))}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="graphgtm")
    commands = root.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Analyze a network fixture")
    analyze.add_argument("--graph", type=Path, required=True)
    analyze.add_argument("--out", type=Path)
    analyze.add_argument("--resolution", type=float, default=1.0)

    search = commands.add_parser("search", help="Find evidence-backed GTM entry points")
    search.add_argument("--graph", type=Path, required=True)
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--out", type=Path)
    search.add_argument("--encoder", choices=["demo", "openai"], default="demo")
    search.add_argument("--model", default="text-embedding-3-small")
    search.add_argument("--dimensions", type=int, default=1536)
    search.add_argument("--cache", type=Path, default=Path(".demo/embedding-cache"))

    route = commands.add_parser("route", help="Find paths with relationship evidence")
    route.add_argument("--graph", type=Path, required=True)
    route.add_argument("--source", required=True)
    route.add_argument("--target", required=True)
    route.add_argument("--limit", type=int, default=3)
    route.add_argument("--max-hops", type=int, default=6)
    route.add_argument("--require-evidence", action="store_true")
    route.add_argument("--out", type=Path)
    return root


def _emit(payload: dict, output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
        print(output)
    else:
        print(rendered, end="")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    graph = load_graph(args.graph)
    if args.command == "analyze":
        _emit(analyze_graph(graph, resolution=args.resolution), args.out)
    elif args.command == "search":
        encoder = SparseOpenAIEncoder(args.model, args.dimensions, args.cache) if args.encoder == "openai" else None
        result = find_entry_points(graph, args.query, limit=args.limit, encoder=encoder)
        result["embedding"] = {"provider": args.encoder, "model": args.model if encoder else None}
        _emit(result, args.out)
    elif args.command == "route":
        _emit(routes(graph, args.source, args.target, limit=args.limit, max_hops=args.max_hops,
                     require_evidence=args.require_evidence), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
