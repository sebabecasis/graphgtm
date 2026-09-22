# GraphGTM

For agent-assisted operation, start with [AGENTS.md](AGENTS.md). Claude Code loads the same guide through [CLAUDE.md](CLAUDE.md).

Map a buyer ecosystem, identify its communities and important nodes, then use semantic search to find relevant people and evidence within it.

## Repository status

Structural analysis, evidence-preserving search and directed source-to-target routes are implemented with synthetic examples. Search supports --encoder openai with OPENAI_API_KEY; demo remains the credential-free default.

The implemented workflow is:

```text
supplied network
→ validate nodes and relationships
→ communities and bridge nodes
→ semantic search
→ relevant profiles and evidence
→ suggested GTM entry points
→ evidence-backed source/target routes
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
