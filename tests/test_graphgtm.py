from __future__ import annotations

import unittest
from pathlib import Path

from graphgtm import analyze_graph, find_entry_points, load_graph, search_profiles


FIXTURE = Path(__file__).parents[1] / "examples" / "sample-ecosystem.json"


class GraphGTMTest(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = load_graph(FIXTURE)

    def test_fixture_has_two_detected_communities(self) -> None:
        analysis = analyze_graph(self.graph)
        self.assertEqual(7, analysis["summary"]["nodes"])
        self.assertEqual(10, analysis["summary"]["edges"])
        self.assertEqual(2, analysis["summary"]["communities"])

    def test_bridge_has_cross_community_participation(self) -> None:
        analysis = analyze_graph(self.graph)
        bridge = analysis["nodes"]["morgan"]
        specialists = [analysis["nodes"][node_id]["participation"] for node_id in ("ada", "farah")]
        self.assertGreater(bridge["participation"], max(specialists))
        self.assertGreater(bridge["betweenness"], 0)
        self.assertEqual("connector", bridge["network_role"])

    def test_concept_search_returns_evidence(self) -> None:
        hits = search_profiles(self.graph, "AI agent tooling for developers", limit=3)
        ids = [hit["id"] for hit in hits]
        self.assertIn("ada", ids)
        self.assertIn("ben", ids)
        self.assertTrue(all(hit["evidence"] for hit in hits))

    def test_entry_points_combine_relevance_and_structure(self) -> None:
        result = find_entry_points(self.graph, "networks connecting technical builders to go-to-market", limit=3)
        self.assertEqual("morgan", result["entry_points"][0]["id"])
        self.assertIn("connects multiple communities", result["entry_points"][0]["why"])

    def test_analysis_is_deterministic(self) -> None:
        first = analyze_graph(self.graph)
        second = analyze_graph(self.graph)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
