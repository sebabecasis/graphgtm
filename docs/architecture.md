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
- A future embedding adapter can replace the encoder without changing the result contract.

## Current limits

- The fixture is synthetic.
- The graph is undirected in this first public slice.
- The bundled concept vocabulary is deliberately small.
- Suggested entry points are analytical prompts for an operator, not autonomous outreach decisions.

