# Architecture

GraphGTM has three separable layers:

```text
network fixture
    │
    ├── structural analysis
    │     ├── PageRank
    │     ├── betweenness
    │     ├── Louvain communities
    │     └── participation / network role
    │
profile and content evidence
    │
    └── replaceable encoder → evidence-preserving search
                                │
                                ▼
              semantic relevance + graph structure
                                │
                                ▼
                  explainable GTM entry points
```

## Boundaries

- `analysis.py` knows only about the graph.
- `search.py` searches profile and evidence chunks and retains the winning text.
- `recommend.py` combines relevance with structural position; it does not invent evidence.
- `ConceptEncoder` makes the bundled fixture runnable without model downloads. It is a demonstration adapter, not a substitute for production embeddings.
- providers.OpenAIEncoder plus the sparse adapter in cli.py enables --encoder openai with model-specific normalized cache files.

## Current limits

- The fixture is synthetic.
- JSON directed: true creates a directed graph and preserves edge evidence/metadata. Structural analysis uses its undirected projection; routes preserve direction.
- The bundled concept vocabulary is deliberately small; real OpenAI vectors are optional.
- Suggested entry points are analytical prompts for an operator, not autonomous outreach decisions.
- routes.py returns bounded shortest-hop paths with edge evidence and explicit no_route handling. --require-evidence excludes uncited relationships. Hops are not a trust/access probability.
- Source-network collection and automatic expansion are not implemented.
