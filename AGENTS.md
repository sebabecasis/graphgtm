# Operating GraphGTM

Read README.md and docs/architecture.md. Python 3.11+ and NetworkX. Use the agent to inspect the network and explain results; no UI is required.

## Agent workflow

1. Establish the market question and whether the operator wants structure, relevant entry points or a route from a specified source to target.
2. Inspect real data provenance. JSON nodes require stable id and may include name, role, profile and evidence. Edges require source/target and may include weight, evidence, source_url and other metadata. Every endpoint must exist.
3. Set directed: true for directional relationships. Omission means undirected. Do not infer a relationship from similar biographies.
4. Analyze communities/bridges, search with the relevant question, then route to a named target if requested. Routes respect direction and keep actual edge evidence.
5. Inspect missing evidence and disconnected targets. Use --require-evidence when every step needs a quotation and source URL. A provided citation is not independent verification.
6. Present recommended people and route steps with caveats. Fewest-hop routes do not measure trust, access probability or willingness to introduce. Do not send outreach without authorization.

## Commands

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m graphgtm.cli analyze --graph examples/sample-ecosystem.json --out .demo/analysis.json
.venv/bin/python -m graphgtm.cli search --graph examples/sample-ecosystem.json --query "technical builders and go-to-market" --out .demo/search.json
.venv/bin/python -m graphgtm.cli route --graph examples/relationship-path.json --source operator --target target --require-evidence
.venv/bin/python -m unittest discover -s tests -v
```

Search supports --encoder openai, --model, --dimensions and --cache with OPENAI_API_KEY. Default demo has a small deterministic vocabulary, not a production embedding model. Cache preserves normalized model-specific vectors; the adapter converts dense coordinates into the sparse search contract.

## Interpretation and boundaries

Structural analysis uses an undirected projection, Louvain communities, PageRank, betweenness and participation. Search combines 60% semantic score, 15% PageRank, 15% betweenness, 10% participation. It uses its own default analysis resolution. Route analysis, unlike those structural measures, preserves direction.

route returns bounded shortest simple paths, edge attributes, evidence_status and found/no_route. --limit is 1–20 and --max-hops is 0–12. Missing source/target IDs are errors, not invented nodes.

Both bundled graphs are synthetic. The repo does not scrape or expand networks; the operator supplies them through authorized data sources. Report that remaining collection boundary. Preserve evidence and direction in changes. Offline tests/mock provider tests do not establish live network coverage or introduction success.
