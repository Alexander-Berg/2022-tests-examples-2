# -*- coding: utf-8 -*-

from sandbox.projects.websearch.middlesearch.TestMiddlesearchSingleHost import TestMiddlesearchSingleHost
from sandbox.projects.common import massif
from sandbox.projects.common.search import components as sc

Massified = massif.generate_task(
    sc.DefaultMiddlesearchParams,
    TestMiddlesearchSingleHost,
    start_timeout=sc.DEFAULT_START_TIMEOUT * 6,
    shutdown_timeout=sc.DEFAULT_START_TIMEOUT * 6,
)


class TestMiddlesearchSingleHostMassif(Massified):
    type = 'TEST_MIDDLESEARCH_SINGLE_HOST_MASSIF'


__Task__ = TestMiddlesearchSingleHostMassif
