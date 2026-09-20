"""Evidence-preserving profile search with a replaceable encoder boundary."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol

import networkx as nx


TOKEN = re.compile(r"[a-z0-9]+")


class Encoder(Protocol):
    def encode(self, text: str) -> dict[str, float]: ...


class ConceptEncoder:
    """Small deterministic encoder for the bundled demonstration.

    It canonicalises a deliberately limited vocabulary so related GTM language
    can match without a network call. Replace this with a real embedding adapter
    for production use; the search and evidence contracts remain unchanged.
    """

    ALIASES = {
        "agents": "agent",
        "agentic": "agent",
        "ai": "agent",
        "developers": "builder",
        "developer": "builder",
        "engineers": "builder",
        "engineering": "builder",
        "tooling": "infrastructure",
        "tools": "infrastructure",
        "platform": "infrastructure",
        "platforms": "infrastructure",
        "sales": "gtm",
        "revenue": "gtm",
        "outbound": "gtm",
        "marketing": "gtm",
        "ecosystem": "network",
        "community": "network",
        "communities": "network",
        "automation": "workflow",
        "workflows": "workflow",
        "operations": "ops",
        "operational": "ops",
        "analytics": "measurement",
        "metrics": "measurement",
    }

    STOP = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"}

    def encode(self, text: str) -> dict[str, float]:
        tokens = []
        for token in TOKEN.findall(text.casefold()):
            if token in self.STOP:
                continue
            tokens.append(self.ALIASES.get(token, token))
        counts = Counter(tokens)
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {token: value / norm for token, value in counts.items()}


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(key, 0.0) for key, value in left.items())


def search_profiles(
    graph: nx.Graph,
    query: str,
    *,
    encoder: Encoder | None = None,
    limit: int = 10,
) -> list[dict]:
    active_encoder = encoder or ConceptEncoder()
    query_vector = active_encoder.encode(query)
    hits = []
    for node_id, attrs in graph.nodes(data=True):
        chunks = [str(attrs.get("profile", "")), *[str(item) for item in attrs.get("evidence", [])]]
        scored = [(cosine(query_vector, active_encoder.encode(chunk)), chunk) for chunk in chunks if chunk]
        if not scored:
            continue
        score, evidence = max(scored, key=lambda row: row[0])
        if score <= 0:
            continue
        hits.append(
            {
                "id": node_id,
                "name": attrs.get("name", node_id),
                "role": attrs.get("role", ""),
                "semantic_score": score,
                "evidence": evidence,
            }
        )
    hits.sort(key=lambda hit: (-hit["semantic_score"], hit["id"]))
    return hits[:limit]

