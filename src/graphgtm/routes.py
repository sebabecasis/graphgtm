"""Bounded shortest-hop routes retaining actual edge evidence and direction."""
import networkx as nx


def routes(graph, source, target, *, limit=3, max_hops=6, require_evidence=False):
    if source not in graph or target not in graph:
        raise ValueError("Source and target must exist in the supplied network")
    if not 1 <= limit <= 20 or not 0 <= max_hops <= 12:
        raise ValueError("Use limit 1..20 and max_hops 0..12")
    usable = graph.copy()
    if require_evidence:
        usable.remove_edges_from([(a, b) for a, b, d in graph.edges(data=True)
                                  if not d.get("evidence") or not d.get("source_url")])
    result = {"source": source, "target": target, "directed": graph.is_directed(),
              "ranking": "fewest hops", "routes": [], "status": "no_route"}
    try:
        for path in nx.shortest_simple_paths(usable, source, target):
            if len(path) - 1 > max_hops:
                break
            edges = [{"source": a, "target": b, **dict(graph[a][b]),
                      "evidence_status": "provided" if graph[a][b].get("evidence") and graph[a][b].get("source_url") else "missing"}
                     for a, b in zip(path, path[1:])]
            result["routes"].append({"nodes": path, "hops": len(path) - 1, "edges": edges})
            if len(result["routes"]) >= limit:
                break
    except nx.NetworkXNoPath:
        pass
    if result["routes"]:
        result["status"] = "found"
    return result
