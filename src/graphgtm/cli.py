"""Command-line interface for GraphGTM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze_graph, load_graph
from .recommend import find_entry_points


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
        _emit(find_entry_points(graph, args.query, limit=args.limit), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

