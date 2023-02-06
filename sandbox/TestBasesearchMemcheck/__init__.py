# -*- coding: utf-8 -*-

from sandbox.projects.websearch.basesearch.TestBasesearchPerformance import TestBasesearchPerformance
from sandbox.projects.common.search import memcheck
from sandbox.projects.common.search import components as sc

Memchecked = memcheck.generate_task(
    sc.DefaultBasesearchParams,
    TestBasesearchPerformance,
)


class TestBasesearchMemcheck(Memchecked):
    """
        Запускает тест базового поиска на производительность с использованием valgrind
        в режиме memcheck (обнаружение ошибок некорректной работы с памятью).
        Строит отчёт об ошибках в формате XML.
    """
    type = 'TEST_BASESEARCH_MEMCHECK'
    # Average usage is less than 20 Gb
    execution_space = 20 * 1024


__Task__ = TestBasesearchMemcheck
