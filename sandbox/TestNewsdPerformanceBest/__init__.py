# -*- coding: utf-8 -*-

from sandbox.projects.TestNewsdPerformance import TestNewsdPerformance, PlanParameter, ApphostMode

from sandbox.projects.common import dolbilka
from sandbox.projects.common.TestPerformanceBest import BaseTestPerformanceBestTask
from sandbox.projects.common.news.newsd import create_newsd_params


# was forked from projects.websearch.basesearch.projects.websearch.basesearch.TestBasesearchPerformanceBest
class TestNewsdPerformanceBest(BaseTestPerformanceBestTask):
    """
        Параллельный запуск тестирования базового с последующей агрегацией результатов.
        Запускается указанное количество подзадач типа TEST_NEWSD_PERFORMANCE (параметр number_of_runs)

        Выбирается лучший обстрел.
    """

    type = 'TEST_NEWSD_PERFORMANCE_BEST'
    execution_space = 5 * 1024  # 5 Gb
    cores = 1

    newsd_params = create_newsd_params()

    input_parameters = (
        BaseTestPerformanceBestTask.input_parameters +
        newsd_params.params +
        (
            PlanParameter,
            ApphostMode,
        ) +
        dolbilka.DolbilkaExecutor.input_task_parameters
    )

    def _get_performance_task_type(self):
        return (
            TestNewsdPerformance.type
        )


__Task__ = TestNewsdPerformanceBest
