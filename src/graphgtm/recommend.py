"""Combine semantic relevance and graph structure into explainable entry points."""

from __future__ import annotations

from typing import Any

import networkx as nx

from .analysis import analyze_graph
from .search import Encoder, search_profiles


def _normalise(values: dict[str, float]) -> dict[str, float]:
    maximum = max(values.values(), default=0.0)
    return {key: (value / maximum if maximum else 0.0) for key, value in values.items()}


def find_entry_points(
    graph: nx.Graph,
    query: str,
    *,
    encoder: Encoder | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    analysis = analyze_graph(graph)
    semantic_hits = search_profiles(graph, query, encoder=encoder, limit=max(limit * 3, limit))
    pagerank = _normalise({node_id: row["pagerank"] for node_id, row in analysis["nodes"].items()})
    betweenness = _normalise({node_id: row["betweenness"] for node_id, row in analysis["nodes"].items()})

    results = []
    for hit in semantic_hits:
        structural = analysis["nodes"][hit["id"]]
        score = (
            0.60 * hit["semantic_score"]
            + 0.15 * pagerank[hit["id"]]
            + 0.15 * betweenness[hit["id"]]
            + 0.10 * structural["participation"]
        )
        reasons = [f"semantic match {hit['semantic_score']:.2f}"]
        if structural["participation"] >= 0.45:
            reasons.append("connects multiple communities")
        if pagerank[hit["id"]] >= 0.75:
            reasons.append("structurally prominent")
        reasons.append(f"network role: {structural['network_role']}")
        results.append(
            {
                **hit,
                "community": structural["community"],
                "network_role": structural["network_role"],
                "pagerank": structural["pagerank"],
                "betweenness": structural["betweenness"],
                "participation": structural["participation"],
                "entry_score": score,
                "why": reasons,
            }
        )
    results.sort(key=lambda row: (-row["entry_score"], row["id"]))
    return {
        "query": query,
        "graph_summary": analysis["summary"],
        "entry_points": results[:limit],
    }

