# GraphGTM

Map a buyer ecosystem, identify its communities and important nodes, then use semantic search to find relevant people and evidence within it.

## Repository status

The first analytical slice is implemented using a safe synthetic network.

The first working slice will demonstrate:

```text
seed network
→ graph expansion
→ communities and bridge nodes
→ semantic search
→ relevant profiles and evidence
→ suggested GTM entry points
```

## Run the example

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

graphgtm analyze \
  --graph examples/sample-ecosystem.json \
  --out .demo/analysis.json

graphgtm search \
  --graph examples/sample-ecosystem.json \
  --query "networks connecting technical builders to go-to-market" \
  --out .demo/entry-points.json
```

Every search result retains the profile or evidence passage that caused the match. The entry-point ranking combines that relevance with PageRank, betweenness and cross-community participation.

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

See [`docs/architecture.md`](docs/architecture.md) for the analytical boundaries and current limits.

