import unittest
import networkx as nx
from graphgtm.routes import routes
from graphgtm.cli import SparseOpenAIEncoder
from unittest.mock import patch


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.graph = nx.DiGraph()
        self.graph.add_edge("a", "b", evidence="A follows B", source_url="https://example.test/a")
        self.graph.add_edge("b", "c", evidence="B follows C", source_url="https://example.test/b")
        self.graph.add_node("isolated")

    def test_directed_paths_preserve_evidence(self):
        result = routes(self.graph, "a", "c", require_evidence=True)
        self.assertEqual(["a", "b", "c"], result["routes"][0]["nodes"])
        self.assertEqual("provided", result["routes"][0]["edges"][0]["evidence_status"])
        self.assertEqual("no_route", routes(self.graph, "c", "a")["status"])

    def test_disconnected_and_bounded_paths(self):
        self.assertEqual("no_route", routes(self.graph, "a", "isolated")["status"])
        self.assertEqual("no_route", routes(self.graph, "a", "c", max_hops=1)["status"])
        self.assertEqual(0, routes(self.graph, "a", "a")["routes"][0]["hops"])
        with self.assertRaises(ValueError):
            routes(self.graph, "missing", "a")

    def test_unverified_edges_are_not_invented(self):
        self.graph.add_edge("a", "c")
        self.assertEqual("missing", routes(self.graph, "a", "c")["routes"][0]["edges"][0]["evidence_status"])
        self.assertEqual(2, routes(self.graph, "a", "c", require_evidence=True)["routes"][0]["hops"])

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
    def test_dense_provider_fits_sparse_search_contract(self):
        encoder = SparseOpenAIEncoder(dimensions=2, transport=lambda *a, **k: {"data": [{"embedding": [3, 4]}]})
        self.assertEqual({"0": 0.6, "1": 0.8}, encoder.encode("text"))
