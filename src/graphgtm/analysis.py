"""Deterministic structural analysis for a buyer-ecosystem graph."""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import networkx as nx


def load_graph(path: str | Path) -> nx.Graph:
    data = json.loads(Path(path).read_text())
    graph = nx.Graph()
    for node in data.get("nodes", []):
        node_id = str(node["id"])
        attrs = {key: value for key, value in node.items() if key != "id"}
        graph.add_node(node_id, **attrs)
    for edge in data.get("edges", []):
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in graph or target not in graph:
            raise ValueError(f"Edge references an unknown node: {source!r} -> {target!r}")
        graph.add_edge(source, target, weight=float(edge.get("weight", 1.0)))
    if not graph.nodes:
        raise ValueError("Graph fixture has no nodes")
    return graph


def _community_map(graph: nx.Graph, *, resolution: float, seed: int) -> dict[str, int]:
    groups = nx.community.louvain_communities(
        graph,
        weight="weight",
        resolution=resolution,
        seed=seed,
    )
    ordered = sorted((sorted(group) for group in groups), key=lambda group: (-len(group), group[0]))
    return {node_id: index for index, group in enumerate(ordered) for node_id in group}


def _participation(graph: nx.Graph, communities: dict[str, int]) -> dict[str, float]:
    result: dict[str, float] = {}
    for node_id in graph.nodes:
        counts = Counter(communities[neighbor] for neighbor in graph.neighbors(node_id))
        degree = sum(counts.values())
        result[node_id] = 0.0 if not degree else 1.0 - sum((count / degree) ** 2 for count in counts.values())
    return result


def _within_z(graph: nx.Graph, communities: dict[str, int]) -> dict[str, float]:
    within_degree = {
        node_id: sum(1 for neighbor in graph.neighbors(node_id) if communities[neighbor] == communities[node_id])
        for node_id in graph.nodes
    }
    by_community: dict[int, list[int]] = defaultdict(list)
    for node_id, value in within_degree.items():
        by_community[communities[node_id]].append(value)
    stats = {
        community: (statistics.mean(values), statistics.pstdev(values))
        for community, values in by_community.items()
    }
    output: dict[str, float] = {}
    for node_id, value in within_degree.items():
        mean, deviation = stats[communities[node_id]]
        output[node_id] = 0.0 if deviation == 0 else (value - mean) / deviation
    return output


def _role(within_z: float, participation: float) -> str:
    if within_z >= 2.5:
        if participation < 0.30:
            return "community hub"
        if participation < 0.75:
            return "connector hub"
        return "network hub"
    if participation < 0.05:
        return "specialist"
    if participation < 0.45:
        return "community member"
    if participation < 0.80:
        return "connector"
    return "network connector"


def _pagerank(
    graph: nx.Graph,
    *,
    alpha: float = 0.85,
    tolerance: float = 1.0e-12,
    max_iterations: int = 200,
) -> dict[str, float]:
    """Small weighted PageRank implementation without SciPy.

    NetworkX 3.6 delegates its public PageRank function to SciPy. Keeping this
    iteration here avoids adding a large numerical dependency for a tiny graph
    analysis package.
    """
    nodes = list(graph.nodes)
    count = len(nodes)
    rank = {node_id: 1.0 / count for node_id in nodes}
    strength = {
        node_id: sum(float(graph[node_id][neighbor].get("weight", 1.0)) for neighbor in graph.neighbors(node_id))
        for node_id in nodes
    }
    base = (1.0 - alpha) / count

    for _ in range(max_iterations):
        updated = {node_id: base for node_id in nodes}
        for node_id in nodes:
            if strength[node_id] == 0:
                share = alpha * rank[node_id] / count
                for target in nodes:
                    updated[target] += share
                continue
            for neighbor in graph.neighbors(node_id):
                weight = float(graph[node_id][neighbor].get("weight", 1.0))
                updated[neighbor] += alpha * rank[node_id] * weight / strength[node_id]
        if sum(abs(updated[node_id] - rank[node_id]) for node_id in nodes) < tolerance:
            return updated
        rank = updated
    raise RuntimeError("PageRank did not converge")


def analyze_graph(graph: nx.Graph, *, resolution: float = 1.0, seed: int = 42) -> dict[str, Any]:
    communities = _community_map(graph, resolution=resolution, seed=seed)
    pagerank = _pagerank(graph)
    betweenness = nx.betweenness_centrality(graph, normalized=True, weight=None)
    participation = _participation(graph, communities)
    within_z = _within_z(graph, communities)

    nodes: dict[str, dict[str, Any]] = {}
    for node_id, attrs in graph.nodes(data=True):
        nodes[node_id] = {
            "id": node_id,
            "name": attrs.get("name", node_id),
            "role": attrs.get("role", ""),
            "community": communities[node_id],
            "degree": graph.degree(node_id),
            "pagerank": pagerank[node_id],
            "betweenness": betweenness[node_id],
            "participation": participation[node_id],
            "within_z": within_z[node_id],
            "network_role": _role(within_z[node_id], participation[node_id]),
        }

    community_rows = []
    for community_id in sorted(set(communities.values())):
        members = [node_id for node_id, value in communities.items() if value == community_id]
        ranked = sorted(members, key=lambda node_id: (-pagerank[node_id], node_id))
        community_rows.append(
            {
                "id": community_id,
                "size": len(members),
                "members": sorted(members),
                "anchors": ranked[:3],
            }
        )

    return {
        "summary": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "communities": len(community_rows),
        },
        "nodes": nodes,
        "communities": community_rows,
    }
