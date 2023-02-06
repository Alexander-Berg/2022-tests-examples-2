#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest


class TestSimUtils(unittest.TestCase):
    def setUp(self):
        import utils.sim_utils as sim_utils

        self.paths = {'/path/username/create', '/path/root/create', '/path/asdaasdsdfdfgdfgdfglkfghlkfgh/create',
                      '/a/b/c', '/'}
        self.path = {'/a/b/c'}
        self.sim_utils = sim_utils

    def test_jaccard_index(self):
        set_1 = set('/spectre/abcxczmv/new'.split('/'))
        set_2 = set('/spectre/qwerty/new'.split('/'))
        index = self.sim_utils.jaccard_index(set_1, set_2)
        self.assertEqual(index, 0.6)

    def test_path_sim_metric(self):
        metric = self.sim_utils.path_sim_metric(list(self.paths))
        self.assertEqual(metric, {'/path/asdaasdsdfdfgdfgdfglkfghlkfgh/create': [1.0, 0.6, 0.6, 0.25,
                                                                                 0.14285714285714285],
                                  '/a/b/c': [0.14285714285714285, 0.14285714285714285, 0.14285714285714285, 0.25, 1.0],
                                  '/path/username/create': [0.6, 1.0, 0.6, 0.25, 0.14285714285714285],
                                  '/': [0.25, 0.25, 0.25, 1.0, 0.25],
                                  '/path/root/create': [0.6, 0.6, 1.0, 0.25, 0.14285714285714285]})

    def test_filter_similar_paths(self):
        filtered = self.sim_utils.filter_similar_paths(self.paths)
        self.assertEqual(filtered, {'/', '/a/b/c', '/path/asdaasdsdfdfgdfgdfglkfghlkfgh/create'})
        filtered = self.sim_utils.filter_similar_paths(self.path)
        self.assertEqual(filtered, {'/a/b/c'})
