# -*- coding: utf-8 -*-
from sandbox.projects.common.search.BaseTestSuperMindTask import BaseTestSuperMindTask
from sandbox.projects.websearch.basesearch.TestBasesearchPerformanceBest import TestBasesearchPerformanceBest


class TestSuperMind(BaseTestSuperMindTask):

    """
        Проверяет, что ручка Supermind управления производительностью базового поиска работает
        и поворот ручки в нужную сторону приводит к увеличению RPS (качество при этом проседает,
        но это в данном случае не так важно).

        В режиме mind задаётся значение множителя и вычисляется разница между RPS в процентах
        между двумя запусками TEST_BASESEARCH_PERFORMANCE_BEST.

        В режиме auto тестируется автоматическая деградация при повышении нагрузки.

        Сделано в рамках SEARCH-628
    """

    type = 'TEST_SUPERMIND'

    input_parameters = (
        BaseTestSuperMindTask.input_parameters +
        TestBasesearchPerformanceBest.input_parameters
    )

    def _get_performance_task_type(self):
        return TestBasesearchPerformanceBest.type


__Task__ = TestSuperMind
