# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.datastructures import DirectedGraph
from passport.backend.social.common.test.test_case import TestCase


class TestDirectedGraph(TestCase):
    def setUp(self):
        super(TestDirectedGraph, self).setUp()
        self._g = DirectedGraph()

    def _assert_traverse_bfs_equal(self, expected_values_and_paths=None, **kwargs):
        expected_values_and_paths = expected_values_and_paths or []
        actual_values_and_paths = []
        for node, path in self._g.traverse_bfs(**kwargs):
            value = node.value
            path = [e.src.value for e in path]
            actual_values_and_paths.append((value, path))
        self.assertEqual(actual_values_and_paths, expected_values_and_paths)

    def test_add_node(self):
        value = 1
        node = self._g.add_node(value)
        self.assertIn(node, self._g._nodes)
        self.assertIs(node.value, value)

    def test_nodes_with_equal_value(self):
        value = 1
        node1 = self._g.add_node(value)
        node2 = self._g.add_node(value)
        self.assertNotEqual(node1, node2)
        self.assertIs(node1.value, node2.value)

    def test_has_node(self):
        node = self._g.add_node(1)
        self.assertTrue(self._g.has_node(node))

    def test_not_have_node(self):
        h = DirectedGraph()
        node = h.add_node(1)
        self.assertFalse(self._g.has_node(node))

    def test_add_edge(self):
        node1 = self._g.add_node(1)
        node2 = self._g.add_node(2)
        value = 3
        edge = self._g.add_edge(src=node1, dst=node2, value=value)

        self.assertIs(edge.src, node1)
        self.assertIs(edge.dst, node2)
        self.assertIs(edge.value, value)

        self.assertEqual(len(node1.out_edges), 1)
        self.assertIs(node1.out_edges[0], edge)
        self.assertEqual(len(node1.in_edges), 0)

        self.assertEqual(len(node2.in_edges), 1)
        self.assertIs(node2.in_edges[0], edge)
        self.assertEqual(len(node1.in_edges), 0)

    def test_remove_isolated_node(self):
        node = self._g.add_node(1)
        self._g.remove_node(node)
        self.assertFalse(self._g.has_node(node))

    def test_remove_linked_node(self):
        node1 = self._g.add_node(1)
        node2 = self._g.add_node(2)
        node3 = self._g.add_node(3)
        self._g.add_edge(src=node1, dst=node2)
        edge = self._g.add_edge(src=node2, dst=node3)
        self._g.add_edge(src=node3, dst=node1)

        self._g.remove_node(node1)

        self.assertFalse(self._g.has_node(node1))
        self.assertTrue(self._g.has_node(node2))
        self.assertEqual(node2.in_edges, [])
        self.assertEqual(node2.out_edges, [edge])
        self.assertTrue(self._g.has_node(node3))
        self.assertEqual(node3.in_edges, [edge])
        self.assertEqual(node3.out_edges, [])

    def test_remove_not_existent_node(self):
        h = DirectedGraph()
        node = h.add_node(1)
        self._g.remove_node(node)

    def test_traverse_isolated(self):
        start = self._g.add_node(1)
        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[(1, [])],
        )

    def test_traverse_direct_cycle(self):
        start = self._g.add_node(1)
        self._g.add_edge(src=start, dst=start)
        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[(1, [])],
        )

    def test_traverse_one_edge(self):
        start = self._g.add_node(1)
        self._g.add_edge(src=start, dst=self._g.add_node(2))

        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[
                (1, []),
                (2, [1]),
            ],
        )

    def test_traverse_two_edges(self):
        start = self._g.add_node(1)
        node = self._g.add_node(2)
        self._g.add_edge(src=start, dst=node)
        self._g.add_edge(src=node, dst=self._g.add_node(3))

        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[
                (1, []),
                (2, [1]),
                (3, [1, 2]),
            ],
        )

    def test_traverse_indirect_cycle(self):
        start = self._g.add_node(1)
        end = self._g.add_node(2)
        self._g.add_edge(src=start, dst=end)
        self._g.add_edge(src=end, dst=start)

        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[
                (1, []),
                (2, [1]),
            ],
        )

    def test_traverse_fork(self):
        start = self._g.add_node(1)
        node1 = self._g.add_node(2)
        node2 = self._g.add_node(3)
        self._g.add_edge(src=start, dst=node1)
        self._g.add_edge(src=start, dst=node2)

        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[
                (1, []),
                (2, [1]),
                (3, [1]),
            ],
        )

    def test_traverse_many_paths_to_node(self):
        start = self._g.add_node(1)
        node1 = self._g.add_node(2)
        node2 = self._g.add_node(3)
        end = self._g.add_node(4)
        self._g.add_edge(src=start, dst=node1)
        self._g.add_edge(src=start, dst=node2)
        self._g.add_edge(src=node1, dst=end)
        self._g.add_edge(src=node2, dst=end)

        self._assert_traverse_bfs_equal(
            start=start,
            expected_values_and_paths=[
                (1, []),
                (2, [1]),
                (3, [1]),
                (4, [1, 2]),
            ],
        )

    def test_traverse_edge_key(self):
        start = self._g.add_node(0)
        node1 = self._g.add_node(1)
        node2 = self._g.add_node(2)
        node3 = self._g.add_node(3)
        self._g.add_edge(src=start, dst=node1, value=2)
        self._g.add_edge(src=start, dst=node2, value=3)
        self._g.add_edge(src=start, dst=node3, value=1)

        self._assert_traverse_bfs_equal(
            start=start,
            edge_key=lambda e: e.value,
            expected_values_and_paths=[
                (0, []),
                (3, [0]),
                (1, [0]),
                (2, [0]),
            ],
        )

        self._assert_traverse_bfs_equal(
            start=start,
            edge_key=lambda e: -e.value,
            expected_values_and_paths=[
                (0, []),
                (2, [0]),
                (1, [0]),
                (3, [0]),
            ],
        )
