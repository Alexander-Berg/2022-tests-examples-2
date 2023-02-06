# -*- coding: utf-8 -*-

from sandbox.projects.websearch.basesearch.TestBasesearchPerformance import TestBasesearchPerformance
from sandbox.projects.common import massif
from sandbox.projects.common.search import components as sc

Massified = massif.generate_task(sc.DefaultBasesearchParams, TestBasesearchPerformance)


class TestBasesearchMassif(Massified):
    type = 'TEST_BASESEARCH_MASSIF'

    # Average usage is less than 20 Gb
    execution_space = 20 * 1024


__Task__ = TestBasesearchMassif
