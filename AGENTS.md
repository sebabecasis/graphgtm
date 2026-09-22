# Operating GraphGTM

Read `README.md` and `docs/architecture.md`. This repository analyzes a supplied undirected network and ranks relevant entry points. The bundled graph is synthetic. It does not scrape a network, expand it automatically or calculate an introduction path between a source and target.

## Agent workflow

1. Establish the market question and whether the operator wants structural analysis, relevant people, or an actual route to a named target. Explain the route gap before promising the latter.
2. Inspect the supplied graph: `nodes` have stable `id` plus optional `name`, `role`, `profile`, and an `evidence` list; `edges` have `source`, `target` and optional `weight`. Every edge endpoint must exist. Record where real relationship data came from outside this minimal schema; do not infer relationships from similar biographies.
3. Run analysis, then search using the operator's question. Explain communities, bridges and entry points with the retained evidence and relevant structural measures.
4. Review the suggested people and data coverage. A graph connection does not imply willingness to introduce someone, and an undirected edge does not establish the direction of a real relationship.
5. Deliver analysis and search artifacts, evidence for recommendations, and any missing data or capabilities. Keep synthetic examples explicitly labeled.

## Commands

Python 3.11+ and NetworkX are required. Use an isolated environment:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m graphgtm.cli analyze --graph examples/sample-ecosystem.json --out .demo/analysis.json
.venv/bin/python -m graphgtm.cli search --graph examples/sample-ecosystem.json --query "networks connecting technical builders to go-to-market" --out .demo/entry-points.json
.venv/bin/python -m unittest discover -s tests -v
```

Analysis returns node measures and communities with anchors. Communities use Louvain, not Leiden. Search returns evidence and explanations; the score combines 60% semantic match, 15% normalized PageRank, 15% normalized betweenness and 10% participation. This is a heuristic, not an estimated chance of access. Search uses default analysis settings independently of a previous `analyze --resolution` run.

## Development and limits

`analysis.py` handles structure, `search.py` evidence matching, and `recommend.py` ranking. `ConceptEncoder` is a small deterministic vocabulary adapter; production embeddings are not connected. Its encoder protocol returns sparse dictionaries, so a dense-vector provider requires a compatible adapter or an explicit interface change.

The website's ambition to “plot a path” needs a source/target route function, an explanation of each edge, and handling for disconnected targets. Collection, graph expansion, directed relationship semantics and production embeddings are also future work. Agent instructions should not pretend these functions exist. Propose the appropriate code change when requested work reaches these boundaries; preserve source evidence and verify the existing tests after changes.
